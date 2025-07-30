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
        print("hello")
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
        Analyze this educational content and identify:

        1. SUBJECT AREA: What academic subject/field is this? (e.g., Biology, Chemistry, History, etc.)
        2. MAIN TOPICS: What are the 3-7 main topics covered?
        3. OVERALL DIFFICULTY: Basic, Intermediate, or Advanced level?

        For each main topic, provide:
        - Name of the topic
        - Brief description (1-2 sentences)
        - Key concepts within this topic (3-5 important terms/ideas)
        - Subtopics or specific areas covered
        - Difficulty level (basic/intermediate/advanced)
        - Appropriate question types (definition, process, comparison, application, calculation)

        Content to analyze:
        {content[:8000]}

        Respond in this JSON format:
        {{
            "subject_area": "Biology",
            "overall_difficulty": "intermediate",
            "topics": [
                {{
                    "name": "Topic Name",
                    "description": "Brief description of what this topic covers",
                    "key_concepts": ["concept1", "concept2", "concept3"],
                    "subtopics": ["subtopic1", "subtopic2"],
                    "difficulty_level": "basic",
                    "question_types": ["definition", "process"]
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
        Extract important terms and their definitions from this educational content.
        Look for:
        - Technical terms that are defined or explained
        - Key concepts that students need to understand
        - Important vocabulary specific to this subject

        Content:
        {content[:6000]}

        Respond with a JSON object where keys are terms and values are definitions:
        {{
            "photosynthesis": "The process by which plants convert light energy into chemical energy",
            "ATP": "Adenosine triphosphate, the energy currency of cells"
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
        """Classify the type of educational content"""
        # Check source info first
        if source_info:
            filename = source_info.get('filename', '').lower()
            if 'textbook' in filename or 'chapter' in filename:
                return 'textbook'
            elif 'lecture' in filename or 'notes' in filename:
                return 'lecture_notes'
            elif 'study' in filename or 'guide' in filename:
                return 'study_guide'
            elif 'lab' in filename or 'experiment' in filename:
                return 'lab_manual'
        
        # Analyze content patterns
        content_lower = content.lower()
        
        if 'chapter' in content_lower and 'section' in content_lower:
            return 'textbook'
        elif 'lecture' in content_lower or 'today we will' in content_lower:
            return 'lecture_notes'
        elif 'learning objectives' in content_lower or 'study guide' in content_lower:
            return 'study_guide'
        elif 'procedure' in content_lower and 'materials' in content_lower:
            return 'lab_manual'
        else:
            return 'educational_material'
    
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
        summary = f"📚 **Content Analysis Summary**\n\n"
        summary += f"**Subject Area:** {analysis.subject_area}\n"
        summary += f"**Content Type:** {analysis.content_type}\n"
        summary += f"**Difficulty Level:** {analysis.estimated_difficulty}\n\n"
        
        summary += f"**Main Topics ({len(analysis.main_topics)}):**\n"
        for topic in analysis.main_topics:
            summary += f"- **{topic.name}**: {topic.description}\n"
        
        summary += f"\n**Key Terms:** {len(analysis.key_terms)} terms identified\n"
        summary += f"**Learning Objectives:** {len(analysis.learning_objectives)} objectives generated\n"
        
        return summary
