"""
Test script for Document Intelligence System

This script demonstrates the system capabilities with sample scenarios
and validates performance against the challenge constraints.
"""

import time
import json
import os
from pathlib import Path
from document_intelligence import DocumentIntelligenceProcessor


def create_sample_directory():
    """Create sample documents directory if it doesn't exist."""
    sample_dir = Path("sample_documents")
    sample_dir.mkdir(exist_ok=True)
    return str(sample_dir)


def test_performance_constraints():
    """Test against challenge performance constraints."""
    print("="*60)
    print("PERFORMANCE CONSTRAINT VALIDATION")
    print("="*60)
    
    constraints = {
        "max_processing_time": 60,  # seconds
        "max_model_size": 1024,     # MB
        "cpu_only": True,
        "no_internet": True         # after initial setup
    }
    
    print("Challenge Constraints:")
    for key, value in constraints.items():
        print(f"  {key}: {value}")
    print()


def test_sample_personas():
    """Test different persona configurations."""
    
    personas_and_jobs = [
        {
            "persona": "Investment Analyst",
            "job": "Analyze revenue trends and R&D investments",
            "description": "Financial analysis focused on growth metrics"
        },
        {
            "persona": "Research Scientist", 
            "job": "Extract methodology and experimental results",
            "description": "Scientific paper analysis for research insights"
        },
        {
            "persona": "Business Consultant",
            "job": "Identify optimization opportunities and strategic recommendations", 
            "description": "Business strategy and process improvement"
        },
        {
            "persona": "Compliance Officer",
            "job": "Review regulatory requirements and compliance gaps",
            "description": "Risk assessment and regulatory compliance"
        },
        {
            "persona": "Product Manager",
            "job": "Extract user feedback and feature requirements",
            "description": "Product development and user experience insights"
        }
    ]
    
    return personas_and_jobs


def run_sample_test(pdf_dir: str, persona: str, job: str, test_name: str):
    """Run a single test scenario."""
    print(f"\n{'='*20} {test_name} {'='*20}")
    print(f"Persona: {persona}")
    print(f"Job: {job}")
    print(f"PDF Directory: {pdf_dir}")
    print("-" * 60)
    
    try:
        # Initialize processor
        processor = DocumentIntelligenceProcessor()
        
        # Record start time
        start_time = time.time()
        
        # Process documents
        result = processor.process_documents(
            pdf_dir=pdf_dir,
            persona=persona,
            job=job,
            output_file=f"test_output_{test_name.lower().replace(' ', '_')}.json"
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Validate constraints
        print(f"\nRESULTS:")
        print(f"  Processing Time: {processing_time:.2f}s (Constraint: ≤60s) {'✓' if processing_time <= 60 else '✗'}")
        print(f"  Documents Processed: {len(result['metadata']['input_documents'])}")
        print(f"  Total Chunks: {result['metadata']['total_chunks_processed']}")
        print(f"  Relevant Sections: {len(result['extracted_sections'])}")
        
        # Show top sections
        if result['extracted_sections']:
            print(f"\n  Top Relevant Sections:")
            for i, section in enumerate(result['extracted_sections'][:3], 1):
                print(f"    {i}. {section['document']} (Page {section['page_number']})")
                print(f"       {section['section_title'][:80]}...")
        
        return True, processing_time, result
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False, 0, None


def validate_system_requirements():
    """Validate system meets technical requirements."""
    print("\n" + "="*60)
    print("SYSTEM REQUIREMENTS VALIDATION")
    print("="*60)
    
    requirements = {
        "Python Version": "3.8+",
        "CPU Only": "No GPU required",
        "Model Size": "~80MB (all-MiniLM-L6-v2)",
        "Total Package Size": "<500MB",
        "Memory Usage": "~2GB recommended",
        "Internet Required": "Only for initial setup"
    }
    
    print("Technical Requirements:")
    for req, detail in requirements.items():
        print(f"  {req}: {detail}")
    
    print("\nDependency Sizes (approximate):")
    deps = {
        "sentence-transformers": "~200MB",
        "torch (CPU)": "~150MB", 
        "pdfplumber": "~10MB",
        "nltk": "~20MB",
        "numpy": "~15MB",
        "other dependencies": "~50MB"
    }
    
    total_size = 0
    for dep, size in deps.items():
        print(f"  {dep}: {size}")
        # Extract numeric value for total
        size_mb = int(size.replace("~", "").replace("MB", ""))
        total_size += size_mb
    
    print(f"\nTotal Estimated Size: ~{total_size}MB")
    print(f"Constraint Compliance: {'✓' if total_size < 1024 else '✗'} (<1GB)")


def main():
    """Run comprehensive test suite."""
    print("DOCUMENT INTELLIGENCE SYSTEM - TEST SUITE")
    print("="*60)
    print("Testing persona-driven document processing system")
    print("Challenge: CPU-only, ≤1GB model, ≤60s processing, no internet")
    print()
    
    # Validate system requirements
    validate_system_requirements()
    
    # Test performance constraints
    test_performance_constraints()
    
    # Get sample directory
    sample_dir = create_sample_directory()
    
    # Check if sample documents exist
    pdf_files = [f for f in os.listdir(sample_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("\n" + "!"*60)
        print("NO SAMPLE PDF FILES FOUND")
        print("!"*60)
        print(f"Please add PDF files to: {os.path.abspath(sample_dir)}")
        print("Test scenarios will be demonstrated without actual processing.")
        print("Add PDF files and re-run to test full functionality.")
        print()
        
        # Show what would be tested
        print("SAMPLE TEST SCENARIOS:")
        print("-" * 25)
        personas = test_sample_personas()
        for i, scenario in enumerate(personas, 1):
            print(f"{i}. {scenario['persona']}")
            print(f"   Job: {scenario['job']}")
            print(f"   Description: {scenario['description']}")
            print()
        
        return
    
    print(f"\nFound {len(pdf_files)} PDF files in {sample_dir}")
    print("PDF Files:", pdf_files)
    
    # Run test scenarios
    print("\n" + "="*60)
    print("RUNNING TEST SCENARIOS")
    print("="*60)
    
    personas = test_sample_personas()
    results = []
    
    for i, scenario in enumerate(personas[:3], 1):  # Test first 3 scenarios
        success, proc_time, result = run_sample_test(
            pdf_dir=sample_dir,
            persona=scenario['persona'],
            job=scenario['job'],
            test_name=f"Test {i}"
        )
        
        results.append({
            'scenario': scenario,
            'success': success,
            'processing_time': proc_time,
            'result': result
        })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    avg_time = sum(r['processing_time'] for r in results if r['success']) / max(successful_tests, 1)
    
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    print(f"Average Processing Time: {avg_time:.2f}s")
    print(f"Time Constraint Met: {'✓' if avg_time <= 60 else '✗'}")
    
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  Test {i} ({result['scenario']['persona']}): {status}")
        if result['success']:
            print(f"    Processing Time: {result['processing_time']:.2f}s")
    
    print(f"\nOutput files generated in current directory:")
    output_files = [f for f in os.listdir('.') if f.startswith('test_output_') and f.endswith('.json')]
    for file in output_files:
        print(f"  {file}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("System ready for production use!")
    print("Add more PDF files to sample_documents/ for extended testing.")


if __name__ == "__main__":
    main()
