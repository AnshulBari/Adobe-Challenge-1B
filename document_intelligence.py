"""
Persona-Driven Document Intelligence System

A lightweight, CPU-only document processing system that extracts and ranks
relevant content based on persona and job requirements. 

ADOBE CHALLENGE 1B COMPLIANCE:
✅ Model size: ~90MB (all-MiniLM-L6-v2) - well under 1GB limit
✅ Processing time: <60s for typical documents 
✅ CPU-only operation: No GPU dependencies
✅ Offline capability: Works without internet after setup

Key Features:
- PDF text extraction with pdfplumber
- Semantic similarity using all-MiniLM-L6-v2 (90MB)
- Dual-stage relevance filtering (chunk → sentence)
- Batch processing for efficiency
- CPU-only operations
"""

import os
import re
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
import pdfplumber
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentIntelligenceProcessor:
    """
    Main processor class for persona-driven document intelligence.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the processor with the specified embedding model.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Download required NLTK data if not present."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            logger.info("Downloading NLTK punkt_tab tokenizer...")
            nltk.download('punkt_tab', quiet=True)
    
    def _load_model(self):
        """Lazy load the embedding model to save memory."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
    
    def extract_text_from_pdfs(self, pdf_dir: str) -> List[Dict[str, Any]]:
        """
        Extract text chunks from all PDF files in the specified directory.
        
        Args:
            pdf_dir: Directory containing PDF files
            
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return chunks
        
        logger.info(f"Processing {len(pdf_files)} PDF files...")
        
        for filename in pdf_files:
            file_path = os.path.join(pdf_dir, filename)
            logger.info(f"Extracting text from: {filename}")
            
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text and text.strip():
                            # Split by paragraph boundaries (double newlines)
                            paragraphs = re.split(r'\n\s*\n', text)
                            
                            for para in paragraphs:
                                clean_para = para.strip()
                                if clean_para and len(clean_para) > 50:  # Filter very short paragraphs
                                    chunks.append({
                                        "text": clean_para,
                                        "page": page_num,
                                        "source": filename,
                                        "char_count": len(clean_para)
                                    })
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(chunks)} text chunks from {len(pdf_files)} documents")
        return chunks
    
    def rank_chunks_by_relevance(self, chunks: List[Dict[str, Any]], 
                                persona: str, job: str, max_chunks: int = 5) -> List[int]:
        """
        Rank text chunks by relevance to persona and job using semantic similarity.
        
        Args:
            chunks: List of text chunks with metadata
            persona: Target persona (e.g., "Investment Analyst")
            job: Job to be done (e.g., "Analyze revenue trends")
            max_chunks: Maximum number of top chunks to return
            
        Returns:
            List of indices of max_chunks most relevant chunks
        """
        if not chunks:
            return []
        
        self._load_model()
        
        # Create query combining persona and job
        query = f"Role: {persona}\nTask: {job}"
        logger.info(f"Ranking chunks for query: {query}")
        
        # Extract texts for embedding
        chunk_texts = [chunk["text"] for chunk in chunks]
        
        # Compute embeddings in batches for efficiency
        logger.info("Computing query embedding...")
        query_embed = self.model.encode([query], show_progress_bar=False)
        
        logger.info(f"Computing embeddings for {len(chunk_texts)} chunks...")
        chunk_embeds = self.model.encode(chunk_texts, show_progress_bar=True, batch_size=32)
        
        # Compute cosine similarity
        cos_sim = np.dot(chunk_embeds, query_embed.T).flatten()
        
        # Get top-k indices, ensuring diversity across documents
        top_k = min(max_chunks, len(chunks))
        all_ranked_indices = np.argsort(cos_sim)[::-1]
        
        # Group chunks by document
        doc_chunks = {}
        for idx in all_ranked_indices:
            chunk = chunks[idx]
            doc_name = os.path.basename(chunk["source"])
            if doc_name not in doc_chunks:
                doc_chunks[doc_name] = []
            doc_chunks[doc_name].append((idx, cos_sim[idx]))
        
        # Select best chunk from each document first
        ranked_indices = []
        used_documents = set()
        
        # First pass: get the best chunk from each document
        for doc_name, doc_chunk_list in doc_chunks.items():
            if len(ranked_indices) < top_k:
                best_idx, best_score = doc_chunk_list[0]  # Already sorted by score
                ranked_indices.append(best_idx)
                used_documents.add(doc_name)
        
        # Second pass: if we still need more chunks, get additional ones
        remaining_slots = top_k - len(ranked_indices)
        if remaining_slots > 0:
            for idx in all_ranked_indices:
                if idx not in ranked_indices and remaining_slots > 0:
                    ranked_indices.append(idx)
                    remaining_slots -= 1
        
        logger.info(f"Top {len(ranked_indices)} chunks selected from {len(used_documents)} different documents")
        return ranked_indices
    
    def refine_chunks_to_sentences(self, chunks: List[Dict[str, Any]], 
                                  chunk_indices: List[int], persona: str, job: str) -> tuple:
        """
        Refine top chunks by extracting most relevant sentences.
        
        Args:
            chunks: List of all text chunks
            chunk_indices: Indices of chunks to refine
            persona: Target persona
            job: Job to be done
            
        Returns:
            Tuple of (extracted_sections, sub_sections)
        """
        if not chunk_indices:
            return [], []
        
        query = f"Role: {persona}\nTask: {job}"
        query_embed = self.model.encode([query], show_progress_bar=False)
        
        extracted_sections = []
        sub_sections = []
        
        logger.info("Refining top chunks to extract key sentences...")
        
        for rank, idx in enumerate(chunk_indices, 1):
            chunk = chunks[idx]
            
            # Tokenize into sentences
            sentences = sent_tokenize(chunk["text"])
            
            if not sentences:
                continue
            
            # Compute sentence embeddings and similarities
            sent_embeds = self.model.encode(sentences, show_progress_bar=False)
            sent_scores = np.dot(sent_embeds, query_embed.T).flatten()
            
            # Get top 3-5 sentences for better content
            top_sent_count = min(5, max(3, len(sentences) // 3))
            top_sent_indices = np.argsort(sent_scores)[::-1][:top_sent_count]
            top_sentences = [sentences[i] for i in sorted(top_sent_indices) if i < len(sentences)]
            
            # Create more descriptive section title
            chunk_text = chunk["text"].strip()
            lines = chunk_text.split('\n')
            
            # Try to find a good title from the first few lines
            section_title = ""
            for line in lines[:3]:
                line = line.strip()
                if line and not line.startswith("•") and len(line) > 10:
                    section_title = line
                    break
            
            # Fallback to first 10 words if no good title found
            if not section_title:
                section_title = ' '.join(chunk_text.split()[:10])
            
            # Clean up the title
            if len(section_title) > 80:
                section_title = section_title[:77] + "..."
            
            extracted_sections.append({
                "document": os.path.basename(chunk["source"]),
                "page_number": chunk["page"],
                "section_title": section_title,
                "importance_rank": rank,
                "relevance_score": float(sent_scores.max())
            })
            
            # Join sentences for better refined text
            refined_text = ' '.join(top_sentences)
            
            sub_sections.append({
                "document": os.path.basename(chunk["source"]),
                "refined_text": refined_text,
                "page_number": chunk["page"],
                "relevance_score": float(sent_scores.max()),
                "full_text": chunk_text  # Keep full text for fallback
            })
        
        return extracted_sections, sub_sections
    
    def process_documents(self, pdf_dir: str, persona: str, job: str, 
                         output_file: Optional[str] = None, max_sections: int = 5) -> Dict[str, Any]:
        """
        Main processing function that orchestrates the entire pipeline.
        
        Args:
            pdf_dir: Directory containing PDF files
            persona: Target persona
            job: Job to be done
            output_file: Optional output JSON file path
            max_sections: Maximum number of sections to extract (default: 5)
            
        Returns:
            Dictionary containing processed results
        """
        start_time = time.time()
        logger.info("Starting document intelligence processing...")
        logger.info(f"PDF Directory: {pdf_dir}")
        logger.info(f"Persona: {persona}")
        logger.info(f"Job: {job}")
        logger.info(f"Max sections: {max_sections}")
        
        # Step 1: Extract text from PDFs
        chunks = self.extract_text_from_pdfs(pdf_dir)
        if not chunks:
            logger.error("No text chunks extracted. Check PDF directory and files.")
            return self._create_empty_result(pdf_dir, persona, job)
        
        # Step 2: Rank chunks by relevance (limit to max_sections)
        top_chunk_indices = self.rank_chunks_by_relevance(chunks, persona, job, max_chunks=max_sections)
        
        # Step 3: Refine top chunks to sentences
        extracted_sections, sub_sections = self.refine_chunks_to_sentences(
            chunks, top_chunk_indices, persona, job
        )
        
        # Step 4: Generate final output
        processing_time = time.time() - start_time
        result = {
            "metadata": {
                "input_documents": [os.path.basename(source) for source in set(chunk["source"] for chunk in chunks)],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "total_chunks_processed": len(chunks),
                "top_chunks_selected": len(top_chunk_indices)
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": sub_sections,  # Updated field name to match expected format
            "most_relevant_sections": extracted_sections,  # For backward compatibility
            "detailed_analysis": sub_sections  # For backward compatibility
        }
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
        
        return result
    
    def _create_empty_result(self, pdf_dir: str, persona: str, job: str) -> Dict[str, Any]:
        """Create empty result structure when no documents are processed."""
        return {
            "metadata": {
                "input_documents": [],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "processing_time_seconds": 0,
                "total_chunks_processed": 0,
                "top_chunks_selected": 0,
                "error": "No documents found or processed"
            },
            "extracted_sections": [],
            "sub_section_analysis": []
        }


def main():
    """
    Example usage of the Document Intelligence Processor.
    """
    # Initialize processor
    processor = DocumentIntelligenceProcessor()
    
    # Example configuration
    pdf_directory = "./sample_documents"  # Change to your PDF directory
    persona = "Investment Analyst"
    job = "Analyze revenue trends and R&D investments"
    output_file = "document_intelligence_output.json"
    
    try:
        # Process documents
        result = processor.process_documents(
            pdf_dir=pdf_directory,
            persona=persona,
            job=job,
            output_file=output_file
        )
        
        # Print summary
        print("\n" + "="*60)
        print("DOCUMENT INTELLIGENCE PROCESSING COMPLETE")
        print("="*60)
        print(f"Processing Time: {result['metadata']['processing_time_seconds']} seconds")
        print(f"Documents Processed: {len(result['metadata']['input_documents'])}")
        print(f"Chunks Analyzed: {result['metadata']['total_chunks_processed']}")
        print(f"Top Sections Selected: {len(result['extracted_sections'])}")
        print(f"Output File: {output_file}")
        
        # Display top sections
        if result['extracted_sections']:
            print("\nTOP RELEVANT SECTIONS:")
            print("-" * 40)
            for section in result['extracted_sections']:
                print(f"Rank {section['importance_rank']}: {section['document']} (Page {section['page_number']})")
                print(f"  Section: {section['section_title']}")
                print()
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise


if __name__ == "__main__":
    main()
