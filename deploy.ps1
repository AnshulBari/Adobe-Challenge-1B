# PowerShell deployment script for Adobe Challenge 1B Document Intelligence System

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Version = "latest",
    
    [Parameter(Position=2)]
    [string]$Persona = "Investment Analyst",
    
    [Parameter(Position=3)]
    [string]$Job = "Analyze revenue trends and growth patterns"
)

# Configuration
$ImageName = "adobe-challenge-1b"
$ProdImageName = "adobe-challenge-1b-prod"
$Registry = $env:REGISTRY

# Functions
function Write-Header {
    Write-Host "🐳 Adobe Challenge 1B - Document Intelligence System" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Test-Dependencies {
    Write-Info "Checking dependencies..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "Docker found: $dockerVersion"
    }
    catch {
        Write-Error "Docker is not installed or not in PATH"
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose found: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose is not installed or not in PATH"
        exit 1
    }
    
    # Check Dockerfile
    if (-not (Test-Path "Dockerfile")) {
        Write-Error "Dockerfile not found in current directory"
        exit 1
    }
    
    Write-Success "All dependencies satisfied"
}

function Build-Image {
    Write-Info "Building development Docker image: $ImageName`:$Version"
    
    $result = docker build -t "$ImageName`:$Version" .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Development image built successfully"
        docker images "$ImageName`:$Version"
    } else {
        Write-Error "Failed to build development image"
        exit 1
    }
}

function Build-ProdImage {
    Write-Info "Building production Docker image: $ProdImageName`:$Version"
    
    $result = docker build -f Dockerfile.prod -t "$ProdImageName`:$Version" .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Production image built successfully"
        docker images "$ProdImageName`:$Version"
    } else {
        Write-Error "Failed to build production image"
        exit 1
    }
}

function Invoke-Validation {
    Write-Info "Running system validation in container..."
    
    docker run --rm --name validation-test "$ImageName`:$Version" python validate_system.py
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Validation completed successfully"
    } else {
        Write-Error "Validation failed"
        return $false
    }
    return $true
}

function Invoke-Tests {
    Write-Info "Running test suite in container..."
    
    docker run --rm --name test-suite "$ImageName`:$Version" python test_system.py
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All tests passed"
    } else {
        Write-Error "Tests failed"
        return $false
    }
    return $true
}

function Start-Services {
    Write-Info "Starting Docker Compose services..."
    
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services started successfully"
        docker-compose ps
    } else {
        Write-Error "Failed to start services"
        exit 1
    }
}

function Stop-Services {
    Write-Info "Stopping Docker Compose services..."
    
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services stopped successfully"
    } else {
        Write-Warning "Some services may still be running"
    }
}

function Show-Logs {
    Write-Info "Showing container logs..."
    docker-compose logs -f
}

function Invoke-Example {
    Write-Info "Running example analysis with persona: $Persona"
    
    # Ensure output directory exists
    if (-not (Test-Path "output")) {
        New-Item -ItemType Directory -Path "output" | Out-Null
    }
    
    # Get current directory for volume mounting
    $currentDir = (Get-Location).Path
    
    docker run --rm `
        -v "$currentDir\sample_documents:/app/input:ro" `
        -v "$currentDir\output:/app/output:rw" `
        "$ImageName`:$Version" `
        python cli.py --pdf-dir /app/input --persona $Persona --job $Job --output /app/output/example_results.json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Example analysis completed. Check .\output\example_results.json"
    } else {
        Write-Error "Example analysis failed"
        return $false
    }
    return $true
}

function Start-InteractiveShell {
    Write-Info "Starting interactive shell in container..."
    
    $currentDir = (Get-Location).Path
    
    docker run -it --rm `
        -v "$currentDir\sample_documents:/app/input:ro" `
        -v "$currentDir\output:/app/output:rw" `
        "$ImageName`:$Version" `
        /bin/bash
}

function Invoke-Cleanup {
    Write-Info "Cleaning up Docker resources..."
    
    # Stop and remove containers
    try {
        docker-compose down --remove-orphans 2>$null
    } catch {
        # Ignore errors
    }
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    Write-Success "Cleanup completed"
}

function Push-ToRegistry {
    if (-not $Registry) {
        Write-Error "REGISTRY environment variable not set"
        exit 1
    }
    
    Write-Info "Pushing images to registry: $Registry"
    
    # Tag and push development image
    docker tag "$ImageName`:$Version" "$Registry/$ImageName`:$Version"
    docker push "$Registry/$ImageName`:$Version"
    
    # Tag and push production image
    docker tag "$ProdImageName`:$Version" "$Registry/$ProdImageName`:$Version"
    docker push "$Registry/$ProdImageName`:$Version"
    
    Write-Success "Images pushed to registry"
}

function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 <command> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Cyan
    Write-Host "  build [version]     - Build development Docker image" -ForegroundColor White
    Write-Host "  prod [version]      - Build production Docker image" -ForegroundColor White
    Write-Host "  validate           - Run validation tests in container" -ForegroundColor White
    Write-Host "  test              - Run test suite in container" -ForegroundColor White
    Write-Host "  start             - Start Docker Compose services" -ForegroundColor White
    Write-Host "  stop              - Stop Docker Compose services" -ForegroundColor White
    Write-Host "  logs              - Show container logs" -ForegroundColor White
    Write-Host "  example [persona] [job] - Run example analysis" -ForegroundColor White
    Write-Host "  shell             - Start interactive shell in container" -ForegroundColor White
    Write-Host "  cleanup           - Clean up Docker resources" -ForegroundColor White
    Write-Host "  push              - Push images to registry (requires REGISTRY env var)" -ForegroundColor White
    Write-Host "  all [version]     - Build, validate, test, and start services" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\deploy.ps1 build v1.0.0" -ForegroundColor White
    Write-Host "  .\deploy.ps1 validate" -ForegroundColor White
    Write-Host "  .\deploy.ps1 example `"Research Scientist`" `"Extract methodology`"" -ForegroundColor White
    Write-Host "  .\deploy.ps1 all latest" -ForegroundColor White
    Write-Host "  `$env:REGISTRY=`"myregistry.com`"; .\deploy.ps1 push" -ForegroundColor White
}

# Main execution
Write-Header

switch ($Command.ToLower()) {
    "build" {
        Test-Dependencies
        Build-Image
    }
    "prod" {
        Test-Dependencies
        Build-ProdImage
    }
    "validate" {
        Test-Dependencies
        Build-Image
        Invoke-Validation
    }
    "test" {
        Test-Dependencies
        Build-Image
        Invoke-Tests
    }
    "start" {
        Test-Dependencies
        Start-Services
    }
    "stop" {
        Test-Dependencies
        Stop-Services
    }
    "logs" {
        Test-Dependencies
        Show-Logs
    }
    "example" {
        Test-Dependencies
        Build-Image
        Invoke-Example
    }
    "shell" {
        Test-Dependencies
        Build-Image
        Start-InteractiveShell
    }
    "cleanup" {
        Test-Dependencies
        Invoke-Cleanup
    }
    "push" {
        Test-Dependencies
        Push-ToRegistry
    }
    "all" {
        Test-Dependencies
        Build-Image
        $validationResult = Invoke-Validation
        $testResult = Invoke-Tests
        if ($validationResult -and $testResult) {
            Start-Services
        } else {
            Write-Error "Skipping service startup due to validation or test failures"
        }
    }
    default {
        Show-Usage
    }
}

Write-Host ""
Write-Success "Operation completed successfully! 🎉"
