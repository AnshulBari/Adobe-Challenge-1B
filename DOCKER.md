# Docker Deployment Guide

## 🐳 Docker Setup for Adobe Challenge 1B

This guide explains how to run the Document Intelligence System using Docker, ensuring consistent deployment across different environments.

## 📋 Prerequisites

- Docker Engine 20.0+ 
- Docker Compose 1.28+
- At least 2GB available RAM
- PDF documents to analyze

## 🚀 Quick Start

### Option 1: Docker Build & Run (Linux/Mac)

```bash
# Build the Docker image
docker build -t adobe-challenge-1b .

# Run analysis with sample documents
docker run -v ./sample_documents:/app/input -v ./output:/app/output adobe-challenge-1b \
  python cli.py --pdf-dir /app/input --persona "Investment Analyst" --job "Analyze revenue trends"
```

### Option 2: Docker Build & Run (Windows)

```powershell
# Build the Docker image
docker build -t adobe-challenge-1b .

# Run analysis with sample documents
docker run -v ${PWD}\sample_documents:/app/input -v ${PWD}\output:/app/output adobe-challenge-1b python cli.py --pdf-dir /app/input --persona "Investment Analyst" --job "Analyze revenue trends"
```

### Option 3: Docker Compose (Recommended)

```bash
# Start the service
docker-compose up --build

# Run one-time analysis
docker-compose run --rm document-intelligence \
  python cli.py --pdf-dir /app/input --persona "Research Scientist" --job "Extract methodology"
```

### Option 4: Deployment Scripts

**Linux/Mac:**
```bash
# Make script executable
chmod +x deploy.sh

# Run all operations (build, validate, test, start)
./deploy.sh all

# Build specific version
./deploy.sh build v1.0.0

# Run validation only
./deploy.sh validate
```

**Windows PowerShell:**
```powershell
# Run all operations
.\deploy.ps1 all

# Build specific version
.\deploy.ps1 build v1.0.0

# Run example analysis
.\deploy.ps1 example "Investment Analyst" "Analyze financial performance"
```

## 📁 Volume Mapping

| Host Path | Container Path | Purpose | Access |
|-----------|----------------|---------|--------|
| `./sample_documents` | `/app/input` | PDF input files | Read-only |
| `./output` | `/app/output` | JSON results | Read-write |
| `model-cache` | `/app/.cache` | Model cache | Persistent |

## 🎯 Usage Examples

### 1. Investment Analysis
```bash
docker run -v ./pdfs:/app/input -v ./results:/app/output adobe-challenge-1b \
  python cli.py --pdf-dir /app/input \
  --persona "Investment Analyst" \
  --job "Analyze revenue trends and R&D investments" \
  --output /app/output/investment_analysis.json
```

### 2. Research Paper Analysis
```bash
docker run -v ./papers:/app/input -v ./results:/app/output adobe-challenge-1b \
  python cli.py --pdf-dir /app/input \
  --persona "Research Scientist" \
  --job "Extract methodology and key findings" \
  --output /app/output/research_analysis.json
```

### 3. Compliance Review
```bash
docker run -v ./documents:/app/input -v ./results:/app/output adobe-challenge-1b \
  python cli.py --pdf-dir /app/input \
  --persona "Compliance Officer" \
  --job "Identify regulatory requirements and risks" \
  --output /app/output/compliance_review.json
```

### 4. Business Strategy Analysis
```bash
docker run -v ./docs:/app/input -v ./results:/app/output adobe-challenge-1b \
  python cli.py --pdf-dir /app/input \
  --persona "Business Consultant" \
  --job "Extract strategic insights and optimization opportunities" \
  --output /app/output/strategy_analysis.json
```

### 5. Interactive Shell
```bash
# Enter container for debugging
docker run -it -v ./sample_documents:/app/input -v ./output:/app/output adobe-challenge-1b bash

# Run Python interactively
docker run -it adobe-challenge-1b python
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TRANSFORMERS_CACHE` | `/app/.cache` | Model cache directory |
| `HF_HOME` | `/app/.cache` | Hugging Face cache directory |
| `TORCH_HOME` | `/app/.cache` | PyTorch cache directory |

### Resource Limits

```yaml
# In docker-compose.yml
mem_limit: 2g        # Maximum 2GB RAM
cpus: '2.0'          # Maximum 2 CPU cores
```

### Custom Configuration

```bash
# Set custom log level
docker run -e LOG_LEVEL=DEBUG adobe-challenge-1b python cli.py --help

# Set custom cache directory
docker run -e TRANSFORMERS_CACHE=/custom/cache adobe-challenge-1b python cli.py --help
```

## 🔍 Validation and Testing

### System Validation
```bash
# Run constraint validation
docker run --rm adobe-challenge-1b python validate_system.py

# Using deployment script
./deploy.sh validate
.\deploy.ps1 validate
```

### Test Suite
```bash
# Run comprehensive tests
docker run --rm adobe-challenge-1b python test_system.py

# Using deployment script
./deploy.sh test
.\deploy.ps1 test
```

