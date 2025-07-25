#!/bin/bash
# Docker deployment script for Adobe Challenge 1B Document Intelligence System

set -e

# Configuration
IMAGE_NAME="adobe-challenge-1b"
PROD_IMAGE_NAME="adobe-challenge-1b-prod"
VERSION=${2:-"latest"}
REGISTRY=${REGISTRY:-""}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "🐳 Adobe Challenge 1B - Document Intelligence System"
    echo "=================================================="
    echo -e "${NC}"
}

build_image() {
    log_info "Building development Docker image: $IMAGE_NAME:$VERSION"
    if docker build -t $IMAGE_NAME:$VERSION .; then
        log_success "Development image built successfully"
        docker images $IMAGE_NAME:$VERSION
    else
        log_error "Failed to build development image"
        exit 1
    fi
}

build_prod_image() {
    log_info "Building production Docker image: $PROD_IMAGE_NAME:$VERSION"
    if docker build -f Dockerfile.prod -t $PROD_IMAGE_NAME:$VERSION .; then
        log_success "Production image built successfully"
        docker images $PROD_IMAGE_NAME:$VERSION
    else
        log_error "Failed to build production image"
        exit 1
    fi
}

run_validation() {
    log_info "Running system validation in container..."
    if docker run --rm --name validation-test $IMAGE_NAME:$VERSION python validate_system.py; then
        log_success "Validation completed successfully"
    else
        log_error "Validation failed"
        return 1
    fi
}

run_tests() {
    log_info "Running test suite in container..."
    if docker run --rm --name test-suite $IMAGE_NAME:$VERSION python test_system.py; then
        log_success "All tests passed"
    else
        log_error "Tests failed"
        return 1
    fi
}

start_services() {
    log_info "Starting Docker Compose services..."
    if docker-compose up -d; then
        log_success "Services started successfully"
        docker-compose ps
    else
        log_error "Failed to start services"
        exit 1
    fi
}

stop_services() {
    log_info "Stopping Docker Compose services..."
    if docker-compose down; then
        log_success "Services stopped successfully"
    else
        log_warning "Some services may still be running"
    fi
}

show_logs() {
    log_info "Showing container logs..."
    docker-compose logs -f
}

run_example() {
    local persona=${2:-"Investment Analyst"}
    local job=${3:-"Analyze revenue trends and growth patterns"}
    
    log_info "Running example analysis with persona: $persona"
    
    # Ensure output directory exists
    mkdir -p ./output
    
    if docker run --rm \
        -v "$(pwd)/sample_documents:/app/input:ro" \
        -v "$(pwd)/output:/app/output:rw" \
        $IMAGE_NAME:$VERSION \
        python cli.py --pdf-dir /app/input --persona "$persona" --job "$job" --output /app/output/example_results.json; then
        log_success "Example analysis completed. Check ./output/example_results.json"
    else
        log_error "Example analysis failed"
        return 1
    fi
}

interactive_shell() {
    log_info "Starting interactive shell in container..."
    docker run -it --rm \
        -v "$(pwd)/sample_documents:/app/input:ro" \
        -v "$(pwd)/output:/app/output:rw" \
        $IMAGE_NAME:$VERSION \
        /bin/bash
}

cleanup() {
    log_info "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    log_success "Cleanup completed"
}

push_to_registry() {
    if [ -z "$REGISTRY" ]; then
        log_error "REGISTRY environment variable not set"
        exit 1
    fi
    
    log_info "Pushing images to registry: $REGISTRY"
    
    # Tag and push development image
    docker tag $IMAGE_NAME:$VERSION $REGISTRY/$IMAGE_NAME:$VERSION
    docker push $REGISTRY/$IMAGE_NAME:$VERSION
    
    # Tag and push production image
    docker tag $PROD_IMAGE_NAME:$VERSION $REGISTRY/$PROD_IMAGE_NAME:$VERSION
    docker push $REGISTRY/$PROD_IMAGE_NAME:$VERSION
    
    log_success "Images pushed to registry"
}

show_usage() {
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  build [version]     - Build development Docker image"
    echo "  prod [version]      - Build production Docker image"
    echo "  validate           - Run validation tests in container"
    echo "  test              - Run test suite in container"
    echo "  start             - Start Docker Compose services"
    echo "  stop              - Stop Docker Compose services"
    echo "  logs              - Show container logs"
    echo "  example [persona] [job] - Run example analysis"
    echo "  shell             - Start interactive shell in container"
    echo "  cleanup           - Clean up Docker resources"
    echo "  push              - Push images to registry (requires REGISTRY env var)"
    echo "  all [version]     - Build, validate, test, and start services"
    echo ""
    echo "Examples:"
    echo "  $0 build v1.0.0"
    echo "  $0 validate"
    echo "  $0 example \"Research Scientist\" \"Extract methodology\""
    echo "  $0 all latest"
    echo "  REGISTRY=myregistry.com $0 push"
}

# Pre-flight checks
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile not found in current directory"
        exit 1
    fi
}

# Main execution
print_header

case "${1:-help}" in
    "build")
        check_dependencies
        build_image
        ;;
    "prod")
        check_dependencies
        build_prod_image
        ;;
    "validate")
        check_dependencies
        build_image
        run_validation
        ;;
    "test")
        check_dependencies
        build_image
        run_tests
        ;;
    "start")
        check_dependencies
        start_services
        ;;
    "stop")
        check_dependencies
        stop_services
        ;;
    "logs")
        check_dependencies
        show_logs
        ;;
    "example")
        check_dependencies
        build_image
        run_example "$@"
        ;;
    "shell")
        check_dependencies
        build_image
        interactive_shell
        ;;
    "cleanup")
        check_dependencies
        cleanup
        ;;
    "push")
        check_dependencies
        push_to_registry
        ;;
    "all")
        check_dependencies
        build_image
        run_validation
        run_tests
        start_services
        ;;
    "help"|*)
        show_usage
        ;;
esac

echo ""
log_success "Operation completed successfully! 🎉"
