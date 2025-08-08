"""
Advanced Quiz Generator for Educational AI Assistant
Features:
- Multiple choice and fill-in-the-blank questions
- Configurable quiz length
- Content selection from knowledge base or direct queries
- Intelligent feedback with explanations
- Wrong answer tracking and analytics
- Standard quiz and flashcard formats
"""

import json
import random
import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import openai
import os


class QuizType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    MIXED = "mixed"


class QuizFormat(Enum):
    STANDARD = "standard"
    FLASHCARD = "flashcard"


@dataclass
class Question:
    """Represents a single quiz question"""
    id: str
    type: QuizType
    question: str
    correct_answer: str
    options: Optional[List[str]] = None  # For multiple choice
    explanation: str = ""
    topic: str = ""
    difficulty: str = "medium"
    created_at: str = ""


@dataclass
class QuizAttempt:
    """Represents a user's attempt at answering a question"""
    question_id: str
    user_answer: str
    is_correct: bool
    timestamp: str
    feedback_given: str = ""


@dataclass
class QuizSession:
    """Represents a complete quiz session"""
    session_id: str
    quiz_type: QuizType
    quiz_format: QuizFormat
    questions: List[Question]
    attempts: List[QuizAttempt]
    score: int = 0
    total_questions: int = 0
    started_at: str = ""
    completed_at: str = ""


