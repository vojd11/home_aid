#!/bin/bash

# Home Aid Kit Manager Setup Script

echo "🏠 Setting up Home Aid Kit Manager..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend environment file..."
    cp backend/.env.example backend/.env
fi

# Create PostgreSQL initialization script
mkdir -p backend/sql
cat > backend/sql/init.sql << 'EOF'
-- Enable pg_trgm extension for fuzzy search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create database (already handled by Docker environment)
EOF

echo "🐳 Starting services with Docker Compose..."
docker-compose up -d postgres redis

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo "🔧 Running database migrations..."
docker-compose run --rm api alembic upgrade head

echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Setup complete!"
echo ""
echo "📋 Service Information:"
echo "• Frontend: http://hate.local:3000"
echo "• Backend API: http://hate.local:8000"
echo "• API Documentation: http://hate.local:8000/docs"
echo "• PostgreSQL: hate.local:5432"
echo "• Redis: hate.local:6379"
echo ""
echo "🛠️ Development Commands:"
echo "• View logs: docker-compose logs -f"
echo "• Stop services: docker-compose down"
echo "• Restart services: docker-compose restart"
echo "• Access backend shell: docker-compose exec api bash"
echo ""
echo "📖 See README.md for more information."
