"""
Core Generic Course Assistant
Domain-agnostic RAG system that can work with any subject using plugin configurations
Enhanced with dynamic content analysis capabilities
"""
import os
import chromadb
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import importlib

# Try different OpenAI imports for compatibility
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available. Install with: pip install openai")

load_dotenv()

class CoreAssistant:
    """
    Generic course assistant that can adapt to any subject domain
    Uses subject-specific configuration modules for domain knowledge
    Enhanced with dynamic content analysis for any educational material
    """
    
    def __init__(self, subject_name: str = None, collection_name: str = "study_guides"):
        """
        Initialize the core assistant
        
        Args:
            subject_name: Name of subject (e.g., 'biology', 'chemistry')
            collection_name: ChromaDB collection name
        """
        self.collection_name = collection_name
        self.chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.chroma_client.get_collection(collection_name)
        
        # Load subject configuration
        self.subject_config = self._load_subject_config(subject_name)
        self.subject_info = self.subject_config.get_subject_info()
        
        # Initialize content analyzer
        self.content_analysis = None  # Will be populated when content is analyzed
        
        # Initialize OpenAI client
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.ai_enabled = True
                print(f"✅ OpenAI integration enabled for {self.subject_info['display_name']}")
                
                # Initialize content analyzer
                from content_analyzer import ContentAnalyzer
                self.content_analyzer = ContentAnalyzer()
                print(f"✅ Content analyzer initialized")
            except Exception as e:
                print(f"⚠️ Content analyzer initialization failed: {e}")
                self.content_analyzer = None
            except Exception as e:
                print(f"⚠️ OpenAI client setup failed: {e}")
                self.ai_enabled = False
        else:
            self.ai_enabled = False
            print(f"⚠️ OpenAI not available - using search-only mode for {self.subject_info['display_name']}")
    
    def _load_subject_config(self, subject_name: str = None):
        """
        Dynamically load subject configuration
        Falls back to auto-detection or generic config
        """
        if subject_name:
            # Try to load specified subject
            try:
                module_name = f"subjects.{subject_name}_config"
                config_module = importlib.import_module(module_name)
                config_class_name = f"{subject_name.capitalize()}Config"
                return getattr(config_module, config_class_name)
            except (ImportError, AttributeError) as e:
                print(f"⚠️ Could not load {subject_name} config: {e}")
                print("📁 Falling back to auto-detection...")
        
        # Auto-detect subject from content or use generic
        detected_subject = self._auto_detect_subject()
        if detected_subject:
            try:
                module_name = f"subjects.{detected_subject}_config"
                config_module = importlib.import_module(module_name)
                config_class_name = f"{detected_subject.capitalize()}Config"
                print(f"🔍 Auto-detected subject: {detected_subject}")
                return getattr(config_module, config_class_name)
            except (ImportError, AttributeError):
                pass
        
        # Fall back to generic config
        print("📋 Using generic configuration")
        from subjects.generic_config import GenericConfig
        return GenericConfig
    
    def _auto_detect_subject(self) -> Optional[str]:
        """
        Auto-detect subject by analyzing content in ChromaDB
        Returns subject name if detected, None otherwise
        """
        try:
            # Sample some content from the collection
            sample_results = self.collection.query(
                query_texts=[""],
                n_results=10,
                include=["documents", "metadatas"]
            )
            
            if not sample_results['documents'] or not sample_results['documents'][0]:
                return None
            
            # Combine sample content for analysis
            sample_text = " ".join(sample_results['documents'][0]).lower()
            
            # Check available subject configs
            available_subjects = self._discover_available_subjects()
            
            for subject in available_subjects:
                try:
                    module_name = f"subjects.{subject}_config"
                    config_module = importlib.import_module(module_name)
                    config_class_name = f"{subject.capitalize()}Config"
                    config_class = getattr(config_module, config_class_name)
                    
                    keywords = config_class.detect_subject_keywords()
                    keyword_count = sum(1 for keyword in keywords if keyword in sample_text)
                    
                    # If we find enough keywords, this is likely the subject
                    if keyword_count >= 3:  # Threshold for detection
                        return subject
                        
                except (ImportError, AttributeError):
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Auto-detection failed: {e}")
            return None
    
    def _discover_available_subjects(self) -> List[str]:
        """
        Dynamically discover available subject configurations
        Scans the subjects directory for *_config.py files
        """
        subjects = []
        try:
            import pkgutil
            import subjects
            
            for importer, modname, ispkg in pkgutil.iter_modules(subjects.__path__):
                if modname.endswith('_config') and modname != 'generic_config':
                    subject_name = modname.replace('_config', '')
                    subjects.append(subject_name)
        except (ImportError, AttributeError):
            # Fallback: try known subjects manually
            known_subjects = ['biology', 'chemistry', 'physics', 'history', 'math']
            for subject in known_subjects:
                try:
                    module_name = f"subjects.{subject}_config"
                    importlib.import_module(module_name)
                    subjects.append(subject)
                except ImportError:
                    continue
        
        return subjects
    
    def retrieve_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from ChromaDB"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            context_chunks = []
            if results['documents'] and results['documents'][0]:
                for doc, metadata, distance in zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                ):
                    context_chunks.append({
                        'content': doc,
                        'source': f"{metadata['title']} - {metadata['section_title']}",
                        'chapter': metadata['chapter'],
                        'lectures': metadata['lectures'],
                        'section_type': metadata['section_type'],
                        'relevance_score': 1.0 / (1.0 + distance)
                    })
            
            return context_chunks
        except Exception as e:
            print(f"❌ Context retrieval error: {e}")
            return []
    
    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI answer using retrieved context and subject-specific prompts"""
        if not self.ai_enabled:
            return self._fallback_response(question, context_chunks)
        
        # Build context for the prompt
        context_text = ""
        sources = []
        
        for i, chunk in enumerate(context_chunks[:3], 1):  # Use top 3 chunks
            context_text += f"\n--- Source {i}: {chunk['source']} ---\n"
            context_text += chunk['content']
            context_text += "\n"
            sources.append({
                'source': chunk['source'],
                'chapter': chunk['chapter'],
                'lectures': chunk['lectures'],
                'relevance': chunk['relevance_score']
            })
        
        # Get subject-specific system prompt
        system_prompt = self.subject_config.get_system_prompt()
        
        user_prompt = f"""Question: {question}

