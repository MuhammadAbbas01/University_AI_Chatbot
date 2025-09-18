#!/usr/bin/env python3
"""
University of Malakand Intelligent AI Chatbot
A comprehensive AI system that provides accurate, contextual answers
about the university using scraped data and advanced NLP techniques.
"""

import sqlite3
import json
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass
import hashlib
import pickle

# For text processing and similarity
from collections import Counter
import math

@dataclass
class SearchResult:
    """Structure for search results"""
    content: str
    title: str
    url: str
    category: str
    relevance_score: float
    snippet: str

class UniversityKnowledgeBase:
    """Intelligent knowledge base for university information"""
    
    def __init__(self, data_dir: str = "university_data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "university_knowledge.db"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load knowledge base
        self.load_knowledge_base()
        
        # Initialize text processing
        self.stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'])
        
        # Cache for faster searches
        self.search_cache = {}
        
        # Faculty and department quick access
        self.faculty_index = {}
        self.department_index = {}
        self.build_indexes()

    def load_knowledge_base(self):
        """Load all university data from database and files"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Knowledge base not found at {self.db_path}. Please run data_scraper.py first.")
        
        self.logger.info("Loading university knowledge base...")
        
        # Load from database
        conn = sqlite3.connect(self.db_path)
        
        # Load all pages
        self.pages = []
        cursor = conn.execute("SELECT url, title, content, content_type FROM pages")
        for row in cursor.fetchall():
            self.pages.append({
                'url': row[0],
                'title': row[1],
                'content': row[2],
                'content_type': row[3]
            })
        
        # Load faculty information
        self.faculty = []
        cursor = conn.execute("SELECT * FROM faculty")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            self.faculty.append(dict(zip(columns, row)))
        
        # Load departments
        self.departments = []
        cursor = conn.execute("SELECT * FROM departments")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            self.departments.append(dict(zip(columns, row)))
        
        # Load notifications
        self.notifications = []
        cursor = conn.execute("SELECT * FROM notifications")
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            self.notifications.append(dict(zip(columns, row)))
        
        conn.close()
        self.logger.info(f"Loaded {len(self.pages)} pages, {len(self.faculty)} faculty, {len(self.departments)} departments")

    def build_indexes(self):
        """Build search indexes for faster retrieval"""
        # Build faculty index
        for faculty_member in self.faculty:
            name = faculty_member.get('name', '').lower()
            if name:
                self.faculty_index[name] = faculty_member
        
        # Build department index
        for dept in self.departments:
            name = dept.get('name', '').lower()
            if name:
                self.department_index[name] = dept

    def preprocess_text(self, text: str) -> List[str]:
        """Clean and tokenize text for processing"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Tokenize and remove stopwords
        words = [word for word in text.split() if word and word not in self.stopwords and len(word) > 2]
        
        return words

    def calculate_tf_idf(self, query_words: List[str], document: str) -> float:
        """Calculate TF-IDF score for document relevance"""
        doc_words = self.preprocess_text(document)
        doc_word_count = len(doc_words)
        
        if doc_word_count == 0:
            return 0.0
        
        # Calculate TF (Term Frequency)
        doc_word_freq = Counter(doc_words)
        tf_score = 0
        
        for word in query_words:
            tf = doc_word_freq.get(word, 0) / doc_word_count
            if tf > 0:
                tf_score += tf
        
        # Simple relevance score (can be enhanced with proper IDF)
        relevance = tf_score * len([w for w in query_words if w in doc_words]) / len(query_words)
        
        return relevance

    def semantic_search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Perform semantic search across university knowledge base"""
        query_words = self.preprocess_text(query)
        results = []
        
        # Search through all pages
        for page in self.pages:
            relevance = self.calculate_tf_idf(query_words, page['content'])
            
            if relevance > 0:
                # Create snippet
                snippet = self.create_snippet(page['content'], query_words)
                
                result = SearchResult(
                    content=page['content'],
                    title=page['title'],
                    url=page['url'],
                    category=page['content_type'],
                    relevance_score=relevance,
                    snippet=snippet
                )
                results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:limit]

    def create_snippet(self, content: str, query_words: List[str], snippet_length: int = 200) -> str:
        """Create a relevant snippet from content"""
        sentences = content.split('.')
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_words = self.preprocess_text(sentence)
            score = len(set(query_words) & set(sentence_words))
            
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
        
        if len(best_sentence) > snippet_length:
            best_sentence = best_sentence[:snippet_length] + "..."
        
        return best_sentence or content[:snippet_length] + "..."

    def find_faculty_by_name(self, name: str) -> Optional[Dict]:
        """Find faculty member by name"""
        name_lower = name.lower()
        
        # Exact match
        if name_lower in self.faculty_index:
            return self.faculty_index[name_lower]
        
        # Partial match
        for faculty_name, faculty_info in self.faculty_index.items():
            if name_lower in faculty_name or any(part in faculty_name for part in name_lower.split()):
                return faculty_info
        
        return None

    def get_department_info(self, dept_name: str) -> Optional[Dict]:
        """Get department information"""
        dept_lower = dept_name.lower()
        
        # Direct match
        if dept_lower in self.department_index:
            return self.department_index[dept_lower]
        
        # Partial match
        for department_name, dept_info in self.department_index.items():
            if dept_lower in department_name or any(part in department_name for part in dept_lower.split()):
                return dept_info
        
        return None

    def get_recent_notifications(self, limit: int = 5) -> List[Dict]:
        """Get recent notifications"""
        sorted_notifications = sorted(
            self.notifications, 
            key=lambda x: x.get('date', ''), 
            reverse=True
        )
        return sorted_notifications[:limit]

class UniversityAIChatbot:
    """Main AI chatbot class for University of Malakand"""
    
    def __init__(self, data_dir: str = "university_data"):
        self.kb = UniversityKnowledgeBase(data_dir)
        self.conversation_history = []
        
        # Intent patterns
        self.intent_patterns = {
            'faculty_info': ['faculty', 'professor', 'teacher', 'dr.', 'dr ', 'staff'],
            'admissions': ['admission', 'apply', 'application', 'entry', 'requirement'],
            'departments': ['department', 'dept', 'school', 'faculty of'],
            'notifications': ['notification', 'news', 'announcement', 'notice', 'update'],
            'academics': ['course', 'program', 'degree', 'semester', 'exam', 'result'],
            'research': ['research', 'publication', 'journal', 'paper', 'study'],
            'contact': ['contact', 'phone', 'email', 'address', 'location'],
            'general': ['about', 'history', 'information', 'what is', 'tell me']
        }
        
        # Common question patterns
        self.question_patterns = {
            'who_is': r'who is (.+?)[\?]?',
            'what_is': r'what is (.+?)[\?]?',
            'when_is': r'when is (.+?)[\?]?',
            'where_is': r'where is (.+?)[\?]?',
            'how_to': r'how to (.+?)[\?]?'
        }

    def detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        query_lower = query.lower()
        
        intent_scores = {}
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general'

    def extract_entities(self, query: str) -> Dict:
        """Extract entities from query"""
        entities = {}
        
        # Check for person names (Dr./Prof. patterns)
        name_patterns = [
            r'(dr\.?\s+[a-z\s]+)',
            r'(prof\.?\s+[a-z\s]+)',
            r'(professor\s+[a-z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities['person'] = match.group(1).strip()
                break
        
        # Extract department names
        dept_keywords = ['department of', 'dept of', 'faculty of']
        for keyword in dept_keywords:
            pattern = rf'{keyword}\s+([a-z\s]+)'
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities['department'] = match.group(1).strip()
                break
        
        return entities

    def generate_response(self, query: str) -> str:
        """Generate intelligent response based on query"""
        intent = self.detect_intent(query)
        entities = self.extract_entities(query)
        
        # Handle specific intents
        if intent == 'faculty_info':
            return self.handle_faculty_query(query, entities)
        elif intent == 'admissions':
            return self.handle_admissions_query(query)
        elif intent == 'departments':
            return self.handle_department_query(query, entities)
        elif intent == 'notifications':
            return self.handle_notifications_query(query)
        else:
            return self.handle_general_query(query)

    def handle_faculty_query(self, query: str, entities: Dict) -> str:
        """Handle faculty-related queries"""
        if 'person' in entities:
            faculty_info = self.kb.find_faculty_by_name(entities['person'])
            if faculty_info:
                response = f"**{faculty_info.get('name', 'N/A')}**\n"
                if faculty_info.get('designation'):
                    response += f"Position: {faculty_info['designation']}\n"
                if faculty_info.get('department'):
                    response += f"Department: {faculty_info['department']}\n"
                if faculty_info.get('email'):
                    response += f"Email: {faculty_info['email']}\n"
                if faculty_info.get('research_interests'):
                    response += f"Research Interests: {faculty_info['research_interests']}\n"
                if faculty_info.get('bio'):
                    response += f"\nBio: {faculty_info['bio'][:200]}..."
                
                return response
        
        # General faculty search
        search_results = self.kb.semantic_search(query, limit=3)
        faculty_results = [r for r in search_results if r.category == 'faculty']
        
        if faculty_results:
            response = "Here's what I found about faculty:\n\n"
            for result in faculty_results[:2]:
                response += f"**{result.title}**\n{result.snippet}\n\n"
            return response
        
        return "I couldn't find specific faculty information. Could you provide more details or check the faculty directory on the university website?"

    def handle_admissions_query(self, query: str) -> str:
        """Handle admissions-related queries"""
        search_results = self.kb.semantic_search(query, limit=5)
        admission_results = [r for r in search_results if r.category == 'admissions' or 'admission' in r.title.lower()]
        
        if admission_results:
            response = "**Admissions Information:**\n\n"
            for result in admission_results[:3]:
                response += f"**{result.title}**\n{result.snippet}\n\n"
            
            response += "\nFor the most current admission requirements and deadlines, please visit the university's official admissions page."
            return response
        
        # Fallback to general search
        general_results = self.kb.semantic_search(query, limit=2)
        if general_results:
            response = "Here's what I found about admissions:\n\n"
            for result in general_results:
                response += f"{result.snippet}\n\n"
            return response
        
        return "For detailed admission information, please visit the university's official website or contact the admissions office directly."

    def handle_department_query(self, query: str, entities: Dict) -> str:
        """Handle department-related queries"""
        if 'department' in entities:
            dept_info = self.kb.get_department_info(entities['department'])
            if dept_info:
                response = f"**{dept_info.get('name', 'Department')}**\n"
                if dept_info.get('description'):
                    response += f"Description: {dept_info['description']}\n"
                if dept_info.get('head'):
                    response += f"Department Head: {dept_info['head']}\n"
                if dept_info.get('faculty_count'):
                    response += f"Faculty Members: {dept_info['faculty_count']}\n"
                if dept_info.get('programs'):
                    response += f"Programs: {dept_info['programs']}\n"
                
                return response
        
        # General department search
        search_results = self.kb.semantic_search(query, limit=3)
        dept_results = [r for r in search_results if r.category == 'department']
        
        if dept_results:
            response = "Here's information about departments:\n\n"
            for result in dept_results:
                response += f"**{result.title}**\n{result.snippet}\n\n"
            return response
        
        return "I couldn't find specific department information. Please provide more details about which department you're interested in."

    def handle_notifications_query(self, query: str) -> str:
        """Handle notifications and news queries"""
        recent_notifications = self.kb.get_recent_notifications(limit=5)
        
        if recent_notifications:
            response = "**Recent University Notifications:**\n\n"
            for notification in recent_notifications:
                response += f"• **{notification.get('title', 'No Title')}**\n"
                if notification.get('date'):
                    response += f"  Date: {notification['date']}\n"
                if notification.get('content'):
                    response += f"  {notification['content'][:100]}...\n\n"
        else:
            # Search in general content
            search_results = self.kb.semantic_search(query, limit=3)
            notification_results = [r for r in search_results if r.category == 'notifications']
            
            if notification_results:
                response = "**University Updates:**\n\n"
                for result in notification_results:
                    response += f"**{result.title}**\n{result.snippet}\n\n"
            else:
                response = "Please check the university's official website for the latest notifications and announcements."
        
        return response

    def handle_general_query(self, query: str) -> str:
        """Handle general queries using semantic search"""
        search_results = self.kb.semantic_search(query, limit=5)
        
        if not search_results:
            return "I'm sorry, I couldn't find specific information about that. Could you please rephrase your question or be more specific?"
        
        # Group results by relevance
        high_relevance = [r for r in search_results if r.relevance_score > 0.1]
        medium_relevance = [r for r in search_results if 0.05 < r.relevance_score <= 0.1]
        
        response = ""
        
        if high_relevance:
            response += "Here's what I found:\n\n"
            for result in high_relevance[:2]:
                response += f"**{result.title}**\n{result.snippet}\n\n"
        
        if medium_relevance and len(high_relevance) < 2:
            response += "Additional information:\n\n"
            for result in medium_relevance[:1]:
                response += f"**{result.title}**\n{result.snippet}\n\n"
        
        # Add helpful suggestions
        response += "\n💡 *You can ask me about faculty members, departments, admissions, research, or recent notifications.*"
        
        return response

    def chat(self, query: str) -> str:
        """Main chat interface"""
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'type': 'user'
        })
        
        # Generate response
        response = self.generate_response(query)
        
        # Add response to history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'type': 'bot'
        })
        
        return response

    def get_quick_help(self) -> str:
        """Provide quick help information"""
        return """
🎓 **University of Malakand AI Assistant**

I can help you with:
• **Faculty Information** - "Tell me about Dr. [Name]" or "Who is the professor of [subject]?"
• **Departments** - "Information about Computer Science department"
• **Admissions** - "How to apply for admission?" or "Admission requirements"
• **Notifications** - "Latest university news" or "Recent announcements"
• **Research** - "Research papers" or "Publications"
• **General Info** - "About University of Malakand"

**Example Questions:**
- "Who is Dr. Fakhruddin?"
- "How to apply for BS Computer Science?"
- "What are the recent notifications?"
- "Tell me about the English department"

Just ask your question in English or Urdu, and I'll provide you with accurate information!
        """

def main():
    """Main function to run the chatbot"""
    print("🎓 University of Malakand AI Chatbot")
    print("=" * 50)
    
    try:
        chatbot = UniversityAIChatbot()
        print("✅ AI Chatbot initialized successfully!")
        print("\nType 'help' for assistance, 'quit' to exit\n")
        
        while True:
            query = input("You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("Chatbot: Thank you for using University of Malakand AI Assistant! Goodbye! 👋")
                break
            elif query.lower() == 'help':
                print("Chatbot:", chatbot.get_quick_help())
                continue
            elif not query:
                continue
            
            # Get response
            response = chatbot.chat(query)
            print(f"Chatbot: {response}\n")
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please run the data scraper first to build the knowledge base.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
