"""
JSON-based Document Intelligence Processor for Adobe Challenge 1B

Standardized interface that processes structured JSON input and produces
standardized JSON output as per Adobe Challenge specifications.

Input Format:
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case",
    "description": "Optional description"
  },
  "documents": [{"filename": "doc.pdf", "title": "Title"}],
  "persona": {"role": "User Persona"},
  "job_to_be_done": {"task": "Use case description"}
}

Output Format:
{
  "metadata": {
    "input_documents": ["list"],
    "persona": "User Persona",
    "job_to_be_done": "Task description",
    "processing_timestamp": "ISO timestamp"
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Title",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }
  ]
}
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from document_intelligence import DocumentIntelligenceProcessor

logger = logging.getLogger(__name__)


class JSONDocumentProcessor:
    """
    JSON-based document processor that handles standardized input/output format.
    """
    
    def __init__(self):
        """Initialize the JSON processor."""
        self.doc_processor = DocumentIntelligenceProcessor()
    
    def validate_input_json(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate the input JSON structure.
        
        Args:
            input_data: Input JSON data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['challenge_info', 'documents', 'persona', 'job_to_be_done']
        
        # Check top-level fields
        for field in required_fields:
            if field not in input_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate challenge_info
        challenge_info = input_data['challenge_info']
        if not isinstance(challenge_info, dict):
            logger.error("challenge_info must be a dictionary")
            return False
        
        # Validate documents
        documents = input_data['documents']
        if not isinstance(documents, list) or not documents:
            logger.error("documents must be a non-empty list")
            return False
        
        for doc in documents:
            if not isinstance(doc, dict) or 'filename' not in doc:
                logger.error("Each document must have a 'filename' field")
                return False
        
        # Validate persona
        persona = input_data['persona']
        if not isinstance(persona, dict) or 'role' not in persona:
            logger.error("persona must be a dictionary with 'role' field")
            return False
        
        # Validate job_to_be_done
        job = input_data['job_to_be_done']
        if not isinstance(job, dict) or 'task' not in job:
            logger.error("job_to_be_done must be a dictionary with 'task' field")
            return False
        
        return True
    
    def check_document_files(self, documents: List[Dict], base_dir: str) -> List[str]:
        """
        Check if all specified documents exist in the base directory.
        
        Args:
            documents: List of document specifications
            base_dir: Base directory to search for files
            
        Returns:
            List of existing file paths
        """
        existing_files = []
        missing_files = []
        
        for doc in documents:
            filename = doc['filename']
            file_path = os.path.join(base_dir, filename)
            
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                missing_files.append(filename)
        
        if missing_files:
            logger.warning(f"Missing files: {missing_files}")
        
        if not existing_files:
            raise FileNotFoundError(f"No specified documents found in {base_dir}")
        
        return existing_files
    
    def process_json_input(self, input_data: Dict[str, Any], base_dir: str = "./input") -> Dict[str, Any]:
        """
        Process documents based on JSON input specification.
        
        Args:
            input_data: Structured JSON input
            base_dir: Base directory containing PDF files
            
        Returns:
            Structured JSON output
        """
        # Validate input
        if not self.validate_input_json(input_data):
            raise ValueError("Invalid input JSON structure")
        
        # Extract parameters
        challenge_info = input_data['challenge_info']
        documents = input_data['documents']
        persona_role = input_data['persona']['role']
        job_task = input_data['job_to_be_done']['task']
        
        # Check document files exist
        file_paths = self.check_document_files(documents, base_dir)
        
        logger.info(f"Processing {len(file_paths)} documents for persona '{persona_role}'")
        logger.info(f"Job: {job_task}")
        
        # Create a temporary directory structure for processing
        temp_dir = Path(base_dir)
        
        # Process documents using existing document intelligence
        start_time = time.time()
        
        # Extract text from PDFs
        text_chunks = self.doc_processor.extract_text_from_pdfs(str(temp_dir))
        
        # Filter chunks to only include specified documents
        specified_filenames = [doc['filename'] for doc in documents]
        filtered_chunks = [
            chunk for chunk in text_chunks 
            if os.path.basename(chunk['source']) in specified_filenames
        ]
        
        if not filtered_chunks:
            raise ValueError("No content extracted from specified documents")
        
        # Process with persona and job
        results = self.doc_processor.process_documents(
            pdf_dir=str(temp_dir),
            persona=persona_role,
            job=job_task,
            max_sections=5  # Standard limit for extracted sections
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        # Convert to standardized output format
        output_data = self._convert_to_standard_output(
            input_data, results, processing_time
        )
        
        return output_data
    
    def _convert_to_standard_output(self, input_data: Dict, results: Dict, processing_time: float) -> Dict[str, Any]:
        """
        Convert internal results to standardized output format.
        
        Args:
            input_data: Original input data
            results: Processing results from document intelligence
            processing_time: Time taken for processing
            
        Returns:
            Standardized output dictionary
        """
        # Extract input document filenames
        input_documents = [doc['filename'] for doc in input_data['documents']]
        
        # Create metadata
        metadata = {
            "input_documents": input_documents,
            "persona": input_data['persona']['role'],
            "job_to_be_done": input_data['job_to_be_done']['task'],
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Convert extracted sections
        extracted_sections = []
        if 'most_relevant_sections' in results:
            for i, section in enumerate(results['most_relevant_sections'], 1):
                # Clean up section titles to be more descriptive
                section_title = section.get('section_title', f"Section {i}")
                # Remove truncated text and make titles more meaningful
                if len(section_title) > 80:
                    section_title = section_title[:77] + "..."
                elif section_title.startswith("•"):
                    # Extract meaningful title from bullet points
                    section_title = section_title.strip("• ").split(":")[0].strip()
                
                extracted_sections.append({
                    "document": section.get('document', os.path.basename(section.get('source', 'unknown'))),
                    "section_title": section_title,
                    "importance_rank": section.get('importance_rank', i),
                    "page_number": section.get('page_number', 1)
                })
        elif 'extracted_sections' in results:
            extracted_sections = results['extracted_sections']
        
        # Convert subsection analysis with better refined text
        subsection_analysis = []
        if 'detailed_analysis' in results:
            for analysis in results['detailed_analysis']:
                # Get more comprehensive refined text
                refined_text = analysis.get('content', analysis.get('refined_text', ''))
                
                # If text is too short, try to get more context
                if len(refined_text) < 100:
                    refined_text = analysis.get('full_text', refined_text)
                
                subsection_analysis.append({
                    "document": analysis.get('document', os.path.basename(analysis.get('source', 'unknown'))),
                    "refined_text": refined_text,
                    "page_number": analysis.get('page', analysis.get('page_number', 1))
                })
        elif 'subsection_analysis' in results:
            subsection_analysis = results['subsection_analysis']
        
        # Create final output structure
        output_data = {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        return output_data
    
    def process_from_file(self, input_file: str, output_file: str, base_dir: str = "./input") -> Dict[str, Any]:
        """
        Process documents from JSON input file and save to output file.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file
            base_dir: Base directory containing PDF files
            
        Returns:
            Processing results
        """
        # Load input JSON
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load input JSON: {e}")
        
        # Process
        results = self.process_json_input(input_data, base_dir)
        
        # Save output
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save output JSON: {e}")
        
        logger.info(f"Results saved to {output_file}")
        return results


def main():
    """CLI interface for JSON processing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Adobe Challenge 1B - JSON Document Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json_processor.py --input challenge_input.json --output results.json
  python json_processor.py --input challenge_input.json --output results.json --base-dir ./documents
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input JSON file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Output JSON file path'
    )
    
    parser.add_argument(
        '--base-dir', '-d',
        type=str,
        default='./input',
        help='Base directory containing PDF files (default: ./input)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    try:
        processor = JSONDocumentProcessor()
        results = processor.process_from_file(args.input, args.output, args.base_dir)
        
        print(f"✅ Processing completed successfully!")
        print(f"📄 Processed {len(results['metadata']['input_documents'])} documents")
        print(f"📊 Extracted {len(results['extracted_sections'])} sections")
        print(f"⏱️ Processing time: {results['metadata']['processing_time_seconds']}s")
        print(f"💾 Results saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
