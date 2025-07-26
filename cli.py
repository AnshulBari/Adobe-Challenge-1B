"""
Command Line Interface for Adobe Challenge 1B Document Intelligence System
Supports both structured analysis and cohesive summary generation
"""

import argparse
import json
import os
import sys
from pathlib import Path
from document_intelligence import DocumentIntelligenceProcessor
from cohesive_summarizer import CohesiveSummarizer


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}


def parse_json_input(json_path: str) -> tuple:
    """
    Parse JSON input file and extract persona, job, and pdf_dir.
    
    Supports multiple JSON formats:
    - {"persona": "string"} or {"persona": {"role": "string"}}
    - {"job": "string"} or {"job_to_be_done": {"task": "string"}}
    - {"pdf_dir": "path"} or inferred from documents array
    
    Returns:
        tuple: (persona, job, pdf_dir, metadata)
    """
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON configuration file '{json_path}' not found.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in '{json_path}': {str(e)}")
    
    # Extract persona
    persona = None
    if 'persona' in config:
        if isinstance(config['persona'], dict):
            persona = config['persona'].get('role') or config['persona'].get('name')
        else:
            persona = str(config['persona'])
    
    # Extract job
    job = None
    if 'job_to_be_done' in config:
        if isinstance(config['job_to_be_done'], dict):
            job = config['job_to_be_done'].get('task') or config['job_to_be_done'].get('description')
        else:
            job = str(config['job_to_be_done'])
    elif 'job' in config:
        job = str(config['job'])
    
    # Extract PDF directory
    pdf_dir = config.get('pdf_dir', '.')
    
    # Additional metadata
    metadata = {
        'documents': config.get('documents', []),
        'processing_options': config.get('processing_options', {}),
        'focus_areas': config.get('processing_options', {}).get('focus_areas', [])
    }
    
    return persona, job, pdf_dir, metadata


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
        description="Adobe Challenge 1B - Document Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Structured analysis with command line arguments
  python cli.py --pdf-dir documents --persona "Investment Analyst" --job "Analyze revenue trends"
  
  # Cohesive summary with command line arguments
  python cli.py --pdf-dir documents --persona "Investment Analyst" --job "Analyze revenue trends" --cohesive
  
  # Using JSON configuration file
  python cli.py --input-json config.json --pdf-dir documents --cohesive
  
  # JSON configuration overrides PDF directory
  python cli.py --input-json config.json
  
  # List available personas and jobs
  python cli.py --list-personas
  python cli.py --list-jobs

JSON Configuration Format:
  {
    "persona": {"role": "Investment Analyst"},
    "job_to_be_done": {"task": "Analyze revenue trends"},
    "pdf_dir": "sample_documents",
    "documents": [
      {"filename": "doc1.pdf"},
      {"filename": "doc2.pdf"}
    ]
  }
        """
    )
    
    parser.add_argument(
        '--input-json',
        type=str,
        help='JSON configuration file with documents, persona, and job details'
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
        '--cohesive',
        action='store_true',
        help='Generate cohesive 500-word summary instead of structured analysis'
    )
    
    parser.add_argument(
        '--max-words',
        type=int,
        default=500,
        help='Maximum words in cohesive summary (default: 500)'
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
    
    # Process input - either from JSON file or command line arguments
    pdf_dir = None
    persona = None
    job = None
    json_metadata = {}
    
    if args.input_json:
        # Load from JSON configuration file
        try:
            persona, job, pdf_dir, json_metadata = parse_json_input(args.input_json)
            
            # Command line PDF directory overrides JSON
            if args.pdf_dir:
                pdf_dir = args.pdf_dir
            
            print(f"📥 Loaded configuration from: {args.input_json}")
            print(f"👤 Persona: {persona}")
            print(f"🎯 Job: {job}")
            print(f"📂 PDF Directory: {pdf_dir}")
            
            # Show additional info if available
            if json_metadata.get('documents'):
                print(f"📄 Configured documents: {len(json_metadata['documents'])}")
            if json_metadata.get('focus_areas'):
                print(f"🎯 Focus areas: {', '.join(json_metadata['focus_areas'][:3])}...")
            
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing JSON configuration: {str(e)}")
            sys.exit(1)
    else:
        # Use command line arguments
        pdf_dir = args.pdf_dir
        persona = args.persona
        job = args.job
    
    # Validate required arguments for processing
    if not all([pdf_dir, persona, job]):
        parser.print_help()
        print("\nError: Either use --input-json OR provide --pdf-dir, --persona, and --job.")
        print("Use --list-personas and --list-jobs to see available options.")
        sys.exit(1)
    
    # Validate inputs
    if not validate_inputs(pdf_dir, persona, job):
        sys.exit(1)
    
    # Configure logging
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Process documents
    try:
        # Get max_words from JSON config if available, otherwise use command line arg
        max_words = args.max_words
        if args.input_json and 'max_words' in json_metadata.get('processing_options', {}):
            max_words = json_metadata['processing_options']['max_words']
        
        if args.cohesive:
            # Use cohesive summarizer
            print("🔄 Initializing Cohesive Summarizer...")
            print(f"📄 Generating cohesive summary with persona: {persona}")
            print(f"🎯 Job: {job}")
            print(f"📊 Max words: {max_words}")
            
            summarizer = CohesiveSummarizer()
            result = summarizer.generate_cohesive_summary(
                pdf_dir=pdf_dir,
                persona=persona,
                job=job,
                max_words=max_words
            )
            
            print(f"✅ Generated cohesive summary: {result['metadata']['summary_word_count']} words")
            
        else:
            # Use original structured processor
            print("🔄 Initializing Document Intelligence Processor...")
            print(f"📄 Processing documents with persona: {persona}")
            print(f"🎯 Job: {job}")
            
            processor = DocumentIntelligenceProcessor()
            result = processor.process_documents(
                pdf_dir=pdf_dir,
                persona=persona,
                job=job,
                output_file=args.output
            )
            
            print(f"✅ Processed {len(result['extracted_sections'])} sections")
        
        # Save results
        print(f"\n💾 Saving results to: {args.output}")
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Display results summary
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        
        metadata = result['metadata']
        print(f"📁 Documents Processed: {len(metadata['input_documents'])}")
        print(f"⏱️  Processing Time: {metadata['processing_time_seconds']} seconds")
        print(f"💾 Results saved to: {args.output}")
        
        if args.cohesive:
            # Show cohesive summary details
            print(f"📝 Summary Word Count: {metadata['summary_word_count']}")
            print(f"🔢 Total Content Chunks: {metadata['total_content_chunks']}")
            
            # Show preview
            summary = result['cohesive_summary']
            preview = summary[:200] + "..." if len(summary) > 200 else summary
            print(f"\n📖 Summary Preview:")
            print("-" * 40)
            print(preview)
            
        else:
            # Show structured analysis details
            print(f"🔍 Total Chunks: {metadata['total_chunks_processed']}")
            print(f"📋 Relevant Sections Found: {len(result['extracted_sections'])}")
            
            # Show top sections if found
            if result['extracted_sections']:
                print(f"\n🏆 Top {len(result['extracted_sections'])} Relevant Sections:")
                print("-" * 40)
                for section in result['extracted_sections']:
                    print(f"  Rank {section['importance_rank']}: {section['document']} (Page {section['page_number']})")
                    print(f"    {section['section_title']}")
        
        print(f"\n📂 Full results available in: {args.output}")
        
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
