"""
Command Line Interface for Document Intelligence System

Provides an easy-to-use CLI for processing documents with different personas and jobs.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from document_intelligence import DocumentIntelligenceProcessor


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}


def list_available_personas(config: dict):
    """Display available personas from config."""
    personas = config.get('personas', {})
    if personas:
        print("\nAvailable Personas:")
        print("-" * 20)
        for key, value in personas.items():
            print(f"  {key}: {value['name']}")
            print(f"    Keywords: {', '.join(value['keywords'][:5])}...")
    else:
        print("No predefined personas available.")


def list_sample_jobs(config: dict):
    """Display sample job descriptions from config."""
    jobs = config.get('sample_jobs', {})
    if jobs:
        print("\nSample Jobs:")
        print("-" * 12)
        for key, value in jobs.items():
            print(f"  {key}: {value}")
    else:
        print("No sample jobs available.")


def validate_inputs(pdf_dir: str, persona: str, job: str) -> bool:
    """Validate user inputs."""
    # Check if PDF directory exists
    if not os.path.exists(pdf_dir):
        print(f"Error: PDF directory '{pdf_dir}' does not exist.")
        return False
    
    # Check if directory contains PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"Error: No PDF files found in '{pdf_dir}'.")
        return False
    
    # Check if persona and job are provided
    if not persona.strip():
        print("Error: Persona cannot be empty.")
        return False
    
    if not job.strip():
        print("Error: Job description cannot be empty.")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Persona-Driven Document Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --pdf-dir ./documents --persona "Investment Analyst" --job "Analyze revenue trends"
  python cli.py --pdf-dir ./reports --persona "Research Scientist" --job "Extract methodology" --output results.json
  python cli.py --list-personas
  python cli.py --list-jobs
        """
    )
    
    parser.add_argument(
        '--pdf-dir', 
        type=str,
        help='Directory containing PDF files to process'
    )
    
    parser.add_argument(
        '--persona',
        type=str,
        help='Target persona (e.g., "Investment Analyst", "Research Scientist")'
    )
    
    parser.add_argument(
        '--job',
        type=str,
        help='Job to be done (e.g., "Analyze revenue trends and R&D investments")'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output.json',
        help='Output JSON file path (default: output.json)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    
    parser.add_argument(
        '--list-personas',
        action='store_true',
        help='List available personas from config'
    )
    
    parser.add_argument(
        '--list-jobs',
        action='store_true',
        help='List sample job descriptions from config'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Handle list commands
    if args.list_personas:
        list_available_personas(config)
        return
    
    if args.list_jobs:
        list_sample_jobs(config)
        return
    
    # Validate required arguments for processing
    if not all([args.pdf_dir, args.persona, args.job]):
        parser.print_help()
        print("\nError: --pdf-dir, --persona, and --job are required for processing.")
        print("Use --list-personas and --list-jobs to see available options.")
        sys.exit(1)
    
    # Validate inputs
    if not validate_inputs(args.pdf_dir, args.persona, args.job):
        sys.exit(1)
    
    # Process documents
    try:
        print("Initializing Document Intelligence Processor...")
        processor = DocumentIntelligenceProcessor()
        
        print(f"\nProcessing Configuration:")
        print(f"  PDF Directory: {args.pdf_dir}")
        print(f"  Persona: {args.persona}")
        print(f"  Job: {args.job}")
        print(f"  Output File: {args.output}")
        
        # Run processing
        result = processor.process_documents(
            pdf_dir=args.pdf_dir,
            persona=args.persona,
            job=args.job,
            output_file=args.output
        )
        
        # Display results summary
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        
        metadata = result['metadata']
        print(f"Documents Processed: {len(metadata['input_documents'])}")
        print(f"Processing Time: {metadata['processing_time_seconds']} seconds")
        print(f"Total Chunks: {metadata['total_chunks_processed']}")
        print(f"Relevant Sections Found: {len(result['extracted_sections'])}")
        print(f"Results saved to: {args.output}")
        
        # Show top sections if found
        if result['extracted_sections']:
            print(f"\nTop {len(result['extracted_sections'])} Relevant Sections:")
            print("-" * 40)
            for section in result['extracted_sections']:
                print(f"  Rank {section['importance_rank']}: {section['document']} (Page {section['page_number']})")
                print(f"    {section['section_title']}")
        
        print(f"\nFull results available in: {args.output}")
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
