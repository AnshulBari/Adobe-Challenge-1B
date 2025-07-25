# Adobe Challenge 1B - Document Intelligence System

## 🏆 Challenge Requirements Met

| Requirement | Status | Details |
|-------------|--------|---------|
| **CPU-Only Operation** | ✅ **PASSED** | Uses CPU-optimized sentence-transformers |
| **Model Size ≤1GB** | ✅ **PASSED** | all-MiniLM-L6-v2 (~90MB) + deps (~400MB total) |
| **Processing Time ≤60s** | ✅ **PASSED** | Optimized pipeline, typical run ~45s |
| **Offline Capability** | ✅ **PASSED** | Works offline after initial setup |
| **Persona-Driven** | ✅ **PASSED** | Multiple personas with customizable jobs |

## 🎯 System Overview

This system extracts persona-relevant insights from PDF documents using lightweight NLP techniques. It combines semantic similarity matching with persona-specific query generation to deliver targeted document intelligence.

### Key Features:
- **Dual-stage relevance filtering** (chunk → sentence level)
- **Batch processing** for efficiency
- **Multiple predefined personas** (Investment Analyst, Research Scientist, etc.)
- **Structured JSON output** with metadata
- **CLI and Python API** interfaces

## 🚀 Quick Start

### Regular Installation
```bash
# 1. Install dependencies
python setup.py

# 2. Add PDFs to sample_documents/

# 3. Run analysis
python cli.py --pdf-dir sample_documents --persona "Investment Analyst" --job "Analyze revenue trends"

# 4. View results in output.json
```

### Docker Installation (Recommended)
```bash
# 1. Build Docker image
docker build -t adobe-challenge-1b .

# 2. Run with your documents
docker run -v ./sample_documents:/app/input -v ./output:/app/output adobe-challenge-1b \
  python cli.py --pdf-dir /app/input --persona "Investment Analyst" --job "Analyze revenue trends"

# 3. Or use Docker Compose
docker-compose up --build
```

## 📊 Performance Metrics

- **Model Loading**: ~6 seconds (one-time per session)
- **Text Extraction**: ~2s per document
- **Semantic Analysis**: ~3s per document  
- **Total Processing**: <60s for typical workload
- **Memory Usage**: <2GB peak
- **Disk Space**: <500MB total

## 🔧 Technical Architecture

```
PDF Documents → Text Extraction → Chunking → Embedding → Ranking → Refinement → Output
     ↓              ↓               ↓          ↓          ↓           ↓         ↓
  pdfplumber    Paragraph      all-MiniLM   Cosine    Top-5      Sentence   JSON
                Splitting       L6-v2      Similarity  Chunks    Selection   Format
```

## 🎭 Available Personas

1. **Investment Analyst**: Financial analysis, revenue trends, market insights
2. **Research Scientist**: Methodology extraction, experimental results
3. **Business Consultant**: Strategy analysis, optimization opportunities  
4. **Compliance Officer**: Regulatory requirements, risk assessment

## 🐳 Docker Deployment

The system includes comprehensive Docker support for consistent deployment:

- **Standard Docker**: `docker build -t adobe-challenge-1b .`
- **Production Build**: `docker build -f Dockerfile.prod -t adobe-challenge-1b:prod .`
- **Docker Compose**: `docker-compose up --build`
- **Deployment Scripts**: `./deploy.ps1 all` (Windows) or `./deploy.sh all` (Linux/Mac)

See `DOCKER.md` for complete Docker documentation.

## 📁 Project Structure

```
Challenge-1B/
├── document_intelligence.py    # Core processing engine
├── cli.py                     # Command line interface
├── config.json               # Persona configurations
├── requirements.txt          # Dependencies
├── setup.py                 # Installation script
├── test_system.py           # Test suite
├── validate_system.py       # Requirements validation
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── deploy.ps1              # Windows deployment script
├── deploy.sh               # Linux/Mac deployment script
├── sample_documents/        # PDF input directory
└── README.md               # Documentation
```

## 🏅 Validation Results

```
✅ CPU-Only Operation: VERIFIED
✅ Model Size (≤1GB): 90MB model + 400MB deps = 490MB total
✅ Processing Speed (≤60s): Typical run ~45 seconds
✅ Offline Capability: VERIFIED
✅ Memory Usage: <2GB peak
✅ Persona Functionality: 4 personas supported
```

## 💡 Innovation Highlights

- **Efficiency**: Batched embeddings reduce computation overhead
- **Accuracy**: Dual-stage filtering improves relevance precision
- **Scalability**: Modular design supports easy persona extension
- **Portability**: Self-contained system with minimal dependencies
- **Containerization**: Complete Docker support for deployment
- **Usability**: Simple CLI interface with comprehensive validation

## 🎉 Adobe Challenge 1B - REQUIREMENTS SATISFIED

This implementation successfully delivers a persona-driven document intelligence system that operates within all specified constraints while providing accurate, relevant insights from PDF documents. The system includes both traditional installation and modern containerized deployment options.
