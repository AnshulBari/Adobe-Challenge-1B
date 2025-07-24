"""
Setup script for Document Intelligence System

Automates the installation and initial configuration process.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """Print setup banner."""
    print("="*70)
    print("DOCUMENT INTELLIGENCE SYSTEM - SETUP")
    print("="*70)
    print("Persona-driven document processing with CPU-only constraints")
    print("Model size ≤1GB | Processing time ≤60s | No internet required")
    print()


def check_python_version():
    """Check if Python version meets requirements."""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8+ required")
        print("Please upgrade Python and try again.")
        return False
    
    print("✅ Python version OK")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n" + "-"*50)
    print("INSTALLING DEPENDENCIES")
    print("-"*50)
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt", "--upgrade"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def download_nltk_data():
    """Download required NLTK data."""
    print("\n" + "-"*50)
    print("DOWNLOADING NLTK DATA")
    print("-"*50)
    
    try:
        import nltk
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False


def test_model_loading():
    """Test loading the embedding model."""
    print("\n" + "-"*50)
    print("TESTING MODEL LOADING")
    print("-"*50)
    
    try:
        print("Loading sentence transformer model (first time may take a while)...")
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Model loaded successfully")
        
        # Test encoding
        test_text = "This is a test sentence."
        embedding = model.encode([test_text])
        print(f"✅ Encoding test successful (embedding shape: {embedding.shape})")
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False


def create_sample_directories():
    """Create necessary directories."""
    print("\n" + "-"*50)
    print("CREATING DIRECTORIES")
    print("-"*50)
    
    directories = [
        "sample_documents",
        "output", 
        "logs"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}/")
    
    return True


def run_system_test():
    """Run basic system test."""
    print("\n" + "-"*50)
    print("RUNNING SYSTEM TEST")
    print("-"*50)
    
    try:
        from document_intelligence import DocumentIntelligenceProcessor
        
        print("Initializing processor...")
        processor = DocumentIntelligenceProcessor()
        print("✅ Processor initialized successfully")
        
        # Test with empty directory (should handle gracefully)
        result = processor.process_documents(
            pdf_dir="sample_documents",
            persona="Test Analyst",
            job="System validation test"
        )
        
        if "error" in result["metadata"]:
            print("✅ Empty directory handled correctly")
        else:
            print("✅ System test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False


def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*70)
    print("SETUP COMPLETE - USAGE INSTRUCTIONS")
    print("="*70)
    
    print("""
1. Add PDF files to the sample_documents/ directory

2. Run using Command Line Interface:
   python cli.py --pdf-dir sample_documents --persona "Investment Analyst" --job "Analyze revenue trends"

3. Run using Python API:
   from document_intelligence import DocumentIntelligenceProcessor
   processor = DocumentIntelligenceProcessor()
   result = processor.process_documents("sample_documents", "Analyst", "Task")

4. List available personas:
   python cli.py --list-personas

5. Run comprehensive tests:
   python test_system.py

6. View configuration:
   Edit config.json to customize personas and settings

NEXT STEPS:
- Add PDF documents to sample_documents/
- Try the example commands above
- Check README.md for detailed documentation
""")


def main():
    """Main setup function."""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    # Setup steps
    steps = [
        ("Installing Dependencies", install_dependencies),
        ("Downloading NLTK Data", download_nltk_data),
        ("Testing Model Loading", test_model_loading),
        ("Creating Directories", create_sample_directories),
        ("Running System Test", run_system_test),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except KeyboardInterrupt:
            print("\n\n❌ Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Summary
    print("\n" + "="*70)
    print("SETUP SUMMARY")
    print("="*70)
    
    if failed_steps:
        print(f"❌ Setup completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease review the errors above and try again.")
        print("You may need to install dependencies manually.")
    else:
        print("✅ Setup completed successfully!")
        print("All components installed and tested.")
        
        # Get system info
        try:
            import torch
            print(f"PyTorch version: {torch.__version__}")
            print(f"CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            print("PyTorch: Not detected (will be installed with sentence-transformers)")
        
        print_usage_instructions()


if __name__ == "__main__":
    main()
