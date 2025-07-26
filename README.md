# 🧠 Adobe Challenge 1B - Document Intelligence System

> **Persona-driven document processing that extracts relevant content based on user roles and tasks**

[![Docker](https://img.shield## 📁 Project Structure

```
Adobe-Cprint(f"Top sections: {len(result['extracted_sections'])}")
```

## 📊 JSON Interface Specification

### Input Format

The JSON interface accepts structured input for batch processing and standardized workflows:

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case",
    "description": "Optional description"
  },
  "documents": [
    {"filename": "doc.pdf", "title": "Document Title"}
  ],
  "persona": {"role": "User Persona"},
  "job_to_be_done": {"task": "Use case description"}
}
```

**Example Input** (Travel Planning):
```json
{
  "challenge_info": {
    "challenge_id": "round_1b_002",
    "test_case_name": "travel_planner",
    "description": "France Travel Planning Challenge"
  },
  "documents": [
    {"filename": "South of France - Cities.pdf", "title": "South of France - Cities"},
    {"filename": "South of France - Cuisine.pdf", "title": "South of France - Cuisine"},
    {"filename": "South of France - Things to Do.pdf", "title": "South of France - Things to Do"}
  ],
  "persona": {"role": "Travel Planner"},
  "job_to_be_done": {"task": "Plan a trip of 4 days for a group of 10 college friends."}
}
```

### Output Format

The system produces standardized JSON output with metadata and extracted insights:

```json
{
  "metadata": {
    "input_documents": ["list of processed files"],
    "persona": "User Persona",
    "job_to_be_done": "Task description", 
    "processing_timestamp": "ISO timestamp",
    "processing_time_seconds": 28.45
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Section Title",
      "importance_rank": 1,
      "page_number": 1,
      "relevance_score": 0.892
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf", 
      "refined_text": "Most relevant extracted content...",
      "page_number": 1,
      "relevance_score": 0.892
    }
  ]
}
```

### JSON Processing Commands

```bash
# Process with JSON input/output
python json_processor.py -i input/challenge_input.json -o output/results.json

# Docker JSON processing
docker-compose --profile json up json-processor

# Verbose mode for debugging
python json_processor.py -i input/test.json -o output/test.json --verbose
```

## 📋 Examples

### Example 1: Prompt Engineering Student
```bash
docker-compose run --rm document-intelligence python cli.py \
  --pdf-dir /app/input \
  --persona "Prompt Engineer Aspiring Student" \
  --job "Extract relevant sections for learning prompt engineering" \
  --output /app/output/results.json
```

**Input**: Gemini for Google Workspace Prompting Guide 101 (5.26 MB)  
**Output**: 5 relevant sections focusing on prompt design fundamentals  
**Processing Time**: ~28 seconds

### Example 2: Investment Analyst Core Application
│   ├── cli.py                     # Command line interface
│   ├── cohesive_summarizer.py     # ML processing logic  
│   └── document_intelligence.py   # Document processor class
├── 🐳 Docker Configuration
│   ├── Dockerfile                 # Container configuration
│   ├── Dockerfile.prod            # Production variant
│   ├── docker-compose.yml         # Service orchestration
│   └── .dockerignore             # Build exclusions
├── 📁 Data Directories
│   ├── input/                     # PDF input files
│   └── output/                    # Processing results (results.json)
├── 🛠️ Development & Testing
│   ├── requirements.txt           # Python dependencies
│   ├── setup.py                  # Package setup
│   ├── test_system.py            # System tests
│   └── validate_system.py        # Validation scripts
├── 📚 Documentation
│   ├── README.md                 # This file
│   ├── DOCKER.md                 # Docker usage guide
│   ├── PROJECT_SUMMARY.md        # Project overview
│   ├── CHANGELOG.md              # Version history
│   └── LICENSE                   # MIT License
└── 🔧 Configuration
    ├── .gitignore                # Git exclusions
    └── .dockerignore             # Docker build exclusions
```Docker-Ready-blue?logo=docker)](./Dockerfile)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](./requirements.txt)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)

## 🎯 Adobe Challenge 1B Compliance

