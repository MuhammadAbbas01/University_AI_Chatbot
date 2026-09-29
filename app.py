"""
University of Malakand AI Assistant

Flask application serving a RAG-based assistant over official university PDFs.

Features:
- Word-by-word streaming responses
- HTML-formatted answers with source citations
- Voice input (speech-to-text) and voice output (text-to-speech)
- Analytics tracking
- Password-protected admin panel (PDF upload, re-indexing, stats)
"""

from flask import Flask, render_template, request, jsonify, session, Response, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import config
from rag_engine import initialize_rag, get_rag_system
from voice_processor import get_voice_processor
import json
import os
import time
import re

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG_MODE
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = config.PDF_FOLDER

# Analytics
chat_histories = {}
analytics_data = {
    "total_questions": 0,
    "popular_questions": {},
    "users_count": 0,
    "total_pdfs": 0,
    "avg_response_time": 0,
    "start_time": datetime.now().isoformat()
}

ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def format_answer_to_html(answer):
    """
    Convert the model's markdown-style answer into HTML
    (headings, bullet lists, numbered lists and paragraphs).
    """
    if not answer:
        return ""

    # Split into paragraphs
    paragraphs = answer.split('\n\n')
    formatted_parts = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # **Bold Heading**
        if para.startswith('**') and para.endswith('**'):
            heading = para.replace('**', '').strip()
            formatted_parts.append(
                f'<h3 style="color: #1e40af; font-weight: 700; margin: 24px 0 16px 0; '
                f'font-size: 20px; border-left: 4px solid #3b82f6; padding-left: 12px;">'
                f'{heading}</h3>'
            )

        # Bullet list with •
        elif '•' in para or para.strip().startswith('- '):
            items = para.split('\n')
            list_html = '<ul style="margin: 16px 0; padding-left: 28px; line-height: 2;">'
            for item in items:
                item = item.strip()
                if item:
                    item = item.lstrip('•-').strip()
                    # Bold parts within list items
                    item = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #1e40af;">\1</strong>', item)
                    list_html += f'<li style="margin: 10px 0; color: #334155;">{item}</li>'
            list_html += '</ul>'
            formatted_parts.append(list_html)

        # Numbered list
        elif para and para[0].isdigit() and ('. ' in para[:5] or ') ' in para[:5]):
            items = para.split('\n')
            list_html = '<ol style="margin: 16px 0; padding-left: 28px; line-height: 2;">'
            for item in items:
                item = item.strip()
                if item and (item[0].isdigit() if item else False):
                    item = re.sub(r'^\d+[\.)]\s*', '', item)
                    # Bold parts within list items
                    item = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #1e40af;">\1</strong>', item)
                    list_html += f'<li style="margin: 10px 0; color: #334155;">{item}</li>'
            list_html += '</ol>'
            formatted_parts.append(list_html)

        # Regular paragraph
        else:
            # Bold inline text
            para = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #1e40af; font-weight: 600;">\1</strong>', para)
            formatted_parts.append(
                f'<p style="margin: 14px 0; line-height: 1.8; color: #1e293b; font-size: 15px;">{para}</p>'
            )

    return ''.join(formatted_parts)

