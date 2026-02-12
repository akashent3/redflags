#!/bin/bash

echo "🚀 Starting RedFlag AI Application..."
echo "======================================"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -e "\n${YELLOW}Checking Redis...${NC}"
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    redis-server --daemonize yes
    sleep 2
    redis-cli ping > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Redis started${NC}"
    else
        echo -e "${RED}✗ Failed to start Redis${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Redis already running${NC}"
fi

# Check if PostgreSQL is running
echo -e "\n${YELLOW}Checking PostgreSQL...${NC}"
pg_isready > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not running. Please start it first.${NC}"
    exit 1
fi

# Start Backend
echo -e "\n${YELLOW}Starting Backend API (Port 8000)...${NC}"
cd /home/user/redflags/backend
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Check if backend started
curl -s http://localhost:8000/docs > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Check /tmp/backend.log${NC}"
fi

# Start Celery Worker
echo -e "\n${YELLOW}Starting Celery Worker...${NC}"
celery -A app.celery_app worker --loglevel=info > /tmp/celery.log 2>&1 &
CELERY_PID=$!
sleep 3
if ps -p $CELERY_PID > /dev/null; then
    echo -e "${GREEN}✓ Celery started (PID: $CELERY_PID)${NC}"
else
    echo -e "${RED}✗ Celery failed to start. Check /tmp/celery.log${NC}"
fi

# Start Frontend
echo -e "\n${YELLOW}Starting Frontend (Port 3000)...${NC}"
cd /home/user/redflags/frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5

# Check if frontend started
curl -s http://localhost:3000 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check /tmp/frontend.log${NC}"
fi

# Summary
echo -e "\n======================================"
echo -e "${GREEN}✅ All services started!${NC}"
echo -e "======================================\n"

echo "📊 Service URLs:"
echo "  • Backend API:  http://localhost:8000"
echo "  • API Docs:     http://localhost:8000/docs"
echo "  • Frontend:     http://localhost:3000"

echo -e "\n📝 Logs:"
echo "  • Backend:  tail -f /tmp/backend.log"
echo "  • Celery:   tail -f /tmp/celery.log"
echo "  • Frontend: tail -f /tmp/frontend.log"

echo -e "\n🔢 Process IDs:"
echo "  • Backend: $BACKEND_PID"
echo "  • Celery:  $CELERY_PID"
echo "  • Frontend: $FRONTEND_PID"

echo -e "\n⏹️  To stop all services:"
echo "  kill $BACKEND_PID $CELERY_PID $FRONTEND_PID"
echo "  Or run: pkill -f 'uvicorn|celery|next-server'"

echo -e "\n🧪 Quick Test:"
echo "  1. Open http://localhost:3000"
echo "  2. Register/Login"
echo "  3. Go to Analyze page"
echo "  4. Search for 'TCS' or 'Reliance'"
echo "  5. Click Analyze and wait"

echo -e "\n💡 Tip: Save PIDs to file for easy stopping:"
echo "  echo \"$BACKEND_PID $CELERY_PID $FRONTEND_PID\" > /tmp/redflags.pids"
echo "  kill \$(cat /tmp/redflags.pids)"

# Save PIDs
echo "$BACKEND_PID $CELERY_PID $FRONTEND_PID" > /tmp/redflags.pids
echo -e "\n${GREEN}PIDs saved to /tmp/redflags.pids${NC}"