**✅ All Requirements Met:**
- **Model Size**: ~90MB (all-MiniLM-L6-v2) - **well under 1GB limit**
- **Processing Time**: <30s for typical documents  
- **CPU-Only**: No GPU dependencies required
- **Offline**: Works without internet after initial setup

## 🚀 Quick Start

### JSON Interface (Recommended)

The Adobe Challenge 1B system now supports a standardized JSON interface for streamlined processing:

```bash
# Clone the repository
git clone https://github.com/AnshulBari/Adobe-Challenge-1B.git
cd Adobe-Challenge-1B

# Place your PDF files in the input directory
mkdir input output

# Create a challenge input JSON file
cat > input/challenge_input.json << 'EOF'
{
  "challenge_info": {
    "challenge_id": "round_1b_001",
    "test_case_name": "analysis_task",
    "description": "Document analysis challenge"
  },
  "documents": [
    {"filename": "your-document.pdf", "title": "Your Document"}
  ],
  "persona": {"role": "Data Analyst"},
  "job_to_be_done": {"task": "Extract key insights and trends"}
}
EOF

# Run with Docker (JSON mode)
docker-compose --profile json up json-processor

# Or run locally
python json_processor.py -i input/challenge_input.json -o output/results.json

# View results
cat output/results.json
```

### Using Docker (Legacy CLI)

```bash
# Clone the repository
git clone https://github.com/AnshulBari/Adobe-Challenge-1B.git
cd Adobe-Challenge-1B

# Place your PDF files in the input directory
mkdir input
cp your-document.pdf input/

# Run the application
docker-compose run --rm document-intelligence python cli.py \
  --pdf-dir /app/input \
  --persona "Your Role" \
  --job "Your specific task" \
  --output /app/output/results.json

# View results
cat output/results.json
```

### Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# JSON Processing (recommended)
python json_processor.py --input ./input/challenge_input.json --output ./output/results.json

# CLI Processing (legacy)
python cli.py --pdf-dir ./input --persona "Data Analyst" --job "Extract insights" --output ./output/results.json
```

# Run the application
python cli.py --pdf-dir ./input --persona "Data Analyst" --job "Extract insights" --output ./output/results.json
```

## 🔧 Key Features

- **Persona-Driven Analysis**: Tailors content extraction based on specific user roles and tasks
- **Lightweight Architecture**: Uses all-MiniLM-L6-v2 model (80MB) for efficient processing
- **CPU-Only Operation**: No GPU required, works on standard hardware
- **Fast Processing**: Optimized for <60 seconds processing time
- **Dual-Stage Filtering**: Chunk-level and sentence-level relevance ranking
- **Batch Processing**: Efficient embedding computation
- **Comprehensive Output**: Structured JSON with metadata and refined insights

## 🏗️ Architecture

### Text Extraction & Chunking
- Uses `pdfplumber` for reliable PDF text extraction
- Page-level granularity with paragraph boundary splitting
- Preserves document context without complex layout analysis

### Embedding & Relevance Ranking
- Leverages Sentence Transformers with all-MiniLM-L6-v2 model
- Combines persona and job into unified query
- Cosine similarity ranking for top-5 chunk selection

### Sub-section Refinement
- NLTK punkt tokenizer for sentence splitting
- Re-ranks sentences within top chunks
- Extracts top 2 sentences as refined insights

## 📋 Requirements

### System Requirements
- Python 3.8+
- CPU-only (no GPU required)
- ~90MB for model (all-MiniLM-L6-v2)
- ~500MB total disk space for dependencies  
- 2GB+ RAM recommended

### Adobe Challenge 1B Constraints ✅
- **✅ Model Size**: ~90MB (well under 1GB limit)
- **✅ Processing Time**: <60s for typical documents
- **✅ CPU-Only**: No GPU dependencies
- **✅ Offline**: Works without internet after setup

### Dependencies
```
pdfplumber==0.10.0
sentence-transformers==2.2.2
nltk==3.8.1
numpy==1.24.3
PyPDF2==3.0.1
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Challenge-1B
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download NLTK data** (automatically handled on first run)
```python
import nltk
nltk.download('punkt')
```

### Basic Usage

#### Command Line Interface

**Traditional Command Line Arguments:**
```bash
# Structured analysis (detailed sections)
python cli.py --pdf-dir ./documents --persona "Investment Analyst" --job "Analyze revenue trends and R&D investments"

