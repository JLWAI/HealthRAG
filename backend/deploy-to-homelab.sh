#!/bin/bash
# HealthRAG Backend - Homelab Deployment Script
# Deploys to jwWinMin at 192.168.0.64

set -e  # Exit on error

HOMELAB_USER="root"
HOMELAB_HOST="192.168.0.210"
HOMELAB_PATH="/opt/healthrag/backend"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "═══════════════════════════════════════════════════════════"
echo "  HealthRAG Backend - Homelab Deployment"
echo "  Target: $HOMELAB_USER@$HOMELAB_HOST:$HOMELAB_PATH"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check SSH connection
echo "📡 Testing SSH connection..."
if ! ssh -q -o ConnectTimeout=5 $HOMELAB_USER@$HOMELAB_HOST exit; then
    echo "❌ ERROR: Cannot connect to homelab server at $HOMELAB_HOST"
    echo "   Please check:"
    echo "   1. Server is powered on"
    echo "   2. You're on the same network"
    echo "   3. SSH is enabled on server"
    exit 1
fi
echo "✅ SSH connection successful"
echo ""

# Check if repository exists on homelab
echo "📂 Checking repository on homelab..."
if ssh $HOMELAB_USER@$HOMELAB_HOST "test -d /opt/healthrag/.git"; then
    echo "✅ Repository exists - pulling latest changes"
    ssh $HOMELAB_USER@$HOMELAB_HOST "cd /opt/healthrag && git pull origin main"
else
    echo "⚠️  Git repository not initialized"
    echo "   HealthRAG is already deployed at /opt/healthrag"
    echo "   Syncing backend files manually..."

    # Create backend directory if it doesn't exist
    ssh $HOMELAB_USER@$HOMELAB_HOST "mkdir -p $HOMELAB_PATH"

    # Sync backend files
    rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' \
        "$SCRIPT_DIR/" $HOMELAB_USER@$HOMELAB_HOST:$HOMELAB_PATH/

    echo "✅ Backend files synced"
fi
echo ""

# Check .env file
echo "🔐 Checking environment configuration..."
if ! ssh $HOMELAB_USER@$HOMELAB_HOST "test -f $HOMELAB_PATH/.env"; then
    echo "⚠️  .env file not found on homelab"
    echo ""
    echo "You need to create .env file with your configuration."
    echo "Options:"
    echo "  1. Copy from local machine (if you have .env configured)"
    echo "  2. Create manually on homelab server"
    echo ""
    read -p "Copy .env from local machine? [y/N]: " COPY_ENV

    if [[ $COPY_ENV =~ ^[Yy]$ ]]; then
        if [ -f "$SCRIPT_DIR/.env" ]; then
            echo "📤 Copying .env to homelab..."
            scp "$SCRIPT_DIR/.env" $HOMELAB_USER@$HOMELAB_HOST:$HOMELAB_PATH/.env
            echo "✅ .env copied"
        else
            echo "❌ ERROR: No .env file found locally at $SCRIPT_DIR/.env"
            echo "   Please create .env file first (see .env.homelab.example)"
            exit 1
        fi
    else
        echo ""
        echo "Please create .env file on homelab server:"
        echo "  ssh $HOMELAB_USER@$HOMELAB_HOST"
        echo "  cd $HOMELAB_PATH"
        echo "  cp .env.homelab.example .env"
        echo "  nano .env  # Edit with your values"
        echo ""
        read -p "Press Enter when .env is ready..."
    fi
else
    echo "✅ .env file exists"
fi
echo ""

# Check Docker
echo "🐳 Checking Docker on homelab..."
if ! ssh $HOMELAB_USER@$HOMELAB_HOST "docker --version" > /dev/null 2>&1; then
    echo "❌ ERROR: Docker not found on homelab server"
    echo "   Please install Docker Desktop for Windows"
    echo "   https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo "✅ Docker is installed"
echo ""

# Deploy
echo "🚀 Deploying to homelab..."
echo ""

# Build and start containers
ssh $HOMELAB_USER@$HOMELAB_HOST << 'ENDSSH'
cd /opt/healthrag/backend

echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "📊 Container status:"
docker-compose ps

echo ""
echo "🔍 Checking health endpoint..."
sleep 5
curl -s http://localhost:8000/health || echo "⚠️  Health check failed - check logs below"

echo ""
echo "📋 Recent logs:"
docker-compose logs --tail=20 healthrag-api
ENDSSH

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Deployment Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Access Points:"
echo "  • Local Network:  http://192.168.0.210:8000"
echo "  • API Docs:       http://192.168.0.210:8000/docs"
echo "  • Health Check:   http://192.168.0.210:8000/health"
echo "  • Streamlit UI:   http://192.168.0.210:8501 (existing)"
echo ""
echo "🔧 Useful Commands:"
echo "  • View logs:      ssh $HOMELAB_USER@$HOMELAB_HOST 'cd $HOMELAB_PATH && docker-compose logs -f'"
echo "  • Restart API:    ssh $HOMELAB_USER@$HOMELAB_HOST 'cd $HOMELAB_PATH && docker-compose restart healthrag-api'"
echo "  • Stop all:       ssh $HOMELAB_USER@$HOMELAB_HOST 'cd $HOMELAB_PATH && docker-compose down'"
echo ""
echo "📖 Next Steps:"
echo "  1. Test API: curl http://192.168.0.210:8000/health"
echo "  2. Setup remote access (see HOMELAB_DEPLOYMENT.md)"
echo "  3. Import Postman collection and run tests"
echo ""