def load_analytics():
    global analytics_data
    if os.path.exists(config.ANALYTICS_FILE):
        try:
            with open(config.ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                analytics_data = json.load(f)
        except:
            pass

def save_analytics():
    if config.ENABLE_ANALYTICS:
        try:
            with open(config.ANALYTICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(analytics_data, f, indent=2)
        except:
            pass

def log_question(question, response_time=0):
    if config.ENABLE_ANALYTICS:
        analytics_data["total_questions"] += 1

        if response_time > 0:
            current_avg = analytics_data.get("avg_response_time", 0)
            total_q = analytics_data["total_questions"]
            analytics_data["avg_response_time"] = ((current_avg * (total_q - 1)) + response_time) / total_q

        q_lower = question.lower()[:100]
        if q_lower in analytics_data["popular_questions"]:
            analytics_data["popular_questions"][q_lower] += 1
        else:
            analytics_data["popular_questions"][q_lower] = 1

        save_analytics()

@app.route('/')
def home():
    """Main page"""
    if 'user_id' not in session:
        session['user_id'] = f"user_{datetime.now().timestamp()}"
        analytics_data["users_count"] += 1
        save_analytics()

    pdf_count = 0
    if os.path.exists(config.PDF_FOLDER):
        pdf_count = len([f for f in os.listdir(config.PDF_FOLDER)
                        if f.endswith('.pdf') and not f.startswith('._')])
    analytics_data["total_pdfs"] = pdf_count

    return render_template('index.html',
                         app_name=config.APP_NAME,
                         university=config.UNIVERSITY_NAME,
                         tagline=config.UNIVERSITY_TAGLINE,
                         location=config.UNIVERSITY_LOCATION,
                         stats=config.UNIVERSITY_STATS,
                         total_questions=analytics_data.get("total_questions", 0),
                         total_pdfs=pdf_count,
                         resources=config.UNIVERSITY_RESOURCES)

@app.route('/ask_stream', methods=['POST'])
def ask_stream():
    """
    Answer a question and stream the response to the browser word by word
    using server-sent events.
    """

    try:
        data = json.loads(request.data)
        question = data.get('question', '').strip()
    except:
        question = ""

    def generate():
        try:
            if not question:
                yield f"data: {json.dumps({'error': 'Please enter a question'})}\n\n"
                return

            start_time = time.time()
            rag = get_rag_system()

            if not rag:
                yield f"data: {json.dumps({'error': 'System initializing... Please wait.'})}\n\n"
                return

            # Get the answer from the RAG engine
            result = rag.get_answer(question)
            response_time = time.time() - start_time

            log_question(question, response_time)

            # Format to beautiful HTML
            formatted_answer = format_answer_to_html(result["answer"])
            sources = result["sources"]

            if formatted_answer:
                # STREAM WORD-BY-WORD like ChatGPT!
                words = formatted_answer.split(' ')
                accumulated_text = ""

                for word in words:
                    accumulated_text += word + " "

                    chunk_data = {
                        "type": "word",
                        "content": word + " ",
                        "full_text": accumulated_text,
                        "is_complete": False
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    time.sleep(config.STREAM_DELAY)  # Control streaming speed

            # Send sources and completion
            completion_data = {
                "type": "complete",
                "is_complete": True,
                "sources": sources,
                "timestamp": datetime.now().strftime("%I:%M %p"),
                "response_time": f"{response_time:.2f}s",
                "pdfs_searched": len(set([s['file'] for s in sources])) if sources else 0,
                "model": config.OLLAMA_MODEL,
                "confidence": result.get("confidence", "medium"),
                "answer_text": result["answer"]  # Send plain text for TTS
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except Exception as e:
            print(f"Stream error: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': f'Error: {str(e)}'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

# ============================================================================
# VOICE ENDPOINTS
# ============================================================================

@app.route('/voice/transcribe', methods=['POST'])
def voice_transcribe():
    """
    🎤 SPEECH-TO-TEXT ENDPOINT

    Upload audio file, get text transcription.
    """
    try:
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'text': '',
                'error': 'No audio file provided'
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'text': '',
                'error': 'No file selected'
            }), 400

        if not allowed_audio_file(audio_file.filename):
            return jsonify({
                'success': False,
                'text': '',
                'error': 'Invalid audio format. Supported: wav, mp3, ogg, webm, m4a'
            }), 400

        # Save temporary file
        temp_path = os.path.join(
            'temp',
            f"audio_{datetime.now().timestamp()}_{secure_filename(audio_file.filename)}"
        )
        os.makedirs('temp', exist_ok=True)
        audio_file.save(temp_path)

        # Transcribe
        voice_processor = get_voice_processor()
        result = voice_processor.speech_to_text(temp_path)

        # Cleanup
        try:
            os.remove(temp_path)
        except:
            pass

        return jsonify(result)

    except Exception as e:
        print(f"Voice transcription error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'text': '',
            'error': str(e)
        }), 500

@app.route('/voice/synthesize', methods=['POST'])
def voice_synthesize():
    """
    🔊 TEXT-TO-SPEECH ENDPOINT

    Send text, get audio file.
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400

        # Generate audio
        voice_processor = get_voice_processor()
        result = voice_processor.text_to_speech(text)

        if not result['success']:
            return jsonify(result), 500

        # Return audio file
        return send_file(
            result['file_path'],
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='response.mp3'
        )

    except Exception as e:
        print(f"Voice synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# EXISTING ENDPOINTS (unchanged)
# ============================================================================

@app.route('/history', methods=['GET'])
def get_history():
    user_id = session.get('user_id', 'anonymous')
    history = chat_histories.get(user_id, [])
    return jsonify({"history": history})

@app.route('/clear', methods=['POST'])
def clear_history():
    user_id = session.get('user_id', 'anonymous')
    if user_id in chat_histories:
        chat_histories[user_id] = []
    return jsonify({"message": "History cleared"})

@app.route('/status')
def status():
    rag = get_rag_system()
    pdf_count = 0
    if os.path.exists(config.PDF_FOLDER):
        pdf_count = len([f for f in os.listdir(config.PDF_FOLDER)
                        if f.endswith('.pdf') and not f.startswith('._')])

    return jsonify({
        "status": "online" if rag else "initializing",
        "model": config.OLLAMA_MODEL,
        "system_ready": rag is not None,
        "pdf_count": pdf_count,
        "total_questions": analytics_data.get("total_questions", 0),
        "active_users": len(chat_histories),
        "avg_response_time": f"{analytics_data.get('avg_response_time', 0):.2f}s",
        "timestamp": datetime.now().isoformat()
    })

# ============================================================================
# ADMIN PANEL (unchanged)
# ============================================================================

@app.route('/admin')
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    password = request.form.get('password', '')
    if password == config.ADMIN_PASSWORD:
        session['is_admin'] = True
        return redirect(url_for('admin_dashboard'))
    return "Wrong password!", 403

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    pdfs = []
    if os.path.exists(config.PDF_FOLDER):
        for filename in os.listdir(config.PDF_FOLDER):
            if filename.endswith('.pdf') and not filename.startswith('._'):
                filepath = os.path.join(config.PDF_FOLDER, filename)
                size = os.path.getsize(filepath) / (1024 * 1024)
                modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                pdfs.append({
                    "name": filename,
                    "size": f"{size:.2f} MB",
                    "modified": modified.strftime("%Y-%m-%d %H:%M")
                })

    popular = sorted(
        analytics_data.get("popular_questions", {}).items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return render_template('admin_dashboard.html',
                         analytics=analytics_data,
                         pdfs=pdfs,
                         popular_questions=popular,
                         model=config.OLLAMA_MODEL,
                         university=config.UNIVERSITY_NAME)

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(filepath)
            return jsonify({
                "message": f"✅ File '{filename}' uploaded! Reload database to use it.",
                "filename": filename
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Only PDF files allowed"}), 400

@app.route('/admin/delete/<filename>', methods=['POST'])
def admin_delete(filename):
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        filepath = os.path.join(config.PDF_FOLDER, secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"message": f"File '{filename}' deleted!"})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/reload', methods=['POST'])
def admin_reload():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        rag = get_rag_system()
        success = rag.reload_database()

        if success:
            pdf_count = len([f for f in os.listdir(config.PDF_FOLDER)
                           if f.endswith('.pdf') and not f.startswith('._')])
            analytics_data["total_pdfs"] = pdf_count
            save_analytics()
            return jsonify({"message": "✅ Database reloaded! Now searching ALL PDFs!"})
        else:
            return jsonify({"error": "Failed to reload"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/analytics/reset', methods=['POST'])
def reset_analytics():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    global analytics_data
    analytics_data = {
        "total_questions": 0,
        "popular_questions": {},
        "users_count": 0,
        "total_pdfs": analytics_data.get("total_pdfs", 0),
        "avg_response_time": 0,
        "start_time": datetime.now().isoformat()
    }
    save_analytics()
    return jsonify({"message": "Analytics reset!"})

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Validate configuration, initialise the RAG and voice systems, then start the server."""

    print("=" * 80)
    print(f"🎓 {config.UNIVERSITY_NAME} AI Assistant")
    print(f"   {config.UNIVERSITY_TAGLINE}")
    print(f"   🤖 Model: {config.OLLAMA_MODEL}")
    print("=" * 80)

    # Validate
    print("\n🔧 Validating configuration...")
    errors = config.validate_config()
    if errors:
        for error in errors:
            print(error)
        if any("❌" in e for e in errors):
            print("\n⚠️ Please fix errors before continuing!")
            return

    # Load analytics
    load_analytics()

    # Initialize RAG
    print("\n⚙️ Initializing RAG system...")
    print("⏳ This may take 2-3 minutes for first-time setup...")

    if not initialize_rag():
        print("\n❌ Failed to initialize!")
        return

    # Initialize Voice Processor
    print("\n🎤 Initializing Voice System...")
    try:
        get_voice_processor()
        print("✅ Voice system ready!")
    except Exception as e:
        print(f"⚠️ Voice system failed (optional feature): {e}")

    # Ready!
    print("\n" + "=" * 80)
    print("✅ SYSTEM READY")
    print("=" * 80)
    print(f"\n🌐 Local Access: http://localhost:{config.PORT}")
    print(f"🔐 Admin Panel: http://localhost:{config.PORT}/admin")
    print("\n" + "=" * 80)
    print("📋 Features:")
    print("  ✅ MMR retrieval across all indexed PDFs")
    print("  ✅ Word-by-word streaming responses")
    print("  ✅ HTML-formatted answers with source citations")
    print(f"  ✅ Model: {config.OLLAMA_MODEL}")
    print("  ✅ Voice input (speech-to-text)")
    print("  ✅ Voice output (text-to-speech)")
    print("  ✅ Analytics tracking")
    print("  ✅ Admin dashboard")
    print("=" * 80)
    
    print("\n🚀 Starting web server...\n")
    
    # Run the app
    app.run(
        host='127.0.0.1',
        port=config.PORT,
        debug=config.DEBUG_MODE,
        threaded=config.THREADED
    )

if __name__ == '__main__':
    main()