# Cohesive summary (flowing narrative)
python cli.py --pdf-dir ./documents --persona "Investment Analyst" --job "Analyze revenue trends" --cohesive

# Custom word limit for cohesive summary
python cli.py --pdf-dir ./documents --persona "Research Scientist" --job "Extract key findings" --cohesive --max-words 300
```

**New JSON Input Support:**
```bash
# Use JSON configuration file
python cli.py --input-json config.json --cohesive

# JSON config with directory override
python cli.py --input-json config.json --pdf-dir ./custom_docs

# List available personas and jobs
python cli.py --list-personas
python cli.py --list-jobs
```

**JSON Configuration Format:**
```json
{
  "persona": {"role": "Investment Analyst"},
  "job_to_be_done": {"task": "Analyze revenue trends and R&D investments"},
  "pdf_dir": "sample_documents",
  "documents": [
    {"filename": "financial_report_q1.pdf"},
    {"filename": "annual_report.pdf"}
  ],
  "processing_options": {
    "max_words": 500,
    "focus_areas": ["revenue growth", "R&D spending", "profitability"]
  }
}
```

**Flexible JSON Formats Supported:**
```json
// Simple format
{
  "persona": "Investment Analyst",
  "job": "Analyze revenue trends",
  "pdf_dir": "documents"
}

// Detailed format  
{
  "persona": {"role": "Research Scientist"},
  "job_to_be_done": {"task": "Extract methodology"},
  "processing_options": {"max_words": 300}
}
```

#### Python API
```python
from document_intelligence import DocumentIntelligenceProcessor

# Initialize processor
processor = DocumentIntelligenceProcessor()

# Process documents
result = processor.process_documents(
    pdf_dir="./sample_documents",
    persona="Investment Analyst", 
    job="Analyze revenue trends and R&D investments",
    output_file="output.json"
)

# Access results
print(f"Processing time: {result['metadata']['processing_time_seconds']} seconds")
print(f"Top sections: {len(result['extracted_sections'])}")
```

## � Examples

### Example 1: Prompt Engineering Student
```bash
docker-compose run --rm document-intelligence python cli.py \
  --pdf-dir /app/input \
  --persona "Prompt Engineer Aspiring Student" \
  --job "Extract relevant sections for learning prompt engineering" \
  --output /app/output/results.json
```

**Input**: Gemini for Google Workspace Prompting Guide 101 (5.26 MB)  
**Output**: 5 relevant sections focusing on prompt design fundamentals  
**Processing Time**: ~28 seconds

### Example 2: Investment Analyst
```bash
python cli.py \
  --pdf-dir ./input \
  --persona "Investment Analyst" \
  --job "Analyze revenue trends and financial metrics" \
  --output ./output/analysis.json
```

### Example 3: Research Scientist
```bash
python cli.py \
  --pdf-dir ./research_papers \
  --persona "Research Scientist" \
  --job "Extract methodology and experimental results" \
  --output ./output/research_insights.json
```

## �📁 Project Structure

```
Challenge-1B/
├── document_intelligence.py    # Main processor class
├── cli.py                     # Command line interface
├── config.json               # Configuration and personas
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── sample_documents/         # Sample PDF files (create this folder)
```

## ⚙️ Configuration

The `config.json` file contains:

- **Model Configuration**: Embedding model settings and batch sizes
- **Processing Configuration**: Chunk limits, sentence extraction parameters
- **Predefined Personas**: Investment Analyst, Research Scientist, Business Consultant, Compliance Officer
- **Sample Jobs**: Common task templates for different use cases

### Adding Custom Personas

Edit `config.json` to add new personas:

```json
{
  "personas": {
    "your_persona": {
      "name": "Your Custom Persona",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }
  }
}
```

## 📊 Output Format

The system generates structured JSON output:

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Investment Analyst",
    "job_to_be_done": "Analyze revenue trends",
    "processing_timestamp": "2025-01-20T10:30:00Z",
    "processing_time_seconds": 45.2,
    "total_chunks_processed": 234,
    "top_chunks_selected": 5
  },
  "extracted_sections": [
    {
      "document": "financial_report.pdf",
      "page_number": 5,
      "section_title": "Revenue Analysis Q4 2024 Financial Performance",
      "importance_rank": 1
    }
  ],
  "sub_section_analysis": [
    {
      "document": "financial_report.pdf", 
      "section_title": "Revenue Analysis Q4 2024 Financial Performance",
      "refined_text": "Revenue increased by 15% year-over-year. R&D investments totaled $2.3M in Q4.",
      "page_number_constraints": 5
    }
  ]
}
```