Course Content:
{context_text}

Please provide a clear, educational answer based on this course content."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': 'high' if len(context_chunks) >= 2 else 'medium',
                'method': 'ai_generated',
                'subject': self.subject_info['display_name']
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return self._fallback_response(question, context_chunks)
    
    def _fallback_response(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback response when AI is not available"""
        if not context_chunks:
            return {
                'answer': f"I couldn't find relevant content to answer your question about '{question}'. Try rephrasing or asking about a different topic.",
                'sources': [],
                'confidence': 'low',
                'method': 'search_only',
                'subject': self.subject_info['display_name']
            }
        
        # Create answer from top context chunks
        answer_parts = [f"Based on the course content, here's what I found about '{question}':\n"]
        sources = []
        
        for i, chunk in enumerate(context_chunks[:2], 1):
            answer_parts.append(f"\n**From {chunk['source']}:**")
            answer_parts.append(chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content'])
            sources.append({
                'source': chunk['source'],
                'chapter': chunk['chapter'],
                'lectures': chunk['lectures'],
                'relevance': chunk['relevance_score']
            })
        
        return {
            'answer': "\n".join(answer_parts),
            'sources': sources,
            'confidence': 'medium' if len(context_chunks) >= 2 else 'low',
            'method': 'search_only',
            'subject': self.subject_info['display_name']
        }
    
    def ask_question(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """Main method to ask a question and get an answer"""
        print(f"🔍 Searching for: {question}")
        
        # Retrieve relevant context
        context_chunks = self.retrieve_context(question, context_limit)
        print(f"📄 Found {len(context_chunks)} relevant chunks")
        
        # Generate answer
        result = self.generate_answer(question, context_chunks)
        
        return result
    
    def suggest_related_topics(self, question: str) -> List[str]:
        """Suggest related topics based on subject-specific keywords"""
        suggestions = []
        question_lower = question.lower()
        
        topic_keywords = self.subject_config.get_topic_keywords()
        
        for topic, related in topic_keywords.items():
            if topic in question_lower:
                suggestions.extend(related)
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def get_welcome_message(self) -> str:
        """Get subject-specific welcome message"""
        return self.subject_config.get_welcome_message()
    
    # ===== NEW: CONTENT ANALYSIS METHODS =====
    
    def analyze_existing_content(self) -> Dict[str, Any]:
        """
        Analyze all existing content in the collection to discover topics and structure
        This creates a dynamic understanding of what material is available
        """
        if not self.content_analyzer:
            return {"error": "Content analyzer not available"}
        
        print("🔍 Analyzing existing content for topic discovery...")
        
        try:
            # Get all content from collection
            results = self.collection.get(include=["documents", "metadatas"])
            content_chunks = results['documents']
            metadatas = results['metadatas']
            
            if not content_chunks:
                return {"error": "No content found in collection"}
            
            # Analyze content structure
            self.content_analysis = self.content_analyzer.analyze_content(
                content_chunks,
                source_info={"filename": "course_content", "type": "study_materials"}
            )
            
            print(f"✅ Analysis complete: Found {len(self.content_analysis.main_topics)} main topics")
            
            return {
                "status": "success",
                "topics_found": len(self.content_analysis.main_topics),
                "subject_area": self.content_analysis.subject_area,
                "content_type": self.content_analysis.content_type,
                "key_terms": len(self.content_analysis.key_terms),
                "learning_objectives": len(self.content_analysis.learning_objectives)
            }
            
        except Exception as e:
            print(f"❌ Content analysis failed: {e}")
            return {"error": str(e)}
    
    def get_discovered_topics(self) -> List[Dict[str, Any]]:
        """Get topics discovered from content analysis"""
        if not self.content_analysis:
            self.analyze_existing_content()
        
        if not self.content_analysis:
            return []
        
        topics = []
        for topic in self.content_analysis.main_topics:
            topics.append({
                "name": topic.name,
                "description": topic.description,
                "key_concepts": topic.key_concepts,
                "subtopics": topic.subtopics,
                "difficulty_level": topic.difficulty_level,
                "question_types": topic.question_types,
                "prerequisites": topic.prerequisites
            })
        
        return topics
    
    def get_content_summary(self) -> str:
        """Get a human-readable summary of analyzed content"""
        if not self.content_analysis:
            self.analyze_existing_content()
        
        if not self.content_analysis:
            return "Content analysis not available"
        
        return self.content_analyzer.get_topic_summary(self.content_analysis)
    
    def can_generate_quiz_for(self, topic_name: str) -> bool:
        """Check if we have enough content to generate a quiz for a specific topic"""
        if not self.content_analysis:
            self.analyze_existing_content()
        
        if not self.content_analysis:
            return False
        
        # Check if topic exists in our analysis
        for topic in self.content_analysis.main_topics:
            if topic_name.lower() in topic.name.lower() or topic_name.lower() in [kc.lower() for kc in topic.key_concepts]:
                return len(topic.key_concepts) >= 3  # Need at least 3 concepts for a quiz
        
        return False
    
    def get_available_quiz_topics(self) -> List[str]:
        """Get list of topics that have enough content for quiz generation"""
        if not self.content_analysis:
            self.analyze_existing_content()
        
        if not self.content_analysis:
            return []
        
        available_topics = []
        for topic in self.content_analysis.main_topics:
            if len(topic.key_concepts) >= 3:  # Minimum concepts for quiz
                available_topics.append(topic.name)
        
        return available_topics


def main():
    """Interactive demo of the core assistant"""
    print("🎓 Core Course Assistant - Subject Detection Demo")
    print("=" * 60)
    
    # Auto-detect subject from content
    assistant = CoreAssistant()
    
    print(assistant.get_welcome_message())
    print(f"🧭 Active Subject: {assistant.subject_info['display_name']}")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n" + "="*60)
        
        # Get answer
        result = assistant.ask_question(question)
        
        # Display the answer
        print("🤖 Answer:")
        print("-" * 20)
        print(result['answer'])
        
        # Show sources
        if result['sources']:
            print(f"\n📚 Sources (Confidence: {result['confidence']}):")
            for i, source in enumerate(result['sources'], 1):
                print(f"   {i}. {source['source']}")
                print(f"      Chapter: {source['chapter']}")
                print(f"      Lectures: {source['lectures']}")
        
        # Show related topics
        related = assistant.suggest_related_topics(question)
        if related:
            print(f"\n🔗 Related topics you might want to explore:")
            for topic in related:
                print(f"   - {topic}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
