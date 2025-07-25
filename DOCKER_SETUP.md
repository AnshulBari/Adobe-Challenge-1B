# Docker Installation and Setup Guide

## 🐳 Installing Docker

### Windows Installation

1. **Download Docker Desktop**:
   - Go to https://docs.docker.com/desktop/install/windows/
   - Download Docker Desktop for Windows
   - Run the installer

2. **System Requirements**:
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 16299 or later)
   - Or Windows 11 64-bit: Home or Pro version 21H2 or higher
   - WSL 2 feature enabled

3. **Installation Steps**:
   ```powershell
   # Enable WSL 2 (if not already enabled)
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   
   # Restart your computer
   # Then install Docker Desktop from the downloaded installer
   ```

### Alternative: Docker without Desktop (using Chocolatey)

```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Docker
choco install docker-desktop
```

## 🚀 Testing Docker Installation

After installation, restart your system and test:

```powershell
# Check Docker version
docker --version

# Test Docker with hello-world
docker run hello-world
```

## 🏗️ Building Adobe Challenge 1B Docker Image

Once Docker is installed, you can build and run the project:

```powershell
# Navigate to project directory
cd "d:\GitRepo\Adobe\Challenge-1B"

# Build the image
docker build -t adobe-challenge-1b .

# Test the build
docker run --rm adobe-challenge-1b python --version

# Run validation
docker run --rm adobe-challenge-1b python validate_system.py
```

## 🎯 Using the Docker Setup

### Quick Commands

```powershell
# Build and validate (using our deployment script)
.\deploy.ps1 validate

# Build production image
.\deploy.ps1 prod

# Start services with Docker Compose
.\deploy.ps1 start

# Clean up Docker resources
.\deploy.ps1 cleanup
```

### Manual Docker Commands

```powershell
# Build image
docker build -t adobe-challenge-1b .

# Run with sample documents
docker run -v ${PWD}\sample_documents:/app/input -v ${PWD}\output:/app/output adobe-challenge-1b python cli.py --pdf-dir /app/input --persona "Investment Analyst" --job "Analyze revenue trends"

# Interactive shell
docker run -it adobe-challenge-1b bash
```

## 📦 What's Included in Docker Setup

I've created these Docker files for you:

1. **`Dockerfile`** - Main Docker configuration
2. **`Dockerfile.prod`** - Production-optimized build
3. **`docker-compose.yml`** - Service orchestration
4. **`.dockerignore`** - Build optimization
5. **`deploy.ps1`** - Windows PowerShell deployment script
6. **`deploy.sh`** - Linux/Mac deployment script
7. **`DOCKER.md`** - Comprehensive Docker documentation

## 🎉 Benefits of Docker Setup

- ✅ **Consistent Environment**: Same environment everywhere
- ✅ **Easy Deployment**: One command to run anywhere
- ✅ **Isolation**: No conflicts with your system
- ✅ **Portable**: Share with others easily
- ✅ **Resource Control**: Memory and CPU limits
- ✅ **Production Ready**: Optimized for deployment

## 🔄 Next Steps

1. Install Docker Desktop from the official website
2. Restart your computer
3. Run `docker --version` to verify installation
4. Navigate to your project directory
5. Run `.\deploy.ps1 validate` to build and test everything

The Docker setup is ready to use once you have Docker installed! 🚀