## 🎭 Supported Personas

### Investment Analyst
- **Focus**: Financial performance, revenue trends, R&D investments
- **Keywords**: Revenue, profit, growth, investment, ROI, market performance

### Research Scientist  
- **Focus**: Methodology, experimental results, data analysis
- **Keywords**: Methodology, results, hypothesis, experiment, data, conclusion

### Business Consultant
- **Focus**: Strategy, process optimization, recommendations
- **Keywords**: Strategy, optimization, efficiency, process, solution

### Compliance Officer
- **Focus**: Regulations, policies, risk assessment
- **Keywords**: Regulation, compliance, policy, requirement, audit, risk

## 🔧 Advanced Usage

### Batch Processing Multiple Jobs

```python
processor = DocumentIntelligenceProcessor()

jobs = [
    ("Investment Analyst", "Analyze revenue trends"),
    ("Research Scientist", "Extract methodology"), 
    ("Compliance Officer", "Identify compliance requirements")
]

for persona, job in jobs:
    result = processor.process_documents(
        pdf_dir="./documents",
        persona=persona,
        job=job,
        output_file=f"output_{persona.lower().replace(' ', '_')}.json"
    )
```

### Custom Model Configuration

```python
# Use different embedding model
processor = DocumentIntelligenceProcessor(model_name='all-mpnet-base-v2')

# Process with custom parameters
result = processor.process_documents(
    pdf_dir="./documents",
    persona="Custom Analyst",
    job="Custom analysis task"
)
```

## 📈 Performance Optimization

### Processing Speed
- **Batch Embedding**: Processes multiple texts simultaneously
- **Selective Refinement**: Only processes top-ranked chunks
- **Efficient Models**: Uses lightweight, CPU-optimized models

### Memory Usage
- **Lazy Loading**: Models loaded only when needed
- **Chunk Processing**: Processes documents in manageable chunks
- **Clean-up**: Automatic memory management

### Accuracy Improvements
- **Dual-Stage Ranking**: Chunk → sentence refinement
- **Context Preservation**: Maintains document structure
- **Semantic Similarity**: Uses state-of-the-art embeddings

## 🧪 Testing

### Sample Test Cases

1. **Financial Documents**: Test with annual reports, financial statements
2. **Research Papers**: Process academic papers, research articles  
3. **Business Reports**: Analyze strategy documents, market reports
4. **Compliance Documents**: Review policies, regulatory filings

### Validation Metrics
- **Processing Time**: <60 seconds for 5 documents (20 pages each)
- **Model Size**: <500MB total including dependencies
- **Accuracy**: Relevant sections ranked in top 5 for test personas

## 🔍 Troubleshooting

### Common Issues

1. **No PDF files found**
   - Check directory path exists
   - Verify PDF files are present
   - Ensure proper file permissions

2. **Model download fails**
   - Check internet connection for initial download
   - Verify disk space (>500MB available)
   - Try manual model download

3. **Slow processing**
   - Reduce batch size in config
   - Check available RAM
   - Consider fewer/smaller documents

4. **Poor relevance ranking**
   - Refine persona descriptions
   - Adjust job descriptions
   - Check document content quality

### Debug Mode

```bash
python cli.py --pdf-dir ./docs --persona "Analyst" --job "Analysis" --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Sentence Transformers**: For efficient embedding models
- **pdfplumber**: For reliable PDF text extraction
- **NLTK**: For natural language processing utilities
- **NumPy**: For fast numerical computations

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

---

**Built for Adobe Challenge 1B - Persona-Driven Document Intelligence**
