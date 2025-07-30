"""
Generic Subject Configuration
Base configuration for any educational subject - provides fallback behavior
"""
from typing import Dict, List, Any

class GenericConfig:
    """
    Generic configuration that works for any educational subject
    Serves as base class and fallback when no specific subject is detected
    """
    
    @staticmethod
    def get_subject_info() -> Dict[str, str]:
        """Return basic subject information"""
        return {
            'name': 'generic',
            'display_name': 'General Studies',
            'description': 'Generic educational content assistant',
            'version': '1.0'
        }
    
    @staticmethod
    def get_system_prompt() -> str:
        """Return the system prompt for AI interactions"""
        return """You are a helpful educational tutor assistant. Use the provided course content to answer the student's question accurately and clearly.

Guidelines:
- Base your answer primarily on the provided course content
- Be educational and explain concepts clearly
- If the content doesn't fully answer the question, say so
- Include specific details from the course materials when relevant
- Keep answers concise but thorough
- Use bullet points or numbered lists when helpful for clarity
- Adapt your language to the subject matter and student level"""
    
    @staticmethod
    def get_topic_keywords() -> Dict[str, List[str]]:
        """Return generic topic keywords and related concepts"""
        return {
            'concept': ['idea', 'theory', 'principle', 'notion'],
            'process': ['procedure', 'method', 'steps', 'workflow'],
            'analysis': ['examination', 'evaluation', 'assessment', 'study'],
            'comparison': ['contrast', 'difference', 'similarity', 'versus'],
            'application': ['implementation', 'usage', 'practice', 'example'],
            'definition': ['meaning', 'explanation', 'description', 'term'],
            'relationship': ['connection', 'link', 'association', 'correlation'],
            'cause': ['reason', 'factor', 'source', 'origin'],
            'effect': ['result', 'outcome', 'consequence', 'impact'],
            'system': ['structure', 'organization', 'framework', 'model']
        }
    
    @staticmethod
    def detect_subject_keywords() -> List[str]:
        """Return keywords that might indicate this is generic educational content"""
        return [
            'study', 'learn', 'education', 'course', 'lesson', 'chapter',
            'concept', 'theory', 'principle', 'method', 'analysis',
            'example', 'definition', 'explanation', 'understanding'
        ]
    
    @staticmethod
    def get_welcome_message() -> str:
        """Return welcome message for this subject"""
        return """
🎓 Welcome to the Generic Educational Assistant!

I can help you with questions about your course material across any subject.
I'll analyze your content and provide helpful answers based on what you've studied.

Features:
• Answer questions using your course materials
• Suggest related topics for further study  
• Generate quizzes from your content
• Analyze and summarize educational material

Ask me anything about your coursework!
        """.strip()
    
    @staticmethod
    def get_question_types() -> List[str]:
        """Return appropriate question types for this subject"""
        return [
            'definition',
            'explanation', 
            'comparison',
            'analysis',
            'application',
            'synthesis'
        ]
    
    @staticmethod
    def get_difficulty_indicators() -> Dict[str, List[str]]:
        """Return keywords that indicate content difficulty"""
        return {
            'basic': [
                'introduction', 'basic', 'fundamental', 'overview',
                'simple', 'elementary', 'beginning', 'foundation'
            ],
            'intermediate': [
                'detailed', 'analysis', 'comparison', 'relationship',
                'application', 'method', 'process', 'mechanism'
            ],
            'advanced': [
                'complex', 'synthesis', 'evaluation', 'critical',
                'advanced', 'sophisticated', 'comprehensive', 'theoretical'
            ]
        }
