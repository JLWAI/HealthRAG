#!/bin/bash

# HealthRAG Homelab Deployment Script
# Automates deployment to jwBeast Proxmox homelab
# Target: CT 100 (Docker Host @ 192.168.0.210)

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
DOCKER_HOST="192.168.0.210"
DOCKER_USER="root"
OLLAMA_HOST="192.168.0.211"
DEPLOY_DIR="/opt/healthrag"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  HealthRAG Homelab Deployment Script                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Verify Ollama is running
echo -e "${YELLOW}[1/6] Verifying Ollama service on CT 101...${NC}"
if curl -s http://${OLLAMA_HOST}:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama is running and accessible${NC}"
    echo -e "Models available:"
    curl -s http://${OLLAMA_HOST}:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | sed 's/^/  - /'
else
    echo -e "${RED}✗ Cannot connect to Ollama on ${OLLAMA_HOST}:11434${NC}"
    echo -e "${YELLOW}Please start Ollama on CT 101 first:${NC}"
    echo -e "  ssh root@${OLLAMA_HOST}"
    echo -e "  ollama serve &"
    exit 1
fi
echo ""

# Step 2: Transfer files to Docker host
echo -e "${YELLOW}[2/6] Transferring files to CT 100...${NC}"
echo -e "Target: ${DOCKER_USER}@${DOCKER_HOST}:${DEPLOY_DIR}"

# Create remote directory
ssh ${DOCKER_USER}@${DOCKER_HOST} "mkdir -p ${DEPLOY_DIR}"

# Use rsync for efficient transfer (excludes .git, venv, etc.)
rsync -avz --progress \
  --exclude='.git' \
  --exclude='venv*' \
  --exclude='data/vectorstore' \
  --exclude='data/workouts.db' \
  --exclude='data/food_log.db' \
  --exclude='*.log' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='test-results' \
  ./ ${DOCKER_USER}@${DOCKER_HOST}:${DEPLOY_DIR}/

echo -e "${GREEN}✓ Files transferred successfully${NC}"
echo ""

# Step 3: Check if PDFs exist
echo -e "${YELLOW}[3/6] Checking PDF knowledge base...${NC}"
PDF_COUNT=$(ssh ${DOCKER_USER}@${DOCKER_HOST} "ls -1 ${DEPLOY_DIR}/data/pdfs/*.pdf 2>/dev/null | wc -l" || echo "0")
if [ "$PDF_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Found ${PDF_COUNT} PDFs in data/pdfs/${NC}"
else
    echo -e "${YELLOW}⚠ No PDFs found in data/pdfs/${NC}"
    echo -e "${YELLOW}You'll need to transfer PDFs manually:${NC}"
    echo -e "  scp data/pdfs/*.pdf ${DOCKER_USER}@${DOCKER_HOST}:${DEPLOY_DIR}/data/pdfs/"
fi
echo ""

# Step 4: Build Docker image
echo -e "${YELLOW}[4/6] Building Docker image on CT 100...${NC}"
ssh ${DOCKER_USER}@${DOCKER_HOST} "cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml build"
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 5: Start container
echo -e "${YELLOW}[5/6] Starting HealthRAG container...${NC}"
ssh ${DOCKER_USER}@${DOCKER_HOST} "cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml up -d"
echo -e "${GREEN}✓ Container started${NC}"
echo ""

# Step 6: Verify deployment
echo -e "${YELLOW}[6/6] Verifying deployment...${NC}"
sleep 5  # Wait for container to fully start

# Check container status
CONTAINER_STATUS=$(ssh ${DOCKER_USER}@${DOCKER_HOST} "docker ps --filter name=healthrag --format '{{.Status}}'" || echo "Not running")
if [[ $CONTAINER_STATUS == *"Up"* ]]; then
    echo -e "${GREEN}✓ Container is running: ${CONTAINER_STATUS}${NC}"
else
    echo -e "${RED}✗ Container not running. Check logs:${NC}"
    echo -e "  ssh ${DOCKER_USER}@${DOCKER_HOST}"
    echo -e "  cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml logs"
    exit 1
fi

# Check health endpoint
if curl -s http://${DOCKER_HOST}:8501/_stcore/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HealthRAG is responding on port 8501${NC}"
else
    echo -e "${YELLOW}⚠ Health check pending (container may still be starting)${NC}"
fi
echo ""

# Step 7: Process PDFs (if needed)
if [ "$PDF_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}[Optional] Processing PDFs to build vectorstore...${NC}"
    read -p "Process PDFs now? This takes 5-10 minutes. (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Processing PDFs (this may take a while)...${NC}"
        ssh ${DOCKER_USER}@${DOCKER_HOST} "cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml exec healthrag python3 process_pdfs.py"
        echo -e "${GREEN}✓ PDFs processed and vectorstore created${NC}"
    else
        echo -e "${YELLOW}Skipped PDF processing. You can run it later:${NC}"
        echo -e "  ssh ${DOCKER_USER}@${DOCKER_HOST}"
        echo -e "  cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml exec healthrag python3 process_pdfs.py"
    fi
    echo ""
fi

# Success summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Deployment Successful!                                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access HealthRAG:${NC}"
echo -e "  Web UI: ${GREEN}http://${DOCKER_HOST}:8501${NC}"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  View logs:    ssh ${DOCKER_USER}@${DOCKER_HOST} 'cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml logs -f'"
echo -e "  Restart:      ssh ${DOCKER_USER}@${DOCKER_HOST} 'cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml restart'"
echo -e "  Stop:         ssh ${DOCKER_USER}@${DOCKER_HOST} 'cd ${DEPLOY_DIR} && docker compose -f docker-compose.homelab.yml down'"
echo ""
echo -e "${BLUE}Architecture:${NC}"
echo -e "  HealthRAG:    CT 100 (${DOCKER_HOST}:8501)"
echo -e "  Ollama:       CT 101 (${OLLAMA_HOST}:11434)"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Open http://${DOCKER_HOST}:8501 in your browser"
echo -e "  2. Create a user profile"
echo -e "  3. Ask a health/fitness question"
echo -e "  4. Set up automated backups (see docs/HOMELAB_DEPLOYMENT.md)"
echo ""
