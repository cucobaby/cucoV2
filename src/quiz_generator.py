"""
Quiz Generator - Creates quizzes from discovered content topics
Uses AI to generate contextually relevant questions from course materials
"""
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import openai
from dotenv import load_dotenv

load_dotenv()

class QuestionType(Enum):
    DEFINITION = "definition"
    PROCESS = "process" 
    COMPARISON = "comparison"
    APPLICATION = "application"
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

class DifficultyLevel(Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class QuizQuestion:
    """Represents a single quiz question"""
    question_id: str
    question_type: QuestionType
    question_text: str
    correct_answer: str
    explanation: str
    difficulty: DifficultyLevel
    source_material: str
    source_section: str
    points: int = 1
    
    # Optional fields for different question types
    multiple_choice_options: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    estimated_time_minutes: Optional[int] = None

@dataclass
class Quiz:
    """Represents a complete quiz"""
    quiz_id: str
    title: str
    topic: str
    questions: List[QuizQuestion]
    total_points: int
    estimated_time_minutes: int
    difficulty_level: DifficultyLevel
    created_from_sources: List[str]
    instructions: str

class QuizGenerator:
    """
    Generates quizzes from course content using AI
    Uses content analysis to create contextually relevant questions
    """
    
    def __init__(self):
        """Initialize the quiz generator"""
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.ai_enabled = True
        except Exception as e:
            print(f"⚠️ OpenAI not available: {e}")
            self.ai_enabled = False
            self.client = None
        
        # Default question type distributions
        self.default_question_mix = {
            QuestionType.DEFINITION: 0.3,
            QuestionType.PROCESS: 0.4,
            QuestionType.COMPARISON: 0.2,
            QuestionType.APPLICATION: 0.1
        }
        
        # Question type prompts
        self.question_prompts = {
            QuestionType.DEFINITION: self._get_definition_prompt,
            QuestionType.PROCESS: self._get_process_prompt,
            QuestionType.COMPARISON: self._get_comparison_prompt,
            QuestionType.APPLICATION: self._get_application_prompt
        }
    
    def generate_quiz(self, 
                     topic: str,
                     content_chunks: List[Dict[str, Any]],
                     num_questions: int = 10,
                     question_types: Optional[List[QuestionType]] = None,
                     difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> Quiz:
        """
        Generate a quiz on a specific topic using content analysis
        
        Args:
            topic: The topic name (e.g., "Photosynthesis")
            content_chunks: Relevant content from ChromaDB search
            num_questions: Number of questions to generate
            question_types: Specific question types to include
            difficulty: Target difficulty level
            
        Returns:
            Complete Quiz object with questions and metadata
        """
        if not self.ai_enabled:
            return self._generate_fallback_quiz(topic, content_chunks, num_questions)
        
        print(f"🎯 Generating {num_questions}-question quiz on '{topic}'")
        
        # Step 1: Analyze content for question opportunities
        question_opportunities = self._analyze_content_for_questions(topic, content_chunks)
        
        # Step 2: Determine question type distribution
        question_distribution = self._plan_question_distribution(
            num_questions, question_types, question_opportunities
        )
        
        # Step 3: Generate questions
        questions = []
        for question_type, count in question_distribution.items():
            for i in range(count):
                question = self._generate_question(
                    topic, content_chunks, question_type, difficulty, question_opportunities
                )
                if question:
                    questions.append(question)
        
        # Step 4: Create quiz metadata
        quiz = Quiz(
            quiz_id=f"quiz_{topic.lower().replace(' ', '_')}_{len(questions)}q",
            title=f"{topic} Quiz",
            topic=topic,
            questions=questions,
            total_points=sum(q.points for q in questions),
            estimated_time_minutes=self._estimate_quiz_time(questions),
            difficulty_level=difficulty,
            created_from_sources=list(set(chunk['source'] for chunk in content_chunks)),
            instructions=f"Quiz covering key concepts in {topic}. Answer all questions based on course material."
        )
        
        print(f"✅ Generated quiz with {len(questions)} questions")
        return quiz
    
    def _analyze_content_for_questions(self, topic: str, content_chunks: List[Dict]) -> Dict[str, Any]:
        """Analyze content to identify what types of questions are possible"""
        
        # Extract key concepts mentioned in content
        all_content = " ".join([chunk['content'] for chunk in content_chunks])
        
        if not self.client:
            return {"concepts": [], "processes": [], "comparisons": []}
        
        prompt = f"""
        Analyze this educational content about {topic} and identify:
        
        1. KEY CONCEPTS that can be defined or explained
        2. PROCESSES or procedures that can be described step-by-step  
        3. RELATIONSHIPS or comparisons that can be made
        4. APPLICATIONS or calculations that can be performed
        
        Content:
        {all_content[:4000]}
        
        Respond in JSON format:
        {{
            "concepts": ["concept1", "concept2"],
            "processes": ["process1", "process2"], 
            "comparisons": ["item1 vs item2"],
            "applications": ["calculation type", "practical application"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"⚠️ Content analysis failed: {e}")
            return {"concepts": [], "processes": [], "comparisons": [], "applications": []}
    
    def _plan_question_distribution(self, 
                                  num_questions: int, 
                                  requested_types: Optional[List[QuestionType]],
                                  opportunities: Dict[str, Any]) -> Dict[QuestionType, int]:
        """Plan how many questions of each type to generate"""
        
        if requested_types:
            # Use requested distribution
            questions_per_type = num_questions // len(requested_types)
            remainder = num_questions % len(requested_types)
            
            distribution = {}
            for i, qtype in enumerate(requested_types):
                distribution[qtype] = questions_per_type + (1 if i < remainder else 0)
            
            return distribution
        
        # Use default distribution based on available content
        distribution = {}
        
        # Adjust distribution based on content opportunities
        available_concepts = len(opportunities.get('concepts', []))
        available_processes = len(opportunities.get('processes', []))
        available_comparisons = len(opportunities.get('comparisons', []))
        available_applications = len(opportunities.get('applications', []))
        
        # Calculate proportional distribution
        total_opportunities = available_concepts + available_processes + available_comparisons + available_applications
        
        if total_opportunities > 0:
            distribution[QuestionType.DEFINITION] = max(1, int(num_questions * available_concepts / total_opportunities))
            distribution[QuestionType.PROCESS] = max(1, int(num_questions * available_processes / total_opportunities))
            distribution[QuestionType.COMPARISON] = int(num_questions * available_comparisons / total_opportunities)
            distribution[QuestionType.APPLICATION] = int(num_questions * available_applications / total_opportunities)
            
            # Ensure we have the right total
            current_total = sum(distribution.values())
            if current_total < num_questions:
                # Add remaining to the most available type
                if available_concepts >= available_processes:
                    distribution[QuestionType.DEFINITION] += num_questions - current_total
                else:
                    distribution[QuestionType.PROCESS] += num_questions - current_total
        else:
            # Fallback to default distribution
            distribution[QuestionType.DEFINITION] = max(1, int(num_questions * 0.4))
            distribution[QuestionType.PROCESS] = max(1, int(num_questions * 0.4))
            distribution[QuestionType.COMPARISON] = int(num_questions * 0.2)
            
            # Ensure total is correct
            current_total = sum(distribution.values())
            if current_total < num_questions:
                distribution[QuestionType.DEFINITION] += num_questions - current_total
        
        return {k: v for k, v in distribution.items() if v > 0}
    
    def _generate_question(self, 
                          topic: str,
                          content_chunks: List[Dict],
                          question_type: QuestionType,
                          difficulty: DifficultyLevel,
                          opportunities: Dict[str, Any]) -> Optional[QuizQuestion]:
        """Generate a single question of the specified type"""
        
        if not self.client:
            return None
        
        # Get appropriate prompt for question type
        prompt_func = self.question_prompts.get(question_type)
        if not prompt_func:
            return None
        
        prompt = prompt_func(topic, content_chunks, difficulty, opportunities)
        
        try:
            print(f"🤖 Making OpenAI API call for {question_type.value} question...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=500  # Add token limit
            )
            
            print(f"✅ OpenAI API response received")
            
            # Parse the response into a QuizQuestion
            question_data = self._parse_question_response(response.choices[0].message.content, question_type, difficulty)
            
            if question_data:
                print(f"✅ Question data parsed successfully")
                return QuizQuestion(
                    question_id=f"q_{len(content_chunks)}_{question_type.value}",
                    question_type=question_type,
                    question_text=question_data['question'],
                    correct_answer=question_data['answer'],
                    explanation=question_data.get('explanation', 'No explanation provided'),
                    difficulty=difficulty,
                    source_material=question_data.get('source', 'Course Content'),
                    source_section=question_data.get('section', 'Multiple Sources'),
                    multiple_choice_options=question_data.get('options'),
                    keywords=question_data.get('keywords'),
                    estimated_time_minutes=question_data.get('time_estimate', 2)
                )
            else:
                print(f"❌ Failed to parse question data")
            
        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a fallback question instead of None
            return QuizQuestion(
                question_id=f"fallback_{question_type.value}",
                question_type=question_type,
                question_text=f"Explain the key concepts of {topic} as they relate to {question_type.value}.",
                correct_answer=f"Review course materials about {topic} to understand the {question_type.value} aspects.",
                explanation="This is a fallback question generated when AI was unavailable.",
                difficulty=difficulty,
                source_material="Course Content",
                source_section="General Review"
            )
    
    def _get_definition_prompt(self, topic: str, content_chunks: List[Dict], difficulty: DifficultyLevel, opportunities: Dict) -> str:
        """Generate prompt for definition questions"""
        content_sample = " ".join([chunk['content'][:500] for chunk in content_chunks[:3]])
        concepts = opportunities.get('concepts', ['key concept'])
        
        return f"""
        Based on this course content about {topic}:
        
        {content_sample}
        
        Generate 1 definition question about one of these concepts: {', '.join(concepts[:3])}
        
        Requirements:
        - {difficulty.value} difficulty level
        - Question should test understanding of the concept
        - Answer should be definitive and based on the provided content
        - Include brief explanation
        
        Respond in JSON format:
        {{
            "question": "What is [concept]?",
            "answer": "Brief, accurate definition",
            "explanation": "Why this answer is correct based on course content",
            "source": "Source material reference",
            "keywords": ["keyword1", "keyword2"]
        }}
        """
    
    def _get_process_prompt(self, topic: str, content_chunks: List[Dict], difficulty: DifficultyLevel, opportunities: Dict) -> str:
        """Generate prompt for process questions"""
        content_sample = " ".join([chunk['content'][:500] for chunk in content_chunks[:3]])
        processes = opportunities.get('processes', ['key process'])
        
        return f"""
        Based on this course content about {topic}:
        
        {content_sample}
        
        Generate 1 process question about: {', '.join(processes[:2])}
        
        Requirements:
        - {difficulty.value} difficulty level
        - Question should test understanding of steps or mechanisms
        - Answer should describe the process clearly
        - Include explanation of why each step matters
        
        Respond in JSON format:
        {{
            "question": "Describe the process of [process name]",
            "answer": "Step-by-step description of the process",
            "explanation": "Why understanding this process is important",
            "source": "Source material reference"
        }}
        """
    
    def _get_comparison_prompt(self, topic: str, content_chunks: List[Dict], difficulty: DifficultyLevel, opportunities: Dict) -> str:
        """Generate prompt for comparison questions"""
        content_sample = " ".join([chunk['content'][:500] for chunk in content_chunks[:3]])
        comparisons = opportunities.get('comparisons', ['concept A vs concept B'])
        
        return f"""
        Based on this course content about {topic}:
        
        {content_sample}
        
        Generate 1 comparison question about: {', '.join(comparisons[:2])}
        
        Requirements:
        - {difficulty.value} difficulty level
        - Question should contrast two related concepts/processes
        - Answer should highlight key differences and similarities
        - Include explanation of significance
        
        Respond in JSON format:
        {{
            "question": "Compare and contrast [item1] and [item2]",
            "answer": "Key differences and similarities",
            "explanation": "Why this comparison is important to understand",
            "source": "Source material reference"
        }}
        """
    
    def _get_application_prompt(self, topic: str, content_chunks: List[Dict], difficulty: DifficultyLevel, opportunities: Dict) -> str:
        """Generate prompt for application questions"""
        content_sample = " ".join([chunk['content'][:500] for chunk in content_chunks[:3]])
        applications = opportunities.get('applications', ['practical application'])
        
        return f"""
        Based on this course content about {topic}:
        
        {content_sample}
        
        Generate 1 application question about: {', '.join(applications[:2])}
        
        Requirements:
        - {difficulty.value} difficulty level
        - Question should require applying concepts to solve problems
        - Answer should show step-by-step solution
        - Include explanation of underlying principles
        
        Respond in JSON format:
        {{
            "question": "Apply [concept] to solve: [problem scenario]",
            "answer": "Step-by-step solution",
            "explanation": "Why this approach works and what principles apply",
            "source": "Source material reference"
        }}
        """
    
    def _parse_question_response(self, response: str, question_type: QuestionType, difficulty: DifficultyLevel) -> Optional[Dict]:
        """Parse AI response into structured question data"""
        try:
            print(f"📝 Parsing response: {response[:100]}...")
            # Try to parse as JSON
            parsed = json.loads(response)
            print(f"✅ JSON parsing successful")
            return parsed
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📝 Raw response: {response}")
            
            # Try to extract key information manually
            try:
                # Simple fallback parsing
                lines = response.strip().split('\n')
                question = "Generated question (parsing failed)"
                answer = "Generated answer"
                explanation = "Generated explanation"
                
                for line in lines:
                    if 'question' in line.lower() and ':' in line:
                        question = line.split(':', 1)[1].strip().strip('"')
                    elif 'answer' in line.lower() and ':' in line:
                        answer = line.split(':', 1)[1].strip().strip('"')
                    elif 'explanation' in line.lower() and ':' in line:
                        explanation = line.split(':', 1)[1].strip().strip('"')
                
                return {
                    "question": question,
                    "answer": answer,
                    "explanation": explanation,
                    "source": "Course Content"
                }
            except Exception as fallback_error:
                print(f"❌ Fallback parsing also failed: {fallback_error}")
                
                # Final fallback
                return {
                    "question": f"What are the key concepts of {question_type.value} related to this topic?",
                    "answer": "Review the course materials for detailed information.",
                    "explanation": "This question was generated as a fallback.",
                    "source": "Course Content"
                }
    
    def _estimate_quiz_time(self, questions: List[QuizQuestion]) -> int:
        """Estimate time needed to complete the quiz"""
        time_per_type = {
            QuestionType.DEFINITION: 2,
            QuestionType.PROCESS: 4,
            QuestionType.COMPARISON: 6,
            QuestionType.APPLICATION: 8
        }
        
        total_time = sum(time_per_type.get(q.question_type, 3) for q in questions)
        return max(total_time, 5)  # Minimum 5 minutes
    
    def _generate_fallback_quiz(self, topic: str, content_chunks: List[Dict], num_questions: int) -> Quiz:
        """Generate a basic quiz when AI is not available"""
        questions = []
        
        for i in range(min(num_questions, len(content_chunks))):
            chunk = content_chunks[i]
            question = QuizQuestion(
                question_id=f"fallback_q_{i}",
                question_type=QuestionType.DEFINITION,
                question_text=f"Based on the content from {chunk['source']}, explain the key concepts related to {topic}.",
                correct_answer="Refer to course materials for detailed explanation.",
                explanation="This question requires reviewing the source material.",
                difficulty=DifficultyLevel.INTERMEDIATE,
                source_material=chunk['source'],
                source_section=chunk.get('section_title', 'Content Section')
            )
            questions.append(question)
        
        return Quiz(
            quiz_id=f"fallback_quiz_{topic.lower().replace(' ', '_')}",
            title=f"{topic} Review Quiz",
            topic=topic,
            questions=questions,
            total_points=len(questions),
            estimated_time_minutes=len(questions) * 3,
            difficulty_level=DifficultyLevel.INTERMEDIATE,
            created_from_sources=[chunk['source'] for chunk in content_chunks],
            instructions="Review quiz - refer to course materials for answers."
        )
    
    def export_quiz(self, quiz: Quiz, format_type: str = "json") -> str:
        """Export quiz in various formats"""
        if format_type == "json":
            return self._export_json(quiz)
        elif format_type == "text":
            return self._export_text(quiz)
        else:
            return self._export_json(quiz)
    
    def _export_json(self, quiz: Quiz) -> str:
        """Export quiz as JSON"""
        quiz_dict = {
            "quiz_id": quiz.quiz_id,
            "title": quiz.title,
            "topic": quiz.topic,
            "total_points": quiz.total_points,
            "estimated_time_minutes": quiz.estimated_time_minutes,
            "difficulty": quiz.difficulty_level.value,
            "instructions": quiz.instructions,
            "questions": [
                {
                    "id": q.question_id,
                    "type": q.question_type.value,
                    "question": q.question_text,
                    "answer": q.correct_answer,
                    "explanation": q.explanation,
                    "source": q.source_material,
                    "points": q.points,
                    "options": q.multiple_choice_options
                }
                for q in quiz.questions
            ]
        }
        return json.dumps(quiz_dict, indent=2)
    
    def _export_text(self, quiz: Quiz) -> str:
        """Export quiz as formatted text"""
        output = []
        output.append(f"# {quiz.title}")
        output.append(f"**Topic:** {quiz.topic}")
        output.append(f"**Time:** {quiz.estimated_time_minutes} minutes")
        output.append(f"**Points:** {quiz.total_points}")
        output.append(f"\n{quiz.instructions}\n")
        
        for i, question in enumerate(quiz.questions, 1):
            output.append(f"## Question {i} ({question.points} point{'s' if question.points != 1 else ''})")
            output.append(f"{question.question_text}")
            
            if question.multiple_choice_options:
                for j, option in enumerate(question.multiple_choice_options, ord('A')):
                    output.append(f"{chr(j)}) {option}")
            
            output.append(f"\n**Answer:** {question.correct_answer}")
            output.append(f"**Explanation:** {question.explanation}")
            output.append(f"**Source:** {question.source_material}")
            output.append("")
        
        return "\n".join(output)
