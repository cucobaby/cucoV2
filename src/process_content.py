import os
import re
import yaml
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import openai
from dotenv import load_dotenv

from models import StudyGuideMetadata, ContentChunk

# Load environment variables
load_dotenv()

class ContentProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
        
        # Initialize ChromaDB
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="study_guides",
            metadata={"description": "Canvas course study guides with YAML metadata"}
        )
    
    def extract_yaml_metadata(self, content: str) -> tuple[StudyGuideMetadata, str]:
        """Extract YAML front matter and return metadata + remaining content"""
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(yaml_pattern, content, re.DOTALL)
        
        if not match:
            raise ValueError("No YAML front matter found")
        
        yaml_content = match.group(1)
        markdown_content = match.group(2)
        
        metadata_dict = yaml.safe_load(yaml_content)
        metadata = StudyGuideMetadata(**metadata_dict)
        
        return metadata, markdown_content
    
    def extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections based on markdown headers"""
        sections = []
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check for headers (## or ###)
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'type': self._classify_section_type(current_section)
                    })
                
                # Start new section
                current_section = line[3:].strip()
                current_content = []
            
            elif line.startswith('### '):
                # Subsection - add to current content
                current_content.append(line)
            
            else:
                current_content.append(line)
        
        # Don't forget the last section
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'type': self._classify_section_type(current_section)
            })
        
        return sections
    
    def _classify_section_type(self, section_title: str) -> str:
        """Classify section type based on title"""
        title_lower = section_title.lower()
        
        if 'learning objective' in title_lower:
            return 'learning_objectives'
        elif 'vocabulary' in title_lower or 'concept' in title_lower:
            return 'vocabulary'
        elif 'mechanism' in title_lower:
            return 'mechanisms'
        elif 'experiment' in title_lower:
            return 'experiments'
        elif 'application' in title_lower:
            return 'applications'
        elif 'regulation' in title_lower:
            return 'regulation'
        else:
            return 'general'
    
    def chunk_content(self, content: str, max_size: int = None) -> List[str]:
        """Split content into chunks while preserving meaning"""
        if max_size is None:
            max_size = self.chunk_size
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > max_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def process_study_guide(self, file_path: Path) -> List[ContentChunk]:
        """Process a single study guide file"""
        print(f"Processing: {file_path.name}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata and content
        metadata, markdown_content = self.extract_yaml_metadata(content)
        
        # Extract sections
        sections = self.extract_sections(markdown_content)
        
        chunks = []
        
        for section in sections:
            section_chunks = self.chunk_content(section['content'])
            
            for i, chunk_text in enumerate(section_chunks):
                # Create unique ID for this chunk
                chunk_id = hashlib.md5(
                    f"{file_path.name}_{section['title']}_{i}".encode()
                ).hexdigest()
                
                chunk = ContentChunk(
                    id=chunk_id,
                    content=chunk_text,
                    metadata=metadata,
                    section_title=section['title'],
                    section_type=section['type'],
                    chunk_index=i,
                    source_file=str(file_path)
                )
                
                chunks.append(chunk)
        
        return chunks
    
    def store_chunks_in_chromadb(self, chunks: List[ContentChunk]):
        """Store chunks in ChromaDB with embeddings"""
        print(f"Storing {len(chunks)} chunks in ChromaDB...")
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        embeddings = []
        
        for chunk in chunks:
            # Generate embedding
            embedding = self.generate_embedding(chunk.content)
            if not embedding:
                continue
            
            documents.append(chunk.content)
            ids.append(chunk.id)
            embeddings.append(embedding)
            
            # Flatten metadata for ChromaDB
            metadata = {
                'title': chunk.metadata.title,
                'course': chunk.metadata.course,
                'chapter': chunk.metadata.chapter,
                'lectures': ', '.join(chunk.metadata.lectures),
                'date': chunk.metadata.date,
                'study_context': chunk.metadata.study_context,
                'learning_focus': chunk.metadata.learning_focus,
                'section_title': chunk.section_title,
                'section_type': chunk.section_type,
                'chunk_index': chunk.chunk_index,
                'source_file': chunk.source_file
            }
            
            # Add note if it exists
            if chunk.metadata.note:
                metadata['note'] = chunk.metadata.note
            
            metadatas.append(metadata)
        
        # Add to ChromaDB collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"Successfully stored {len(documents)} chunks")
    
    def process_all_study_guides(self, data_dir: str = "data/course_materials/lectures"):
        """Process all study guide files in the directory"""
        data_path = Path(data_dir)
        
        if not data_path.exists():
            raise ValueError(f"Data directory not found: {data_dir}")
        
        study_guide_files = list(data_path.glob("study_guide_*.md"))
        
        if not study_guide_files:
            raise ValueError(f"No study guide files found in {data_dir}")
        
        print(f"Found {len(study_guide_files)} study guide files")
        
        all_chunks = []
        
        for file_path in sorted(study_guide_files):
            try:
                chunks = self.process_study_guide(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        print(f"Total chunks created: {len(all_chunks)}")
        
        # Store in ChromaDB
        if all_chunks:
            self.store_chunks_in_chromadb(all_chunks)
        
        return all_chunks

def main():
    """Main function to process all study guides"""
    processor = ContentProcessor()
    
    try:
        chunks = processor.process_all_study_guides()
        print(f"\n✅ Successfully processed {len(chunks)} chunks from study guides")
        print(f"📊 ChromaDB collection '{processor.collection.name}' now contains {processor.collection.count()} items")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
