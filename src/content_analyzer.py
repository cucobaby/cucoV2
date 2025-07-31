"""
Content Analyzer - Dynamic topic discovery from any educational content
Analyzes uploaded materials to extract topics, concepts, and relationships
"""
import os
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TopicInfo:
    """Information about a discovered topic"""
    name: str
    description: str
    key_concepts: List[str]
    subtopics: List[str]
    difficulty_level: str  # 'basic', 'intermediate', 'advanced'
    question_types: List[str]  # 'definition', 'process', 'comparison', 'application'
    prerequisites: List[str]  # Topics that should be understood first

@dataclass
class ContentAnalysis:
    """Complete analysis of educational content"""
    main_topics: List[TopicInfo]
    key_terms: Dict[str, str]  # term -> definition
    relationships: Dict[str, List[str]]  # topic -> related topics
    learning_objectives: List[str]
    content_type: str  # 'textbook', 'lecture_notes', 'study_guide', etc.
    subject_area: str
    estimated_difficulty: str

class ContentAnalyzer:
    """Analyzes any educational content to discover topics and structure"""
    
    def __init__(self):
        # Use same OpenAI initialization pattern as core_assistant.py
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception as e:
            print(f"⚠️ OpenAI initialization failed: {e}")
            print("Content analysis will be limited without OpenAI")
            self.client = None
    
    def analyze_content(self, content_chunks: List[str], source_info: Dict[str, Any] = None) -> ContentAnalysis:
        """
        Analyze educational content to discover topics, concepts, and structure
        
        Args:
            content_chunks: List of text chunks from the content
            source_info: Optional metadata about the source (filename, type, etc.)
        
        Returns:
            ContentAnalysis with discovered topics and structure
        """
        print("🔍 Analyzing content for topics and structure...")
        
        # Combine chunks for analysis (limit to prevent token overflow)
        combined_content = self._prepare_content_for_analysis(content_chunks)
        
        # Step 1: Identify main topics and subject area
        topics_analysis = self._extract_topics(combined_content)
        
        # Step 2: Extract key terms and definitions
        key_terms = self._extract_key_terms(combined_content)
        
        # Step 3: Identify relationships between topics
        relationships = self._analyze_relationships(topics_analysis['topics'], combined_content)
        
        # Step 4: Generate learning objectives
        learning_objectives = self._extract_learning_objectives(combined_content, topics_analysis)
        
        # Step 5: Determine content characteristics
        content_type = self._classify_content_type(combined_content, source_info)
        
        # Build TopicInfo objects
        topic_infos = []
        for topic_data in topics_analysis['topics']:
            topic_info = TopicInfo(
                name=topic_data['name'],
                description=topic_data['description'],
                key_concepts=topic_data['key_concepts'],
                subtopics=topic_data['subtopics'],
                difficulty_level=topic_data['difficulty_level'],
                question_types=topic_data['question_types'],
                prerequisites=topic_data.get('prerequisites', [])
            )
            topic_infos.append(topic_info)
        
        return ContentAnalysis(
            main_topics=topic_infos,
            key_terms=key_terms,
            relationships=relationships,
            learning_objectives=learning_objectives,
            content_type=content_type,
            subject_area=topics_analysis['subject_area'],
            estimated_difficulty=topics_analysis['overall_difficulty']
        )
    
    def _prepare_content_for_analysis(self, content_chunks: List[str], max_tokens: int = 12000) -> str:
        """Prepare content for AI analysis, respecting token limits"""
        combined = " ".join(content_chunks)
        
        # Rough token estimation (1 token ≈ 4 characters)
        if len(combined) > max_tokens * 4:
            # Take first and last portions, plus some middle samples
            start_portion = combined[:max_tokens * 2]
            end_portion = combined[-max_tokens * 2:]
            
            # Sample some middle content
            middle_start = len(combined) // 3
            middle_end = middle_start + max_tokens * 2
            middle_portion = combined[middle_start:middle_end]
            
            combined = f"{start_portion}\n\n... [CONTENT CONTINUES] ...\n\n{middle_portion}\n\n... [CONTENT CONTINUES] ...\n\n{end_portion}"
        
        return combined
    
    def _extract_topics(self, content: str) -> Dict[str, Any]:
        """Extract main topics and subject area from content"""
        if not self.client:
            return self._get_default_analysis()
            
        prompt = f"""
        Analyze this Canvas course content and identify:

        1. SUBJECT AREA: What academic subject/field is this? (e.g., Biology, Chemistry, History, Mathematics, etc.)
        2. MAIN TOPICS: What are the 3-7 main topics covered in this course material?
        3. OVERALL DIFFICULTY: Basic, Intermediate, or Advanced level?

        This content is from a student's Canvas course, so focus on identifying:
        - Course-specific topics that students need to master
        - Key concepts that will likely appear on exams or assignments
        - Skills and knowledge students should gain from this material

        For each main topic, provide:
        - Name of the topic (as it would appear in course materials)
        - Brief description (1-2 sentences explaining what students learn)
        - Key concepts within this topic (3-5 important terms/ideas students must know)
        - Subtopics or specific areas covered in the course
        - Difficulty level (basic/intermediate/advanced) for this course level
        - Appropriate question types for assessment (definition, process, comparison, application, calculation)

        Canvas course content to analyze:
        {content[:8000]}

        Respond in this JSON format:
        {{
            "subject_area": "Biology",
            "overall_difficulty": "intermediate",
            "topics": [
                {{
                    "name": "Cell Structure and Function",
                    "description": "Study of cellular components and how they work together in living organisms",
                    "key_concepts": ["prokaryotic cells", "eukaryotic cells", "organelles", "cell membrane", "nucleus"],
                    "subtopics": ["cell types", "organelle functions", "membrane transport"],
                    "difficulty_level": "intermediate",
                    "question_types": ["definition", "process", "comparison"]
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            
            # Try to parse JSON response
            import json
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return self._parse_fallback_topics(result)
                
        except Exception as e:
            print(f"⚠️ Error in topic extraction: {e}")
            return self._get_default_analysis()
    
    def _extract_key_terms(self, content: str) -> Dict[str, str]:
        """Extract key terms and their definitions"""
        if not self.client:
            return {}
            
        prompt = f"""
        Extract important terms and their definitions from this Canvas course content.
        
        Focus on terms that students need to know for this specific course:
        - Technical terms that are defined or explained in the course material
        - Key vocabulary that will appear on exams, quizzes, or assignments
        - Important concepts specific to this subject area
        - Terms that instructors emphasize or repeat
        - Definitions that students should memorize or understand deeply

        Course content:
        {content[:6000]}

        Respond with a JSON object where keys are terms and values are clear, student-friendly definitions:
        {{
            "photosynthesis": "The process by which plants convert light energy into chemical energy (glucose) using carbon dioxide and water",
            "mitochondria": "The powerhouse organelles of cells that produce ATP energy through cellular respiration",
            "ATP": "Adenosine triphosphate - the primary energy currency used by all living cells"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
            
        except Exception as e:
            print(f"⚠️ Error extracting key terms: {e}")
            return {}
    
    def _analyze_relationships(self, topics: List[Dict], content: str) -> Dict[str, List[str]]:
        """Analyze relationships between topics"""
        if not self.client or not topics:
            return {}
            
        topic_names = [topic['name'] for topic in topics]
        
        prompt = f"""
        Given these topics from educational content: {topic_names}
        
        Analyze how they relate to each other. For each topic, identify which other topics:
        - Are prerequisites (must be understood first)
        - Are closely related or connected
        - Build upon or extend the concept
        
        Content context:
        {content[:4000]}
        
        Respond in JSON format:
        {{
            "Topic A": ["related_topic1", "related_topic2"],
            "Topic B": ["prerequisite_topic", "related_topic"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
            
        except Exception as e:
            print(f"⚠️ Error analyzing relationships: {e}")
            return {}
    
    def _extract_learning_objectives(self, content: str, topics_analysis: Dict) -> List[str]:
        """Extract or generate learning objectives"""
        if not self.client:
            return []
            
        prompt = f"""
        Based on this educational content about {topics_analysis.get('subject_area', 'various topics')}, 
        generate 5-8 clear learning objectives that students should achieve.
        
        Learning objectives should:
        - Start with action verbs (explain, analyze, compare, calculate, etc.)
        - Be specific and measurable
        - Cover different cognitive levels (remember, understand, apply, analyze)
        
        Topics covered: {[t['name'] for t in topics_analysis.get('topics', [])]}
        
        Content sample:
        {content[:4000]}
        
        Format as a simple list:
        - Explain the process of photosynthesis
        - Compare aerobic and anaerobic respiration
        - Calculate ATP yield from glucose metabolism
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            
            result = response.choices[0].message.content
            # Parse the list
            objectives = []
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    objectives.append(line[1:].strip())
                elif line and not line.startswith('#'):
                    objectives.append(line)
            
            return objectives[:10]  # Limit to 10 objectives
            
        except Exception as e:
            print(f"⚠️ Error extracting learning objectives: {e}")
            return []
    
    def _classify_content_type(self, content: str, source_info: Dict = None) -> str:
        """Classify the type of educational content with Canvas-specific awareness"""
        # Check Canvas-specific source info first
        if source_info:
            filename = source_info.get('filename', '').lower()
            url = source_info.get('url', '').lower()
            course_id = source_info.get('course_id', '').lower()
            
            # Canvas-specific content type detection
            if 'pages' in url or 'page' in filename:
                return 'canvas_page'
            elif 'assignments' in url or 'assignment' in filename:
                return 'canvas_assignment'
            elif 'modules' in url or 'module' in filename:
                return 'canvas_module'
            elif 'announcements' in url or 'announcement' in filename:
                return 'canvas_announcement' 
            elif 'discussions' in url or 'discussion' in filename:
                return 'canvas_discussion'
            elif 'files' in url or any(ext in filename for ext in ['.pdf', '.docx', '.pptx']):
                return 'canvas_file'
            elif 'syllabus' in url or 'syllabus' in filename:
                return 'canvas_syllabus'
            elif 'quiz' in url or 'quiz' in filename:
                return 'canvas_quiz'
            
            # Traditional academic content types
            if 'textbook' in filename or 'chapter' in filename:
                return 'textbook'
            elif 'lecture' in filename or 'notes' in filename:
                return 'lecture_notes'
            elif 'study' in filename or 'guide' in filename:
                return 'study_guide'
            elif 'lab' in filename or 'experiment' in filename:
                return 'lab_manual'
        
        # Analyze content patterns with Canvas awareness
        content_lower = content.lower()
        
        # Canvas-specific content patterns
        if any(pattern in content_lower for pattern in ['assignment instructions', 'due date', 'submit']):
            return 'canvas_assignment'
        elif any(pattern in content_lower for pattern in ['discussion prompt', 'reply to', 'post']):
            return 'canvas_discussion'
        elif any(pattern in content_lower for pattern in ['syllabus', 'course schedule', 'grading policy']):
            return 'canvas_syllabus'
        elif any(pattern in content_lower for pattern in ['announcement', 'important notice']):
            return 'canvas_announcement'
        
        # Traditional academic patterns
        elif 'chapter' in content_lower and 'section' in content_lower:
            return 'textbook'
        elif 'lecture' in content_lower or 'today we will' in content_lower:
            return 'lecture_notes'
        elif 'learning objectives' in content_lower or 'study guide' in content_lower:
            return 'study_guide'
        elif 'procedure' in content_lower and 'materials' in content_lower:
            return 'lab_manual'
        else:
            return 'canvas_material'  # Default for Canvas content
    
    def _parse_fallback_topics(self, text: str) -> Dict[str, Any]:
        """Fallback parser if JSON parsing fails"""
        return {
            "subject_area": "General Studies",
            "overall_difficulty": "intermediate",
            "topics": [{
                "name": "General Topic",
                "description": "Educational content requiring analysis",
                "key_concepts": ["concept"],
                "subtopics": ["subtopic"],
                "difficulty_level": "intermediate",
                "question_types": ["definition", "application"]
            }]
        }
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Default analysis if everything fails"""
        return {
            "subject_area": "General Studies",
            "overall_difficulty": "intermediate",
            "topics": []
        }

    def get_topic_summary(self, analysis: ContentAnalysis) -> str:
        """Generate a human-readable summary of the content analysis"""
        summary = f"📚 **Canvas Content Analysis Summary**\n\n"
        summary += f"**Subject Area:** {analysis.subject_area}\n"
        summary += f"**Content Type:** {analysis.content_type}\n"
        summary += f"**Difficulty Level:** {analysis.estimated_difficulty}\n\n"
        
        summary += f"**Main Topics ({len(analysis.main_topics)}):**\n"
        for topic in analysis.main_topics:
            summary += f"- **{topic.name}**: {topic.description}\n"
        
        summary += f"\n**Key Terms:** {len(analysis.key_terms)} terms identified\n"
        summary += f"**Learning Objectives:** {len(analysis.learning_objectives)} objectives generated\n"
        
        return summary

    def get_course_study_guide(self, analysis: ContentAnalysis) -> str:
        """Generate a Canvas course-specific study guide from the analysis"""
        if not analysis.main_topics:
            return "No topics identified for study guide generation."
            
        study_guide = f"📖 **Study Guide: {analysis.subject_area}**\n\n"
        
        # Course Overview
        study_guide += f"**Course Material Type:** {analysis.content_type.replace('_', ' ').title()}\n"
        study_guide += f"**Difficulty Level:** {analysis.estimated_difficulty.title()}\n\n"
        
        # Learning Objectives
        if analysis.learning_objectives:
            study_guide += "**🎯 Learning Objectives:**\n"
            for i, objective in enumerate(analysis.learning_objectives[:5], 1):
                study_guide += f"{i}. {objective}\n"
            study_guide += "\n"
        
        # Main Topics Breakdown
        study_guide += "**📚 Topic Breakdown:**\n\n"
        for i, topic in enumerate(analysis.main_topics, 1):
            study_guide += f"**{i}. {topic.name}** ({topic.difficulty_level})\n"
            study_guide += f"   {topic.description}\n\n"
            
            if topic.key_concepts:
                study_guide += f"   **Key Concepts:**\n"
                for concept in topic.key_concepts:
                    study_guide += f"   • {concept}\n"
                study_guide += "\n"
            
            if topic.subtopics:
                study_guide += f"   **Subtopics:** {', '.join(topic.subtopics)}\n\n"
        
        # Key Terms Section
        if analysis.key_terms:
            study_guide += "**📝 Important Terms to Know:**\n"
            for term, definition in list(analysis.key_terms.items())[:10]:  # Top 10 terms
                study_guide += f"• **{term}**: {definition}\n"
            study_guide += "\n"
        
        # Study Tips
        study_guide += "**💡 Study Tips for This Content:**\n"
        if analysis.estimated_difficulty == "basic":
            study_guide += "• Focus on definitions and basic understanding\n"
            study_guide += "• Practice identifying key terms and concepts\n"
        elif analysis.estimated_difficulty == "intermediate":
            study_guide += "• Understand relationships between concepts\n"
            study_guide += "• Practice applying knowledge to new situations\n"
        else:  # advanced
            study_guide += "• Analyze complex relationships and processes\n"
            study_guide += "• Synthesize information across multiple topics\n"
        
        return study_guide