### Available Personas
```bash
# List all configured personas
docker run --rm adobe-challenge-1b python cli.py --list-personas
```

## 📊 Performance Metrics

| Metric | Docker Performance |
|--------|-------------------|
| **Image Size** | ~800MB (dev), ~600MB (prod) |
| **Memory Usage** | <2GB peak, ~1.2GB typical |
| **CPU Usage** | 1-2 cores during processing |
| **Processing Time** | <60s for typical workload |
| **Model Loading** | ~6s (cached after first run) |
| **Startup Time** | ~10s cold start, ~2s warm start |

## 🛠️ Troubleshooting

### Common Issues

1. **Out of Memory**
   ```bash
   # Increase memory limit
   docker run -m 4g adobe-challenge-1b ...
   ```

2. **Permission Denied on Windows**
   ```powershell
   # Fix volume permissions
   docker run --rm -v ${PWD}:/data busybox chmod -R 777 /data/output
   ```

3. **No PDF Files Found**
   ```bash
   # Check volume mounting
   docker run -v $(pwd)/sample_documents:/app/input adobe-challenge-1b ls -la /app/input
   ```

4. **Model Download Issues**
   ```bash
   # Rebuild with fresh model cache
   docker build --no-cache -t adobe-challenge-1b .
   ```

5. **Container Won't Start**
   ```bash
   # Check container logs
   docker logs <container_id>
   
   # Run with debug output
   docker run -e LOG_LEVEL=DEBUG adobe-challenge-1b python cli.py --help
   ```

### Debug Mode

```bash
# Run with debug logging
docker run -e LOG_LEVEL=DEBUG adobe-challenge-1b python cli.py ...

# Interactive debugging
docker run -it adobe-challenge-1b python -i cli.py

# Shell access for troubleshooting
docker run -it adobe-challenge-1b bash
```

### Health Checks

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' <container_id>

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' <container_id>
```

## 🏗️ Production Deployment

### Production Image
```bash
# Build production-optimized image
docker build -f Dockerfile.prod -t adobe-challenge-1b:prod .

# Run production image
docker run adobe-challenge-1b:prod python cli.py --help
```

### Registry Deployment
```bash
# Tag for registry
docker tag adobe-challenge-1b your-registry.com/adobe-challenge-1b:v1.0.0

# Push to registry
docker push your-registry.com/adobe-challenge-1b:v1.0.0

# Deploy from registry
docker run your-registry.com/adobe-challenge-1b:v1.0.0 python cli.py --help
```

### Orchestration (Kubernetes Example)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: document-intelligence
spec:
  replicas: 1
  selector:
    matchLabels:
      app: document-intelligence
  template:
    metadata:
      labels:
        app: document-intelligence
    spec:
      containers:
      - name: document-intelligence
        image: adobe-challenge-1b:latest
        resources:
          limits:
            memory: "2Gi"
            cpu: "2"
          requests:
            memory: "1Gi"
            cpu: "1"
        volumeMounts:
        - name: input-volume
          mountPath: /app/input
        - name: output-volume
          mountPath: /app/output
      volumes:
      - name: input-volume
        persistentVolumeClaim:
          claimName: input-pvc
      - name: output-volume
        persistentVolumeClaim:
          claimName: output-pvc
```

## 🔒 Security Considerations

- ✅ **Non-root user**: Production image runs as non-root user
- ✅ **Read-only input**: Input volumes mounted read-only
- ✅ **Minimal base image**: Uses python:3.11-slim
- ✅ **No unnecessary ports**: No network exposure by default
- ✅ **Resource limits**: Memory and CPU limits enforced
- ✅ **Secrets management**: Environment variables for sensitive data

## 🎉 Docker Compliance Summary

| Adobe Challenge 1B Requirement | Docker Implementation | Status |
|--------------------------------|----------------------|--------|
| **CPU-Only Operation** | PyTorch CPU-only configuration | ✅ **COMPLIANT** |
| **Model Size ≤1GB** | all-MiniLM-L6-v2 (~90MB) + deps (~400MB) | ✅ **COMPLIANT** |
| **Processing Time ≤60s** | Optimized Docker layers, model caching | ✅ **COMPLIANT** |
| **Offline Operation** | Self-contained with pre-downloaded models | ✅ **COMPLIANT** |
| **Persona-Driven** | Full persona support via CLI/API | ✅ **COMPLIANT** |

## 📝 Additional Notes

- **First run**: May take longer due to model caching
- **Persistent cache**: Use named volumes for model cache persistence
- **Resource monitoring**: Monitor container resource usage in production
- **Log management**: Configure log rotation for long-running containers
- **Updates**: Rebuild images regularly for security updates
- **Backup**: Backup persistent volumes containing model cache

## 🆘 Support

For issues with Docker deployment:

1. Check the troubleshooting section above
2. Verify Docker and Docker Compose versions
3. Ensure sufficient system resources (RAM/CPU)
4. Check container logs for detailed error messages
5. Test with minimal configuration first

Your Docker setup is ready for deployment! 🚀