class QuizGenerator:
    """Advanced quiz generator with AI-powered question creation and analytics"""
    
    def __init__(self, api_key: str = None, storage_path: str = "quiz_data.json"):
        """Initialize the quiz generator"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.storage_path = storage_path
        self.user_analytics = self._load_analytics()
        self.current_session: Optional[QuizSession] = None
    
    def _load_analytics(self) -> Dict:
        """Load user analytics and quiz history"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading analytics: {e}")
        
        return {
            "quiz_sessions": [],
            "wrong_answers": [],
            "topic_performance": {},
            "question_bank": []
        }
    
    def _save_analytics(self):
        """Save user analytics and quiz history"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_analytics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving analytics: {e}")
    
    def create_quiz(self, 
                   content_source: str,
                   quiz_length: int = 5,
                   quiz_type: QuizType = QuizType.MIXED,
                   quiz_format: QuizFormat = QuizFormat.STANDARD,
                   difficulty: str = "medium",
                   use_knowledge_base: bool = False) -> QuizSession:
        """
        Create a new quiz session
        
        Args:
            content_source: Either direct content/topic or knowledge base query
            quiz_length: Number of questions to generate
            quiz_type: Type of questions (multiple choice, fill-in-blank, or mixed)
            quiz_format: Display format (standard or flashcard)
            difficulty: Question difficulty level
            use_knowledge_base: Whether to use existing knowledge base content
        """
        
        print(f"🎯 Creating {quiz_type.value} quiz with {quiz_length} questions...")
        
        # Generate questions based on content source
        if use_knowledge_base:
            questions = self._generate_from_knowledge_base(content_source, quiz_length, quiz_type, difficulty)
        else:
            questions = self._generate_from_topic(content_source, quiz_length, quiz_type, difficulty)
        
        # Create quiz session
        session_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session = QuizSession(
            session_id=session_id,
            quiz_type=quiz_type,
            quiz_format=quiz_format,
            questions=questions,
            attempts=[],
            total_questions=len(questions),
            started_at=datetime.now().isoformat()
        )
        
        return self.current_session
    
    def _generate_from_topic(self, topic: str, num_questions: int, quiz_type: QuizType, difficulty: str) -> List[Question]:
        """Generate questions from a topic using AI"""
        
        questions = []
        
        # Determine question types to generate
        if quiz_type == QuizType.MIXED:
            mc_count = num_questions // 2
            fib_count = num_questions - mc_count
            question_types = [QuizType.MULTIPLE_CHOICE] * mc_count + [QuizType.FILL_IN_BLANK] * fib_count
            random.shuffle(question_types)
        else:
            question_types = [quiz_type] * num_questions
        
        for i, q_type in enumerate(question_types):
            try:
                question = self._generate_single_question(topic, q_type, difficulty, i + 1)
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating question {i + 1}: {e}")
        
        return questions
    
    def _generate_single_question(self, topic: str, question_type: QuizType, difficulty: str, question_num: int) -> Optional[Question]:
        """Generate a single question using AI"""
        
        if question_type == QuizType.MULTIPLE_CHOICE:
            prompt = f"""
            Create a {difficulty} difficulty multiple choice question about: {topic}
            
            Format your response as JSON:
            {{
                "question": "Your question here",
                "correct_answer": "A",
                "options": [
                    "A) Correct answer",
                    "B) Wrong answer 1", 
                    "C) Wrong answer 2",
                    "D) Wrong answer 3"
                ],
                "explanation": "Detailed explanation of why the correct answer is right and why the others are wrong"
            }}
            
            Make sure the question is educational and the explanation is thorough.
            """
        else:  # Fill in the blank
            prompt = f"""
            Create a {difficulty} difficulty fill-in-the-blank question about: {topic}
            
            Format your response as JSON:
            {{
                "question": "Your question with a _____ blank to fill",
                "correct_answer": "the correct word/phrase",
                "explanation": "Detailed explanation of the answer and why it's important"
            }}
            
            Make the blank meaningful and educational.
            """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Generate high-quality quiz questions with detailed explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                question_data = json.loads(json_match.group())
                
                question_id = f"q_{question_num}_{datetime.now().strftime('%H%M%S')}"
                
                return Question(
                    id=question_id,
                    type=question_type,
                    question=question_data["question"],
                    correct_answer=question_data["correct_answer"],
                    options=question_data.get("options"),
                    explanation=question_data["explanation"],
                    topic=topic,
                    difficulty=difficulty,
                    created_at=datetime.now().isoformat()
                )
        
        except Exception as e:
            print(f"Error generating question: {e}")
            return None
    
    def _generate_from_knowledge_base(self, query: str, num_questions: int, quiz_type: QuizType, difficulty: str) -> List[Question]:
        """Generate questions from knowledge base content"""
        # This would integrate with your existing knowledge base
        # For now, treating it as a topic-based generation
        print(f"📚 Searching knowledge base for: {query}")
        
        # TODO: Integrate with actual knowledge base retrieval
        # For now, use topic-based generation
        return self._generate_from_topic(query, num_questions, quiz_type, difficulty)
    
    def present_question(self, question_index: int = 0) -> Dict:
        """Present a question in the chosen format"""
        if not self.current_session or question_index >= len(self.current_session.questions):
            return {"error": "No valid question to present"}
        
        question = self.current_session.questions[question_index]
        
        if self.current_session.quiz_format == QuizFormat.FLASHCARD:
            return self._present_flashcard(question, question_index)
        else:
            return self._present_standard_question(question, question_index)
    
    def _present_standard_question(self, question: Question, index: int) -> Dict:
        """Present question in standard quiz format"""
        presentation = {
            "format": "standard",
            "question_number": index + 1,
            "total_questions": self.current_session.total_questions,
            "question": question.question,
            "type": question.type.value,
            "difficulty": question.difficulty,
            "topic": question.topic
        }
        
        if question.type == QuizType.MULTIPLE_CHOICE:
            presentation["options"] = question.options
            presentation["instruction"] = "Select the correct answer:"
        else:
            presentation["instruction"] = "Fill in the blank:"
        
        return presentation
    
    def _present_flashcard(self, question: Question, index: int) -> Dict:
        """Present question in flashcard format"""
        return {
            "format": "flashcard",
            "question_number": index + 1,
            "total_questions": self.current_session.total_questions,
            "front": question.question,
            "type": question.type.value,
            "difficulty": question.difficulty,
            "topic": question.topic,
            "options": question.options if question.type == QuizType.MULTIPLE_CHOICE else None,
            "instruction": "Think about your answer, then flip to see the correct answer and explanation"
        }
    
    def submit_answer(self, question_index: int, user_answer: str) -> Dict:
        """Submit an answer and get intelligent feedback"""
        if not self.current_session or question_index >= len(self.current_session.questions):
            return {"error": "No valid question to answer"}
        
        question = self.current_session.questions[question_index]
        is_correct = self._check_answer(question, user_answer)
        
        # Generate intelligent feedback
        feedback = self._generate_feedback(question, user_answer, is_correct)
        
        # Record attempt
        attempt = QuizAttempt(
            question_id=question.id,
            user_answer=user_answer,
            is_correct=is_correct,
            timestamp=datetime.now().isoformat(),
            feedback_given=feedback
        )
        
        self.current_session.attempts.append(attempt)
        
        if is_correct:
            self.current_session.score += 1
        else:
            # Track wrong answer for analytics
            self._track_wrong_answer(question, user_answer, feedback)
        
        return {
            "correct": is_correct,
            "feedback": feedback,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "score": f"{self.current_session.score}/{question_index + 1}"
        }
    
    def _check_answer(self, question: Question, user_answer: str) -> bool:
        """Check if the user's answer is correct"""
        if question.type == QuizType.MULTIPLE_CHOICE:
            # Extract letter from answer (e.g., "A)" -> "A")
            user_letter = re.search(r'^([A-D])', user_answer.upper())
            correct_letter = re.search(r'^([A-D])', question.correct_answer.upper())
            
            if user_letter and correct_letter:
                return user_letter.group(1) == correct_letter.group(1)
        else:
            # Fill in the blank - more flexible matching
            user_clean = user_answer.lower().strip()
            correct_clean = question.correct_answer.lower().strip()
            
            # Exact match or close match
            return user_clean == correct_clean or user_clean in correct_clean or correct_clean in user_clean
        
        return False
    
    def _generate_feedback(self, question: Question, user_answer: str, is_correct: bool) -> str:
        """Generate intelligent feedback explaining why the answer is right or wrong"""
        
        if is_correct:
            return f"✅ Correct! {question.explanation}"
        
        # Generate specific feedback for wrong answers
        feedback_prompt = f"""
        The student answered "{user_answer}" to the question: "{question.question}"
        The correct answer is: "{question.correct_answer}"
        
        Provide specific feedback explaining:
        1. Why their answer is incorrect
        2. What the correct concept is
        3. Any relevance their answer might have
        
        Be encouraging but educational. Keep it concise (2-3 sentences).
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful tutor providing constructive feedback to students."},
                    {"role": "user", "content": feedback_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_feedback = response.choices[0].message.content.strip()
            return f"❌ {ai_feedback}\n\n💡 {question.explanation}"
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return f"❌ That's not correct. The right answer is '{question.correct_answer}'. {question.explanation}"
    
    def _track_wrong_answer(self, question: Question, user_answer: str, feedback: str):
        """Track wrong answers for analytics"""
        wrong_answer_record = {
            "question_id": question.id,
            "question": question.question,
            "topic": question.topic,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        self.user_analytics["wrong_answers"].append(wrong_answer_record)
        
        # Update topic performance
        topic = question.topic
        if topic not in self.user_analytics["topic_performance"]:
            self.user_analytics["topic_performance"][topic] = {"correct": 0, "incorrect": 0}
        
        self.user_analytics["topic_performance"][topic]["incorrect"] += 1
    
    def complete_quiz(self) -> Dict:
        """Complete the current quiz session and save results"""
        if not self.current_session:
            return {"error": "No active quiz session"}
        
        self.current_session.completed_at = datetime.now().isoformat()
        
        # Calculate final score
        total_score = self.current_session.score
        total_questions = self.current_session.total_questions
        percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0
        
        # Update analytics
        self.user_analytics["quiz_sessions"].append(asdict(self.current_session))
        self._save_analytics()
        
        results = {
            "session_id": self.current_session.session_id,
            "score": total_score,
            "total_questions": total_questions,
            "percentage": round(percentage, 1),
            "quiz_type": self.current_session.quiz_type.value,
            "quiz_format": self.current_session.quiz_format.value,
            "duration": self._calculate_duration(),
            "areas_for_improvement": self._get_improvement_areas()
        }
        
        # Reset current session
        self.current_session = None
        
        return results
    
    def _calculate_duration(self) -> str:
        """Calculate quiz duration"""
        if not self.current_session.started_at or not self.current_session.completed_at:
            return "Unknown"
        
        start = datetime.fromisoformat(self.current_session.started_at)
        end = datetime.fromisoformat(self.current_session.completed_at)
        duration = end - start
        
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        
        return f"{minutes}m {seconds}s"
    
    def _get_improvement_areas(self) -> List[str]:
        """Identify areas where the user needs improvement"""
        wrong_topics = []
        
        for attempt in self.current_session.attempts:
            if not attempt.is_correct:
                question = next((q for q in self.current_session.questions if q.id == attempt.question_id), None)
                if question and question.topic not in wrong_topics:
                    wrong_topics.append(question.topic)
        
        return wrong_topics
    
    def get_analytics(self) -> Dict:
        """Get comprehensive user analytics"""
        total_sessions = len(self.user_analytics["quiz_sessions"])
        total_questions = sum(session["total_questions"] for session in self.user_analytics["quiz_sessions"])
        total_correct = sum(session["score"] for session in self.user_analytics["quiz_sessions"])
        
        return {
            "total_quizzes": total_sessions,
            "total_questions_answered": total_questions,
            "overall_accuracy": round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0,
            "topic_performance": self.user_analytics["topic_performance"],
            "recent_wrong_answers": self.user_analytics["wrong_answers"][-10:],  # Last 10 wrong answers
            "improvement_suggestions": self._generate_improvement_suggestions()
        }
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Generate personalized improvement suggestions"""
        suggestions = []
        
        # Analyze topic performance
        for topic, performance in self.user_analytics["topic_performance"].items():
            total = performance["correct"] + performance["incorrect"]
            if total >= 3:  # Enough data points
                accuracy = performance["correct"] / total
                if accuracy < 0.7:  # Less than 70% accuracy
                    suggestions.append(f"Review {topic} - current accuracy: {accuracy:.1%}")
        
        # Analyze question types
        wrong_mc = sum(1 for qa in self.user_analytics["wrong_answers"] 
                      if any(q["type"] == "multiple_choice" for q in self.user_analytics["quiz_sessions"] 
                            for question in q["questions"] if question["id"] == qa["question_id"]))
        
        if wrong_mc > 5:
            suggestions.append("Practice multiple choice strategies - eliminate wrong answers first")
        
        if len(suggestions) == 0:
            suggestions.append("Great job! Keep practicing to maintain your performance")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def review_wrong_answers(self, topic: str = None) -> List[Dict]:
        """Get wrong answers for review, optionally filtered by topic"""
        wrong_answers = self.user_analytics["wrong_answers"]
        
        if topic:
            wrong_answers = [qa for qa in wrong_answers if qa["topic"].lower() == topic.lower()]
        
        return wrong_answers[-20:]  # Return last 20 for review


