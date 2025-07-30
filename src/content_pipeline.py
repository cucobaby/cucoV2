"""
Content Processing Pipeline
Processes raw Canvas educational material through analysis and structuring pipeline
"""
import sys
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add the src directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_analyzer import ContentAnalyzer
from process_content import ContentProcessor
from models import StudyGuideMetadata, ContentChunk


class ContentPipeline:
    """
    Orchestrates the complete content processing pipeline:
    Raw Text → Content Analysis → Structured Processing → ChromaDB Storage
    """
    
    def __init__(self, input_file: str = "studyGuide3.txt"):
        # Convert to absolute path relative to project root
        if not os.path.isabs(input_file):
            # Assume we're running from src/ directory, so go up one level
            project_root = Path(__file__).parent.parent
            self.input_file = str(project_root / input_file)
        else:
            self.input_file = input_file
            
        self.content_analyzer = ContentAnalyzer()
        self.content_processor = ContentProcessor()
        
        # Create output directories in project root
        project_root = Path(__file__).parent.parent
        self.temp_dir = project_root / "temp_processing"
        self.temp_dir.mkdir(exist_ok=True)
        
    def run_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete pipeline
        
        Returns:
            Dictionary with pipeline results and statistics
        """
        print("🚀 Starting Content Processing Pipeline")
        print("=" * 50)
        
        try:
            # Step 1: Load raw content
            print("📖 Step 1: Loading raw content...")
            raw_content = self._load_raw_content()
            
            # Step 2: Analyze content with AI
            print("🔍 Step 2: Analyzing content structure...")
            analysis_result = self._analyze_content(raw_content)
            
            # Step 3: Generate structured metadata
            print("📋 Step 3: Generating YAML metadata...")
            metadata = self._generate_metadata(analysis_result)
            
            # Step 4: Create structured study guide
            print("📝 Step 4: Creating structured study guide...")
            structured_file = self._create_structured_file(raw_content, metadata, analysis_result)
            
            # Step 5: Process through content processor
            print("⚙️ Step 5: Processing and chunking content...")
            chunks = self._process_content(structured_file)
            
            # Step 6: Store in ChromaDB
            print("💾 Step 6: Storing in ChromaDB...")
            self._store_in_database(chunks)
            
            # Step 7: Generate summary
            print("📊 Step 7: Generating pipeline summary...")
            summary = self._generate_summary(analysis_result, chunks)
            
            print("\n✅ Pipeline completed successfully!")
            return summary
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "failed", "error": str(e)}
    
    def _load_raw_content(self) -> str:
        """Load raw content from input file"""
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file '{self.input_file}' not found")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📄 Loaded {len(content)} characters from {self.input_file}")
        return content
    
    def _analyze_content(self, raw_content: str) -> Any:
        """Analyze content using ContentAnalyzer"""
        # Split content into chunks for analysis
        content_chunks = [raw_content]  # For now, analyze as single chunk
        
        analysis = self.content_analyzer.analyze_content(
            content_chunks,
            source_info={"filename": self.input_file, "type": "canvas_material"}
        )
        
        print(f"   🎯 Discovered {len(analysis.main_topics)} main topics")
        print(f"   📚 Subject area: {analysis.subject_area}")
        print(f"   📖 Content type: {analysis.content_type}")
        
        return analysis
    
    def _generate_metadata(self, analysis) -> StudyGuideMetadata:
        """Generate YAML metadata from content analysis"""
        
        # Extract key information
        main_topic = analysis.main_topics[0] if analysis.main_topics else None
        topic_name = main_topic.name if main_topic else "Study Material"
        
        # Generate metadata
        metadata = StudyGuideMetadata(
            title=f"{analysis.subject_area}: {topic_name}",
            type="study_guide",
            course=analysis.subject_area,
            chapter=topic_name,
            lectures=[f"Auto-generated from {Path(self.input_file).name}"],  # Use just filename, not full path
            date=datetime.now().strftime("%Y-%m-%d"),
            study_context="Canvas material processing",
            learning_focus=", ".join([obj for obj in analysis.learning_objectives[:3]]) if analysis.learning_objectives else "General understanding",
            note=f"Automatically processed from {Path(self.input_file).name} on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        print(f"   📋 Generated metadata for: {metadata.title}")
        return metadata
    
    def _create_structured_file(self, raw_content: str, metadata: StudyGuideMetadata, analysis) -> Path:
        """Create a structured markdown file with YAML front matter"""
        
        # Create YAML front matter
        yaml_front_matter = f"""---
