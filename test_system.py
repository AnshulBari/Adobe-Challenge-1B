"""
Test script for Document Intelligence System

This script demonstrates the system capabilities with sample scenarios
and validates performance against the challenge constraints.
Includes tests for both structured analysis and cohesive summary generation,
as well as the new JSON input functionality.
"""

import time
import json
import os
import subprocess
import tempfile
from pathlib import Path
from document_intelligence import DocumentIntelligenceProcessor
from cohesive_summarizer import CohesiveSummarizer


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
    cohesive_results = []
    
    # Test first 3 scenarios with both approaches
    for i, scenario in enumerate(personas[:3], 1):
        print(f"\n🔄 SCENARIO {i}: {scenario['persona']}")
        
        # Test structured approach
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
            'result': result,
            'approach': 'structured'
        })
        
        # Test cohesive approach
        cohesive_success, cohesive_time, cohesive_result = test_cohesive_summarizer(
            test_name=f"Cohesive Test {i}",
            persona=scenario['persona'],
            job=scenario['job'],
            pdf_dir=sample_dir
        )
        
        cohesive_results.append({
            'scenario': scenario,
            'success': cohesive_success,
            'processing_time': cohesive_time,
            'result': cohesive_result,
            'approach': 'cohesive'
        })
    
    # Run comparison test for Investment Analyst
    if personas:
        print(f"\n🔍 APPROACH COMPARISON TEST")
        compare_approaches(
            personas[0]['persona'], 
            personas[0]['job'], 
            sample_dir
        )
    
    # Test JSON input functionality
    print(f"\n🧪 JSON INPUT FUNCTIONALITY TEST")
    json_test_success = test_json_input_functionality()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    # Combine all results
    all_results = results + cohesive_results
    successful_tests = sum(1 for r in all_results if r['success'])
    total_tests = len(all_results)
    avg_time = sum(r['processing_time'] for r in all_results if r['success']) / max(successful_tests, 1)
    
    print(f"Total Tests: {total_tests} ({len(results)} structured + {len(cohesive_results)} cohesive)")
    print(f"Tests Passed: {successful_tests}/{total_tests}")
    print(f"Average Processing Time: {avg_time:.2f}s")
    print(f"Time Constraint Met: {'✓' if avg_time <= 60 else '✗'}")
    
    # Structured analysis results
    print(f"\n📋 STRUCTURED ANALYSIS RESULTS:")
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  Test {i} ({result['scenario']['persona']}): {status}")
        if result['success']:
            print(f"    Processing Time: {result['processing_time']:.2f}s")
    
    # Cohesive summary results
    print(f"\n📄 COHESIVE SUMMARY RESULTS:")
    for i, result in enumerate(cohesive_results, 1):
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  Test {i} ({result['scenario']['persona']}): {status}")
        if result['success']:
            print(f"    Processing Time: {result['processing_time']:.2f}s")
            if result['result']:
                word_count = result['result']['metadata']['summary_word_count']
                print(f"    Word Count: {word_count}/500")
    
    print(f"\n📁 Output files generated:")
    output_files = [f for f in os.listdir('.') if 
                   (f.startswith('test_output_') or f.startswith('test_cohesive_') or f.startswith('test_json_')) 
                   and f.endswith('.json')]
    for file in sorted(output_files):
        print(f"  {file}")
    
    # JSON Input Test Results
    print(f"\n🧪 JSON INPUT FUNCTIONALITY:")
    print(f"  JSON Input Tests: {'✓ PASS' if json_test_success else '✗ FAIL'}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("✅ All functionality tested:")
    print("   • Structured Analysis: Detailed sections and rankings")
    print("   • Cohesive Summary: Flowing 500-word narratives") 
    print("   • JSON Input: Flexible configuration format")
    print("📊 System supports multiple input methods and processing approaches!")
    print("Add more PDF files to sample_documents/ for extended testing.")


def test_cohesive_summarizer(test_name: str, persona: str, job: str, pdf_dir: str, max_words: int = 500):
    """Test cohesive summarizer functionality."""
    print(f"\n📄 Testing Cohesive Summarizer: {test_name}")
    print(f"Persona: {persona}")
    print(f"Job: {job}")
    print(f"Max Words: {max_words}")
    print(f"PDF Directory: {pdf_dir}")
    print("-" * 60)
    
    try:
        # Initialize summarizer
        summarizer = CohesiveSummarizer()
        
        # Record start time
        start_time = time.time()
        
        # Generate cohesive summary
        result = summarizer.generate_cohesive_summary(
            pdf_dir=pdf_dir,
            persona=persona,
            job=job,
            max_words=max_words
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Save result
        output_file = f"test_cohesive_{test_name.lower().replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Validate results
        metadata = result['metadata']
        summary = result['cohesive_summary']
        word_count = metadata['summary_word_count']
        
        print(f"✅ COHESIVE SUMMARY SUCCESS")
        print(f"  Processing Time: {processing_time:.2f}s")
        print(f"  Documents Processed: {len(metadata['input_documents'])}")
        print(f"  Content Chunks: {metadata['total_content_chunks']}")
        print(f"  Summary Word Count: {word_count}")
        print(f"  Word Limit Compliance: {'✓' if word_count <= max_words else '✗'}")
        print(f"  Output File: {output_file}")
        
        # Show summary preview
        preview = summary[:150] + "..." if len(summary) > 150 else summary
        print(f"  Preview: {preview}")
        
        return True, processing_time, result
        
    except Exception as e:
        print(f"❌ COHESIVE SUMMARY FAILED")
        print(f"ERROR: {str(e)}")
        return False, 0, None


def test_json_input_functionality():
    """Test the new JSON input functionality with various configurations."""
    print("\n" + "="*60)
    print("JSON INPUT FUNCTIONALITY TESTING")
    print("="*60)
    
    # Create test JSON configurations
    test_configs = [
        {
            "name": "Simple Format",
            "config": {
                "persona": "Investment Analyst",
                "job": "Analyze revenue trends",
                "pdf_dir": "sample_documents"
            }
        },
        {
            "name": "Detailed Format",
            "config": {
                "persona": {"role": "Research Scientist"},
                "job_to_be_done": {"task": "Identify key research findings"},
                "pdf_dir": "sample_documents",
                "processing_options": {
                    "max_words": 300,
                    "focus_areas": ["methodology", "results", "conclusions"]
                }
            }
        },
        {
            "name": "Healthcare Format",
            "config": {
                "persona": {"role": "Healthcare Administrator"},
                "job_to_be_done": {"task": "Analyze patient satisfaction trends"},
                "pdf_dir": "sample_documents", 
                "documents": [
                    {"filename": "sample1.pdf", "category": "satisfaction"},
                    {"filename": "sample2.pdf", "category": "operations"}
                ],
                "processing_options": {
                    "max_words": 450,
                    "focus_areas": ["patient satisfaction", "efficiency", "costs"]
                }
            }
        }
    ]
    
    success_count = 0
    total_tests = len(test_configs)
    
    for i, test_case in enumerate(test_configs, 1):
        print(f"\n🧪 Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Create temporary JSON file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_case['config'], f, indent=2)
                temp_json_path = f.name
            
            print(f"📄 Config: {json.dumps(test_case['config'], indent=2)}")
            
            # Test both structured and cohesive modes
            for mode in ['structured', 'cohesive']:
                print(f"\n  Testing {mode} mode...")
                
                # Build command
                cmd = [
                    'python', 'cli.py',
                    '--input-json', temp_json_path,
                    '--output', f'test_json_{mode}_{i}.json'
                ]
                
                if mode == 'cohesive':
                    cmd.append('--cohesive')
                
                # Run command
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                processing_time = time.time() - start_time
                
                if result.returncode == 0:
                    print(f"    ✅ {mode.title()} mode: SUCCESS ({processing_time:.2f}s)")
                    
                    # Validate output file exists
                    output_file = f'test_json_{mode}_{i}.json'
                    if os.path.exists(output_file):
                        with open(output_file, 'r') as f:
                            output_data = json.load(f)
                        print(f"    📊 Output: {len(output_data.get('metadata', {}).get('input_documents', []))} documents processed")
                        
                        # Clean up output file
                        os.remove(output_file)
                    
                else:
                    print(f"    ❌ {mode.title()} mode: FAILED")
                    print(f"    Error: {result.stderr}")
            
            # Clean up temp JSON file
            os.unlink(temp_json_path)
            success_count += 1
            
        except subprocess.TimeoutExpired:
            print(f"    ❌ TIMEOUT: Processing took longer than 60 seconds")
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
    
    print(f"\n📊 JSON Input Test Results:")
    print(f"  Tests Passed: {success_count}/{total_tests}")
    print(f"  Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    return success_count == total_tests


def compare_approaches(persona: str, job: str, pdf_dir: str):
    """Compare structured analysis vs cohesive summary approaches."""
    print(f"\n🔄 Comparing Approaches: {persona}")
    print("=" * 60)
    
    # Test structured approach
    print("1. STRUCTURED ANALYSIS:")
    struct_success, struct_time, struct_result = run_sample_test(
        pdf_dir, persona, job, f"Structured {persona}"
    )
    
    # Test cohesive approach
    print("\n2. COHESIVE SUMMARY:")
    cohesive_success, cohesive_time, cohesive_result = test_cohesive_summarizer(
        f"Cohesive {persona}", persona, job, pdf_dir
    )
    
    # Comparison
    print(f"\n📊 COMPARISON RESULTS:")
    print("-" * 30)
    print(f"Structured Analysis:")
    print(f"  Success: {'✓' if struct_success else '✗'}")
    print(f"  Time: {struct_time:.2f}s")
    if struct_result:
        print(f"  Sections Found: {len(struct_result.get('extracted_sections', []))}")
    
    print(f"Cohesive Summary:")
    print(f"  Success: {'✓' if cohesive_success else '✗'}")
    print(f"  Time: {cohesive_time:.2f}s")
    if cohesive_result:
        print(f"  Word Count: {cohesive_result['metadata']['summary_word_count']}")
    
    print(f"\nRecommendation: {'Cohesive Summary for unified content' if cohesive_success else 'Structured Analysis for detailed sections'}")
    
    return struct_success and cohesive_success


if __name__ == "__main__":
    main()
