"""
Canvas API Integration for Educational Assistant
Syncs course content and enables real-time processing
"""
import requests
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from content_pipeline import ContentPipeline
from core_assistant import CoreAssistant

load_dotenv()

class CanvasIntegration:
    """
    Integrates with Canvas Student API to fetch and process course content
    """
    
    def __init__(self, canvas_url: str, access_token: str):
        self.canvas_url = canvas_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.pipeline = ContentPipeline()
        self.assistant = CoreAssistant()
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """Get all courses the student is enrolled in"""
        url = f"{self.canvas_url}/api/v1/courses"
        params = {
            'enrollment_state': 'active',
            'include[]': ['term', 'course_image', 'public_description']
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_course_modules(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all modules for a course"""
        url = f"{self.canvas_url}/api/v1/courses/{course_id}/modules"
        params = {'include[]': ['items']}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_course_pages(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all pages for a course"""
        url = f"{self.canvas_url}/api/v1/courses/{course_id}/pages"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_page_content(self, course_id: int, page_url: str) -> Dict[str, Any]:
        """Get full content of a specific page"""
        url = f"{self.canvas_url}/api/v1/courses/{course_id}/pages/{page_url}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_assignments(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all assignments for a course"""
        url = f"{self.canvas_url}/api/v1/courses/{course_id}/assignments"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_discussion_topics(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all discussion topics for a course"""
        url = f"{self.canvas_url}/api/v1/courses/{course_id}/discussion_topics"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def extract_text_content(self, html_content: str) -> str:
        """Extract plain text from HTML content"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(strip=True)
    
    async def sync_course_content(self, course_id: int) -> Dict[str, Any]:
        """
        Sync all content from a course and process through pipeline
        """
        print(f"🔄 Syncing content for course {course_id}")
        
        results = {
            'course_id': course_id,
            'processed_items': [],
            'total_chunks': 0,
            'topics_discovered': [],
            'sync_date': datetime.now().isoformat()
        }
        
        try:
            # Get course info
            course_info = requests.get(
                f"{self.canvas_url}/api/v1/courses/{course_id}",
                headers=self.headers
            ).json()
            
            print(f"📚 Processing course: {course_info.get('name', 'Unknown')}")
            
            # 1. Process course pages
            pages = self.get_course_pages(course_id)
            for page in pages:
                if page.get('published', False):
                    page_content = self.get_page_content(course_id, page['url'])
                    if page_content.get('body'):
                        text_content = self.extract_text_content(page_content['body'])
                        if len(text_content.strip()) > 100:  # Only process substantial content
                            processed = await self._process_content_item(
                                text_content, 
                                f"Page: {page['title']}", 
                                'course_page'
                            )
                            results['processed_items'].append(processed)
            
            # 2. Process assignments
            assignments = self.get_assignments(course_id)
            for assignment in assignments:
                if assignment.get('description'):
                    text_content = self.extract_text_content(assignment['description'])
                    if len(text_content.strip()) > 100:
                        processed = await self._process_content_item(
                            text_content,
                            f"Assignment: {assignment['name']}",
                            'assignment'
                        )
                        results['processed_items'].append(processed)
            
            # 3. Process discussion topics
            discussions = self.get_discussion_topics(course_id)
            for discussion in discussions:
                if discussion.get('message'):
                    text_content = self.extract_text_content(discussion['message'])
                    if len(text_content.strip()) > 100:
                        processed = await self._process_content_item(
                            text_content,
                            f"Discussion: {discussion['title']}",
                            'discussion'
                        )
                        results['processed_items'].append(processed)
            
            # Calculate totals
            results['total_chunks'] = sum(item['chunks_created'] for item in results['processed_items'])
            all_topics = []
            for item in results['processed_items']:
                all_topics.extend(item.get('topics', []))
            results['topics_discovered'] = list(set(all_topics))
            
            print(f"✅ Sync complete: {len(results['processed_items'])} items, {results['total_chunks']} chunks")
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _process_content_item(self, content: str, title: str, content_type: str) -> Dict[str, Any]:
        """Process a single content item through the pipeline"""
        try:
            # Create temporary file for processing
            temp_file = f"temp_{content_type}_{datetime.now().timestamp()}.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Process through pipeline
            pipeline = ContentPipeline(temp_file)
            result = pipeline.run_pipeline()
            
            # Clean up
            os.remove(temp_file)
            
            return {
                'title': title,
                'content_type': content_type,
                'status': result.get('status', 'unknown'),
                'chunks_created': result.get('chunks_created', 0),
                'topics': result.get('main_topics', []),
                'subject_area': result.get('subject_area', 'Unknown')
            }
            
        except Exception as e:
            return {
                'title': title,
                'content_type': content_type,
                'status': 'failed',
                'error': str(e),
                'chunks_created': 0,
                'topics': []
            }
    
    def ask_question_about_course(self, question: str, course_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Ask a question about course content using the AI assistant
        """
        # For now, use the general assistant
        # Could be enhanced to filter by course_id in the future
        result = self.assistant.ask_question(question)
        
        return {
            'question': question,
            'answer': result['answer'],
            'sources': result['sources'],
            'confidence': result['confidence'],
            'course_id': course_id,
            'timestamp': datetime.now().isoformat()
        }


# Example usage
async def main():
    """Example of how to use the Canvas integration"""
    
    # Initialize Canvas integration
    canvas = CanvasIntegration(
        canvas_url=os.getenv("CANVAS_URL", "https://your-school.instructure.com"),
        access_token=os.getenv("CANVAS_ACCESS_TOKEN")
    )
    
    # Get student's courses
    courses = canvas.get_courses()
    print(f"📚 Found {len(courses)} active courses")
    
    # Sync content for first course
    if courses:
        course_id = courses[0]['id']
        sync_result = await canvas.sync_course_content(course_id)
        print(f"🎯 Discovered topics: {sync_result['topics_discovered']}")
        
        # Ask a question about the content
        answer = canvas.ask_question_about_course(
            "What is photosynthesis?", 
            course_id
        )
        print(f"🤖 AI Answer: {answer['answer']}")

if __name__ == "__main__":
    asyncio.run(main())
