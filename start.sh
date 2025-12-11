#!/bin/bash

# Ombee AI - Local Development Startup Script

echo "🐝 Starting Ombee AI Development Environment..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env template..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./ombee.db
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=ombee-holistic
COHERE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
PHOENIX_API_KEY=your_key_here
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com
EOF
    echo "✅ .env template created. Please add your API keys!"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if database exists, if not create tables
if [ ! -f ombee.db ]; then
    echo "🗄️  Creating database..."
    python -c "from database import engine; import models; models.Base.metadata.create_all(bind=engine); print('✅ Database created!')"
fi

echo ""
echo "✨ Ombee AI is ready!"
echo ""
echo "🚀 Starting services..."
echo ""
echo "📡 Backend API will run on: http://localhost:8000"
echo "💬 Chat Frontend will run on: http://localhost:3000"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📊 Phoenix Dashboard: https://app.phoenix.arize.com"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Start backend in background
echo "Starting FastAPI backend..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
python -m http.server 3000 &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Both servers are running!"
echo ""
echo "🎉 Open your browser to: http://localhost:3000"
echo ""

# Wait for user to press Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Servers stopped. Goodbye!'; exit 0" INT

# Keep script running
wait