title: "{metadata.title}"
type: "{metadata.type}"
course: "{metadata.course}"
chapter: "{metadata.chapter}"
lectures:
  - "{metadata.lectures[0]}"
date: "{metadata.date}"
study_context: "{metadata.study_context}"
learning_focus: "{metadata.learning_focus}"
note: "{metadata.note}"
---

"""
        
        # Structure the content
        structured_content = yaml_front_matter
        
        # Add learning objectives if available
        if analysis.learning_objectives:
            structured_content += "## Learning Objectives\n\n"
            for obj in analysis.learning_objectives:
                structured_content += f"- {obj}\n"
            structured_content += "\n"
        
        # Add main topics as sections
        if analysis.main_topics:
            for topic in analysis.main_topics:
                structured_content += f"## {topic.name}\n\n"
                structured_content += f"{topic.description}\n\n"
                
                if topic.key_concepts:
                    structured_content += "### Key Concepts\n\n"
                    for concept in topic.key_concepts:
                        structured_content += f"- {concept}\n"
                    structured_content += "\n"
        
        # Add the raw content as a main section
        structured_content += "## Content\n\n"
        structured_content += raw_content
        
        # Add key terms if available
        if analysis.key_terms:
            structured_content += "\n\n## Vocabulary\n\n"
            for term, definition in analysis.key_terms.items():
                structured_content += f"**{term}**: {definition}\n\n"
        
        # Save structured file
        input_filename = Path(self.input_file).name  # Just get the filename, not full path
        print(f"   DEBUG: input_file = {self.input_file}")
        print(f"   DEBUG: input_filename = {input_filename}")
        print(f"   DEBUG: temp_dir = {self.temp_dir}")
        
        output_filename = f"structured_{input_filename.replace('.txt', '.md')}"
        output_file = self.temp_dir / output_filename
        print(f"   DEBUG: output_file = {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(structured_content)
        
        print(f"   📝 Created structured file: {output_file}")
        return output_file
    
    def _process_content(self, structured_file: Path) -> List[ContentChunk]:
        """Process structured file through ContentProcessor"""
        chunks = self.content_processor.process_study_guide(structured_file)
        print(f"   🧩 Created {len(chunks)} content chunks")
        return chunks
    
    def _store_in_database(self, chunks: List[ContentChunk]):
        """Store chunks in ChromaDB"""
        self.content_processor.store_chunks_in_chromadb(chunks)
        print(f"   💾 Stored {len(chunks)} chunks in ChromaDB")
    
    def _generate_summary(self, analysis, chunks: List[ContentChunk]) -> Dict[str, Any]:
        """Generate pipeline summary"""
        return {
            "status": "success",
            "input_file": self.input_file,
            "subject_area": analysis.subject_area,
            "content_type": analysis.content_type,
            "topics_discovered": len(analysis.main_topics),
            "key_terms_found": len(analysis.key_terms),
            "learning_objectives": len(analysis.learning_objectives),
            "chunks_created": len(chunks),
            "chunks_stored": len(chunks),
            "main_topics": [topic.name for topic in analysis.main_topics],
            "difficulty_level": analysis.estimated_difficulty,
            "processing_date": datetime.now().isoformat()
        }


def main():
    """Run the pipeline with default settings"""
    print("🎓 Content Processing Pipeline")
    print("Looking for studyGuide3.txt in project root...")
    
    pipeline = ContentPipeline("studyGuide3.txt")
    result = pipeline.run_pipeline()
    
    # Print summary
    if result["status"] == "success":
        print("\n" + "=" * 50)
        print("📊 PIPELINE SUMMARY")
        print("=" * 50)
        print(f"📁 Input File: {result['input_file']}")
        print(f"📚 Subject: {result['subject_area']}")
        print(f"📖 Content Type: {result['content_type']}")
        print(f"🎯 Topics Found: {result['topics_discovered']}")
        print(f"📝 Key Terms: {result['key_terms_found']}")
        print(f"🎓 Learning Objectives: {result['learning_objectives']}")
        print(f"🧩 Chunks Created: {result['chunks_created']}")
        print(f"📊 Difficulty: {result['difficulty_level']}")
        print(f"\n🎯 Main Topics:")
        for topic in result['main_topics']:
            print(f"   - {topic}")
        print(f"\n✅ Content is now ready for Q&A and quiz generation!")
    else:
        print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
