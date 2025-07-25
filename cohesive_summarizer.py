"""
Cohesive Summary Generator for Adobe Challenge 1B
Generates flowing 500-word summaries from multiple related PDFs
"""

import os
import re
import json
import time
import logging
import numpy as np
import pdfplumber
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
import nltk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CohesiveSummarizer:
    """
    Enhanced document intelligence processor that generates cohesive summaries
    from multiple related PDF documents.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Ensure NLTK punkt tokenizer is available."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
    
    def _load_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
    
    def extract_structured_content(self, pdf_dir: str) -> List[Dict[str, Any]]:
        """
        Extract and structure content from all PDFs in directory.
        
        Args:
            pdf_dir: Directory containing PDF files
            
        Returns:
            List of structured document content
        """
        documents = []
        filenames = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
        
        if not filenames:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return documents
        
        logger.info(f"Processing {len(filenames)} PDF files for cohesive summary...")
        
        for filename in filenames:
            filepath = os.path.join(pdf_dir, filename)
            try:
                with pdfplumber.open(filepath) as pdf:
                    doc = {"filename": filename, "pages": []}
                    
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text and text.strip():
                            # Structure content hierarchically
                            # Look for common section patterns
                            sections = re.split(r'\n\s*\d+\.\d+|\n\s*[A-Z]+\s|\n\s*[IVX]+\.', text)
                            
                            doc["pages"].append({
                                "page_number": page.page_number,
                                "sections": [s.strip() for s in sections if s.strip()]
                            })
                    
                    if doc["pages"]:  # Only add if has content
                        documents.append(doc)
                        
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                continue
        
        logger.info(f"Successfully extracted content from {len(documents)} documents")
        return documents
    
    def generate_cohesive_summary(self, pdf_dir: str, persona: str, job: str, 
                                max_words: int = 500) -> Dict[str, Any]:
        """
        Generate a cohesive summary from multiple related PDFs.
        
        Args:
            pdf_dir: Directory containing PDF files
            persona: User persona (e.g., "Investment Analyst")
            job: Job to be done (e.g., "Analyze revenue trends")
            max_words: Maximum words in summary (default: 500)
            
        Returns:
            Dictionary containing metadata and cohesive summary
        """
        start_time = time.time()
        self._load_model()
        
        # 1. Extract and structure content
        documents = self.extract_structured_content(pdf_dir)
        if not documents:
            return self._empty_result(pdf_dir, persona, job)
        
        # 2. Create context-aware query
        query = f"As a {persona}, I need to {job}. Key focus areas and insights:"
        
        # 3. Prepare content for processing
        all_content = []
        for doc in documents:
            for page in doc["pages"]:
                for section in page["sections"]:
                    # Split section into logical chunks
                    paragraphs = [p for p in re.split(r'\n\s*\n', section) if p.strip()]
                    for para in paragraphs:
                        if len(para.split()) >= 5:  # Filter very short content
                            all_content.append({
                                "text": para,
                                "source": doc["filename"],
                                "page": page["page_number"],
                                "tokens": len(para.split())
                            })
        
        if not all_content:
            return self._empty_result(pdf_dir, persona, job)
        
        # 4. Compute relevance rankings
        logger.info("Computing semantic relevance scores...")
        content_texts = [c["text"] for c in all_content]
        
        # Batch process embeddings for efficiency
        content_embeddings = self.model.encode(content_texts, batch_size=32)
        query_embedding = self.model.encode([query])[0]
        
        # Compute cosine similarities
        for i, item in enumerate(all_content):
            sim = np.dot(content_embeddings[i], query_embedding) / (
                np.linalg.norm(content_embeddings[i]) * np.linalg.norm(query_embedding)
            )
            item["similarity"] = sim
        
        # 5. Generate cohesive summary
        summary = self._build_cohesive_summary(
            all_content, documents, query_embedding, max_words
        )
        
        # 6. Prepare final result
        processing_time = time.time() - start_time
        logger.info(f"Cohesive summary generated in {processing_time:.2f} seconds")
        
        return {
            "metadata": {
                "input_documents": [doc["filename"] for doc in documents],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "processing_time_seconds": round(processing_time, 2),
                "summary_word_count": len(summary.split()),
                "total_content_chunks": len(all_content),
                "approach": "cohesive_summary"
            },
            "cohesive_summary": summary
        }
    
    def _build_cohesive_summary(self, all_content: List[Dict], documents: List[Dict], 
                               query_embedding: np.ndarray, max_words: int) -> str:
        """Build a cohesive summary maintaining document flow."""
        
        # Sort content by relevance
        sorted_content = sorted(all_content, key=lambda x: x["similarity"], reverse=True)
        
        # Organize content by source document for coherent flow
        content_by_source = {}
        for item in sorted_content:
            content_by_source.setdefault(item["source"], []).append(item)
        
        # Build summary maintaining document order
        summary_parts = []
        current_words = 0
        
        # Process documents in original order
        filenames = [doc["filename"] for doc in documents]
        
        for filename in filenames:
            if filename in content_by_source and current_words < max_words:
                # Sort by page number within document, then by relevance
                doc_content = sorted(
                    content_by_source[filename], 
                    key=lambda x: (x["page"], -x["similarity"])
                )
                
                for item in doc_content:
                    if current_words >= max_words:
                        break
                    
                    # Sentence-level refinement
                    sentences = sent_tokenize(item["text"])
                    selected_sentences = []
                    
                    if len(sentences) > 1:
                        # Compute sentence-level relevance
                        sent_embeddings = self.model.encode(sentences)
                        sent_similarities = np.dot(sent_embeddings, query_embedding)
                        
                        # Select top sentences, maintaining order
                        top_indices = np.argsort(sent_similarities)[-min(3, len(sentences)):]
                        for idx in sorted(top_indices):
                            selected_sentences.append(sentences[idx])
                    else:
                        selected_sentences = sentences
                    
                    # Add content if within word limit
                    new_text = " ".join(selected_sentences)
                    new_words = len(new_text.split())
                    
                    if current_words + new_words <= max_words:
                        summary_parts.append(new_text)
                        current_words += new_words
                    else:
                        # Add partial content if significant space remains
                        remaining_words = max_words - current_words
                        if remaining_words > 20:  # Only add if meaningful space
                            partial_text = " ".join(new_text.split()[:remaining_words])
                            summary_parts.append(partial_text)
                            current_words = max_words
                        break
        
        # Create final cohesive summary
        cohesive_summary = " ".join(summary_parts)
        
        # Add completion note if summary was truncated
        if current_words >= max_words and len(summary_parts) > 1:
            cohesive_summary = cohesive_summary.rstrip() + "..."
        
        return cohesive_summary
    
    def _empty_result(self, pdf_dir: str, persona: str, job: str) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "metadata": {
                "input_documents": [],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "processing_time_seconds": 0,
                "summary_word_count": 0,
                "total_content_chunks": 0,
                "approach": "cohesive_summary",
                "error": "No valid PDF content found"
            },
            "cohesive_summary": "No relevant content found in the provided documents."
        }

# Example usage
def main():
    """Example usage of the cohesive summarizer."""
    summarizer = CohesiveSummarizer()
    
    result = summarizer.generate_cohesive_summary(
        pdf_dir="sample_documents",
        persona="Investment Analyst", 
        job="Analyze revenue trends and R&D investments",
        max_words=500
    )
    
    # Save result
    with open("cohesive_summary.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Cohesive summary generated: {result['metadata']['summary_word_count']} words")
    print(f"Summary: {result['cohesive_summary'][:200]}...")

if __name__ == "__main__":
    main()