# Example usage and testing functions
def main():
    """Example usage of the QuizGenerator"""
    
    # Initialize the quiz generator
    quiz_gen = QuizGenerator()
    
    print("🎓 Advanced Quiz Generator")
    print("=" * 50)
    
    # Example 1: Create a mixed quiz about biology
    print("\n📚 Creating a biology quiz...")
    session = quiz_gen.create_quiz(
        content_source="photosynthesis and cellular respiration",
        quiz_length=3,
        quiz_type=QuizType.MIXED,
        quiz_format=QuizFormat.STANDARD,
        difficulty="medium"
    )
    
    # Present questions and simulate answers
    for i in range(len(session.questions)):
        print(f"\n{'='*50}")
        question_data = quiz_gen.present_question(i)
        print(f"Question {question_data['question_number']}: {question_data['question']}")
        
        if question_data.get('options'):
            for option in question_data['options']:
                print(f"  {option}")
        
        # Simulate user answer (you would get this from user input)
        if i == 0:
            user_answer = "A"  # Simulate correct answer
        else:
            user_answer = "Wrong answer"  # Simulate wrong answer
        
        result = quiz_gen.submit_answer(i, user_answer)
        print(f"\nResult: {result['feedback']}")
        print(f"Score: {result['score']}")
    
    # Complete quiz and show results
    final_results = quiz_gen.complete_quiz()
    print(f"\n🎯 Quiz Complete!")
    print(f"Final Score: {final_results['score']}/{final_results['total_questions']} ({final_results['percentage']}%)")
    print(f"Duration: {final_results['duration']}")
    
    if final_results['areas_for_improvement']:
        print(f"Areas for improvement: {', '.join(final_results['areas_for_improvement'])}")
    
    # Show analytics
    analytics = quiz_gen.get_analytics()
    print(f"\n📊 Your Analytics:")
    print(f"Total Quizzes: {analytics['total_quizzes']}")
    print(f"Overall Accuracy: {analytics['overall_accuracy']}%")
    
    if analytics['improvement_suggestions']:
        print(f"\n💡 Suggestions:")
        for suggestion in analytics['improvement_suggestions']:
            print(f"  • {suggestion}")


if __name__ == "__main__":
    main()
