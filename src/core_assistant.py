"""
Core Generic Course Assistant
Domain-agnostic RAG system that can work with any subject using plugin configurations
Enhanced with dynamic content analysis capabilities and quiz generation
"""
import os
import chromadb
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import importlib
import re
import json

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
                
                # Initialize quiz generator
                from quiz_generator import QuizGenerator
                self.quiz_generator = QuizGenerator(api_key=os.getenv("OPENAI_API_KEY"))
                print(f"✅ Quiz generator initialized")
                
            except Exception as e:
                print(f"⚠️ Content analyzer initialization failed: {e}")
                self.content_analyzer = None
                self.quiz_generator = None
        else:
            self.ai_enabled = False
            self.quiz_generator = None
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
        """Main method to ask a question or generate a quiz"""
        print(f"🔍 Processing: {question}")
        
        # Check if this is a quiz request
        quiz_intent = self._detect_quiz_intent(question)
        
        if quiz_intent['is_quiz_request']:
            return self._handle_quiz_request(question, quiz_intent)
        else:
            return self._handle_normal_question(question, context_limit)
    
    def _detect_quiz_intent(self, question: str) -> Dict[str, Any]:
        """Detect if the user wants to generate a quiz"""
        question_lower = question.lower()
        
        # Quiz trigger words and patterns
        quiz_keywords = [
            'quiz', 'test', 'questions', 'practice', 'assess', 'evaluate',
            'exam', 'review', 'study', 'flashcard', 'multiple choice', 
            'fill in blank', 'true false'
        ]
        
        quiz_patterns = [
            r'(create|generate|make|give me|start) (a |an )?(quiz|test)',
            r'quiz me (on|about)',
            r'(test|assess) my (knowledge|understanding)',
            r'practice (questions|problems)',
            r'(multiple choice|fill.in.blank|flashcard) (questions|quiz)',
            r'(\d+) questions? (about|on)',
            r'study (with|using) (questions|quiz|flashcards)'
        ]
        
        # Check for quiz keywords
        has_quiz_keywords = any(keyword in question_lower for keyword in quiz_keywords)
        
        # Check for quiz patterns
        has_quiz_pattern = any(re.search(pattern, question_lower) for pattern in quiz_patterns)
        
        # Extract quiz parameters
        quiz_params = self._extract_quiz_parameters(question)
        
        return {
            'is_quiz_request': has_quiz_keywords or has_quiz_pattern,
            'confidence': 'high' if has_quiz_pattern else 'medium' if has_quiz_keywords else 'low',
            'parameters': quiz_params
        }
    
    def _extract_quiz_parameters(self, question: str) -> Dict[str, Any]:
        """Extract quiz parameters from the question"""
        from quiz_generator import QuizType, QuizFormat
        
        question_lower = question.lower()
        params = {
            'quiz_type': QuizType.MIXED,
            'quiz_format': QuizFormat.STANDARD,
            'length': 5,
            'topic': None,
            'difficulty': 'medium'
        }
        
        # Extract number of questions
        number_match = re.search(r'(\d+)\s*(questions?|problems?)', question_lower)
        if number_match:
            params['length'] = min(int(number_match.group(1)), 20)  # Cap at 20 questions
        
        # Extract quiz type
        if 'multiple choice' in question_lower or 'mc' in question_lower:
            params['quiz_type'] = QuizType.MULTIPLE_CHOICE
        elif 'fill in' in question_lower or 'blank' in question_lower:
            params['quiz_type'] = QuizType.FILL_IN_BLANK
        elif 'mixed' in question_lower or 'both' in question_lower:
            params['quiz_type'] = QuizType.MIXED
        
        # Extract format
        if 'flashcard' in question_lower:
            params['quiz_format'] = QuizFormat.FLASHCARD
        
        # Extract difficulty
        if 'easy' in question_lower or 'simple' in question_lower:
            params['difficulty'] = 'easy'
        elif 'hard' in question_lower or 'difficult' in question_lower or 'advanced' in question_lower:
            params['difficulty'] = 'hard'
        
        # Extract topic - everything after "on" or "about"
        topic_patterns = [
            r'(?:quiz me|questions?|test)\s+(?:on|about)\s+(.+?)(?:\s|$)',
            r'(?:on|about)\s+(.+?)(?:\s+(?:quiz|test|questions?))?$',
            r'(.+?)\s+(?:quiz|test|questions?)$'
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, question_lower)
            if match:
                topic = match.group(1).strip()
                # Clean up the topic
                topic = re.sub(r'\b(?:quiz|test|questions?|practice|study)\b', '', topic).strip()
                if topic and len(topic) > 2:
                    params['topic'] = topic
                    break
        
        return params
    
    def _handle_quiz_request(self, question: str, quiz_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quiz generation request"""
        if not self.quiz_generator:
            return {
                'answer': "❌ Quiz generation is not available. Please ensure OpenAI API is configured.",
                'type': 'error',
                'sources': []
            }
        
        params = quiz_intent['parameters']
        
        # If no topic specified, try to extract from context or suggest topics
        if not params['topic']:
            available_topics = self.get_available_quiz_topics()
            if available_topics:
                topic_list = ', '.join(available_topics[:5])
                return {
                    'answer': f"🎯 I can create quizzes on these topics: {topic_list}\n\nPlease specify which topic you'd like to be quizzed on. For example:\n• 'Quiz me on photosynthesis'\n• 'Create 5 multiple choice questions about cell division'\n• 'Test my knowledge of genetics'",
                    'type': 'topic_selection',
                    'available_topics': available_topics,
                    'sources': []
                }
            else:
                return {
                    'answer': "❌ I don't have enough content to generate quizzes. Please add some study materials to your knowledge base first.",
                    'type': 'error',
                    'sources': []
                }
        
        # Generate quiz content from knowledge base
        topic_content = self._get_topic_content(params['topic'])
        
        if not topic_content:
            return {
                'answer': f"❌ I couldn't find enough content about '{params['topic']}' to create a quiz. Try a different topic or add more study materials.",
                'type': 'error',
                'sources': []
            }
        
        try:
            # Create quiz session
            quiz_session = self.quiz_generator.create_quiz(
                content_source=topic_content,
                quiz_length=params['length'],
                quiz_type=params['quiz_type'],
                quiz_format=params['quiz_format'],
                difficulty=params['difficulty'],
                use_knowledge_base=True
            )
            
            # Present first question
            first_question = self.quiz_generator.present_question(0)
            
            response = {
                'answer': self._format_quiz_response(first_question, quiz_session),
                'type': 'quiz_start',
                'quiz_session_id': quiz_session.session_id,
                'current_question': 0,
                'total_questions': quiz_session.total_questions,
                'quiz_format': quiz_session.quiz_format.value,
                'sources': [{'source': f"Quiz on {params['topic']}", 'chapter': 'Generated', 'lectures': 'AI Generated'}]
            }
            
            return response
            
        except Exception as e:
            return {
                'answer': f"❌ Failed to generate quiz: {str(e)}",
                'type': 'error',
                'sources': []
            }
    
    def _get_topic_content(self, topic: str) -> str:
        """Get relevant content for the topic from knowledge base"""
        try:
            # Retrieve relevant context for the topic
            results = self.collection.query(
                query_texts=[topic],
                n_results=10,  # Get more content for quiz generation
                include=["documents", "metadatas"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                return ""
            
            # Combine relevant content
            content_parts = []
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                content_parts.append(f"From {metadata['title']}: {doc}")
            
            return "\n\n".join(content_parts)
            
        except Exception as e:
            print(f"❌ Error retrieving topic content: {e}")
            return ""
    
    def _format_quiz_response(self, question_data: Dict, quiz_session) -> str:
        """Format the quiz question for display"""
        response_parts = [
            f"🎯 **{quiz_session.quiz_type.value.replace('_', ' ').title()} Quiz Started!**",
            f"📊 Question {question_data['question_number']} of {question_data['total_questions']}",
            "",
            f"**Question:** {question_data['question']}"
        ]
        
        if question_data.get('options'):
            response_parts.append("")
            response_parts.append("**Options:**")
            for option in question_data['options']:
                response_parts.append(f"  {option}")
        
        response_parts.extend([
            "",
            f"*Difficulty: {question_data['difficulty']} | Format: {question_data['format']}*",
            "",
            "💡 **How to answer:**",
            "• For multiple choice: Type the letter (A, B, C, or D)",
            "• For fill-in-blank: Type your answer",
            "• To skip: Type 'skip'",
            "• To end quiz: Type 'end quiz'"
        ])
        
        return "\n".join(response_parts)
    
    def _handle_normal_question(self, question: str, context_limit: int = 5) -> Dict[str, Any]:
        """Handle normal Q&A (existing functionality)"""
        # Retrieve relevant context
        context_chunks = self.retrieve_context(question, context_limit)
        print(f"📄 Found {len(context_chunks)} relevant chunks")
        
        # Generate answer
        result = self.generate_answer(question, context_chunks)
        result['type'] = 'normal_qa'
        
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


    # ===== QUIZ INTERACTION METHODS =====
    
    def continue_quiz(self, answer: str, session_id: str = None, question_index: int = 0) -> Dict[str, Any]:
        """Continue an active quiz session by submitting an answer"""
        if not self.quiz_generator or not self.quiz_generator.current_session:
            return {
                'answer': "❌ No active quiz session found. Start a new quiz by asking for one!",
                'type': 'error',
                'sources': []
            }
        
        # Handle special commands
        if answer.lower() in ['end quiz', 'quit', 'stop']:
            return self.end_quiz()
        elif answer.lower() == 'skip':
            return self.skip_question(question_index)
        
        try:
            # Submit answer
            result = self.quiz_generator.submit_answer(question_index, answer)
            
            # Check if this was the last question
            session = self.quiz_generator.current_session
            if question_index + 1 >= session.total_questions:
                # Quiz complete
                final_results = self.quiz_generator.complete_quiz()
                return {
                    'answer': self._format_quiz_completion(result, final_results),
                    'type': 'quiz_complete',
                    'final_score': final_results['score'],
                    'total_questions': final_results['total_questions'],
                    'percentage': final_results['percentage'],
                    'sources': []
                }
            else:
                # Present next question
                next_question = self.quiz_generator.present_question(question_index + 1)
                return {
                    'answer': self._format_quiz_answer_feedback(result, next_question, session),
                    'type': 'quiz_continue',
                    'current_question': question_index + 1,
                    'score': result['score'],
                    'sources': []
                }
                
        except Exception as e:
            return {
                'answer': f"❌ Error processing answer: {str(e)}",
                'type': 'error',
                'sources': []
            }
    
    def skip_question(self, question_index: int) -> Dict[str, Any]:
        """Skip current question and move to next"""
        session = self.quiz_generator.current_session
        if question_index + 1 >= session.total_questions:
            return self.end_quiz()
        
        next_question = self.quiz_generator.present_question(question_index + 1)
        return {
            'answer': f"⏭️ **Question Skipped**\n\n{self._format_quiz_response(next_question, session)}",
            'type': 'quiz_continue',
            'current_question': question_index + 1,
            'sources': []
        }
    
    def end_quiz(self) -> Dict[str, Any]:
        """End current quiz session"""
        if not self.quiz_generator.current_session:
            return {
                'answer': "❌ No active quiz session to end.",
                'type': 'error',
                'sources': []
            }
        
        final_results = self.quiz_generator.complete_quiz()
        return {
            'answer': self._format_quiz_completion(None, final_results, ended_early=True),
            'type': 'quiz_complete',
            'final_score': final_results['score'],
            'total_questions': final_results['total_questions'],
            'percentage': final_results['percentage'],
            'sources': []
        }
    
    def _format_quiz_answer_feedback(self, answer_result: Dict, next_question: Dict, session) -> str:
        """Format feedback for an answer and present next question"""
        feedback_parts = [
            f"{'✅' if answer_result['correct'] else '❌'} **Answer Feedback:**",
            answer_result['feedback'],
            "",
            f"**Current Score:** {answer_result['score']}",
            "",
            "─" * 50,
            "",
            f"**Question {next_question['question_number']} of {next_question['total_questions']}:**",
            next_question['question']
        ]
        
        if next_question.get('options'):
            feedback_parts.append("")
            for option in next_question['options']:
                feedback_parts.append(f"  {option}")
        
        return "\n".join(feedback_parts)
    
    def _format_quiz_completion(self, last_answer_result: Dict, final_results: Dict, ended_early: bool = False) -> str:
        """Format the quiz completion message"""
        completion_parts = []
        
        if last_answer_result:
            completion_parts.extend([
                f"{'✅' if last_answer_result['correct'] else '❌'} **Final Answer:**",
                last_answer_result['feedback'],
                "",
                "🎊 **Quiz Complete!** 🎊"
            ])
        elif ended_early:
            completion_parts.append("🛑 **Quiz Ended Early**")
        else:
            completion_parts.append("🎊 **Quiz Complete!** 🎊")
        
        # Add results
        completion_parts.extend([
            "",
            f"📊 **Final Results:**",
            f"• Score: {final_results['score']} out of {final_results['total_questions']}",
            f"• Percentage: {final_results['percentage']}%",
            f"• Duration: {final_results['duration']}",
            f"• Quiz Type: {final_results['quiz_type'].replace('_', ' ').title()}"
        ])
        
        # Performance feedback
        percentage = final_results['percentage']
        if percentage >= 90:
            completion_parts.append("\n🌟 **Excellent work!** You've mastered this topic!")
        elif percentage >= 80:
            completion_parts.append("\n🎯 **Great job!** You have a solid understanding.")
        elif percentage >= 70:
            completion_parts.append("\n📚 **Good effort!** Review the areas you missed.")
        else:
            completion_parts.append("\n💪 **Keep studying!** Practice makes perfect.")
        
        # Areas for improvement
        if final_results.get('areas_for_improvement'):
            completion_parts.extend([
                "",
                "🎯 **Areas to review:**",
                *[f"• {area}" for area in final_results['areas_for_improvement']]
            ])
        
        completion_parts.extend([
            "",
            "💡 **What's next?**",
            "• Ask me questions about topics you missed",
            "• Take another quiz: 'Create a quiz on [topic]'",
            "• Review your analytics: 'Show my quiz performance'"
        ])
        
        return "\n".join(completion_parts)
    
    def get_quiz_analytics(self) -> Dict[str, Any]:
        """Get user's quiz performance analytics"""
        if not self.quiz_generator:
            return {
                'answer': "❌ Quiz analytics not available.",
                'type': 'error',
                'sources': []
            }
        
        analytics = self.quiz_generator.get_analytics()
        
        analytics_text = [
            "📊 **Your Quiz Analytics**",
            "",
            f"🎯 **Overall Performance:**",
            f"• Total Quizzes: {analytics['total_quizzes']}",
            f"• Questions Answered: {analytics['total_questions_answered']}",
            f"• Overall Accuracy: {analytics['overall_accuracy']}%"
        ]
        
        if analytics['topic_performance']:
            analytics_text.extend([
                "",
                "📚 **Performance by Topic:**"
            ])
            for topic, perf in analytics['topic_performance'].items():
                total = perf['correct'] + perf['incorrect']
                accuracy = (perf['correct'] / total * 100) if total > 0 else 0
                analytics_text.append(f"• {topic}: {accuracy:.1f}% ({perf['correct']}/{total})")
        
        if analytics['improvement_suggestions']:
            analytics_text.extend([
                "",
                "💡 **Improvement Suggestions:**",
                *[f"• {suggestion}" for suggestion in analytics['improvement_suggestions']]
            ])
        
        return {
            'answer': "\n".join(analytics_text),
            'type': 'analytics',
            'analytics_data': analytics,
            'sources': []
        }


def main():
    """Interactive demo of the core assistant with quiz capabilities"""
    print("🎓 Core Course Assistant - Q&A and Quiz Generation")
    print("=" * 60)
    
    # Auto-detect subject from content
    assistant = CoreAssistant()
    
    print(assistant.get_welcome_message())
    print(f"🧭 Active Subject: {assistant.subject_info['display_name']}")
    print("\n💡 **What you can do:**")
    print("• Ask any question about your course content")
    print("• Generate quizzes: 'Create a quiz on [topic]'")
    print("• Specify quiz details: 'Give me 5 multiple choice questions about photosynthesis'")
    print("• Check your progress: 'Show my quiz analytics'")
    print("• Type 'quit' to exit")
    print("=" * 60)
    
    # Track active quiz session
    active_quiz = None
    current_question = 0
    
    while True:
        if active_quiz:
            user_input = input(f"🎯 Quiz Answer (Q{current_question + 1}): ").strip()
        else:
            user_input = input("❓ Ask me anything or request a quiz: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            if active_quiz:
                print("\n🛑 Ending quiz session...")
                result = assistant.end_quiz()
                print(result['answer'])
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\n" + "="*80)
        
        # Handle quiz continuation or new requests
        if active_quiz:
            # Continue quiz
            result = assistant.continue_quiz(user_input, active_quiz, current_question)
            
            if result['type'] == 'quiz_continue':
                current_question = result['current_question']
                print("🎯 Quiz Progress:")
                print("-" * 30)
                print(result['answer'])
            elif result['type'] == 'quiz_complete':
                print("🎊 Quiz Results:")
                print("-" * 30)
                print(result['answer'])
                active_quiz = None
                current_question = 0
            else:
                print("❌ Quiz Error:")
                print(result['answer'])
                active_quiz = None
                current_question = 0
                
        else:
            # Handle new request (question or quiz)
            if user_input.lower() in ['show my quiz analytics', 'my analytics', 'quiz stats']:
                result = assistant.get_quiz_analytics()
            else:
                result = assistant.ask_question(user_input)
            
            if result['type'] == 'quiz_start':
                # New quiz started
                active_quiz = result['quiz_session_id']
                current_question = result['current_question']
                print("🎯 New Quiz Started:")
                print("-" * 30)
                print(result['answer'])
                
            elif result['type'] == 'topic_selection':
                print("🎯 Quiz Topic Selection:")
                print("-" * 30)
                print(result['answer'])
                
            elif result['type'] == 'normal_qa':
                # Regular question answered
                print("🤖 Answer:")
                print("-" * 15)
                print(result['answer'])
                
                # Show sources
                if result['sources']:
                    print(f"\n📚 Sources (Confidence: {result['confidence']}):")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"   {i}. {source['source']}")
                        if 'chapter' in source:
                            print(f"      Chapter: {source['chapter']}")
                        if 'lectures' in source:
                            print(f"      Lectures: {source['lectures']}")
                
                # Show related topics
                related = assistant.suggest_related_topics(user_input)
                if related:
                    print(f"\n🔗 Related topics you might want to explore:")
                    for topic in related:
                        print(f"   - {topic}")
                        
            elif result['type'] == 'analytics':
                print("📊 Your Analytics:")
                print("-" * 25)
                print(result['answer'])
                
            else:
                print("🤖 Response:")
                print("-" * 20)
                print(result['answer'])
        
        print("\n" + "="*80)


if __name__ == "__main__":
    main()
