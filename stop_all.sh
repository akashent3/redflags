#!/bin/bash

echo "🛑 Stopping RedFlag AI Application..."
echo "======================================"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PIDs file exists
if [ -f /tmp/redflags.pids ]; then
    echo -e "${YELLOW}Reading PIDs from /tmp/redflags.pids${NC}"
    PIDS=$(cat /tmp/redflags.pids)

    for PID in $PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping process $PID...${NC}"
            kill $PID
            sleep 1
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${RED}Force killing $PID...${NC}"
                kill -9 $PID
            fi
            echo -e "${GREEN}✓ Stopped $PID${NC}"
        else
            echo -e "${YELLOW}Process $PID not running${NC}"
        fi
    done

    rm /tmp/redflags.pids
    echo -e "${GREEN}Removed PIDs file${NC}"
else
    echo -e "${YELLOW}No PIDs file found. Stopping by process name...${NC}"
fi

# Stop by process name (fallback)
echo -e "\n${YELLOW}Stopping remaining processes...${NC}"

# Stop Uvicorn (Backend)
pkill -f "uvicorn app.main:app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Stopped Backend${NC}"
fi

# Stop Celery
pkill -f "celery -A app.celery_app worker" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Stopped Celery${NC}"
fi

# Stop Next.js (Frontend)
pkill -f "next-server\|next dev" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Stopped Frontend${NC}"
fi

# Verify all stopped
sleep 2
echo -e "\n${YELLOW}Verifying...${NC}"

if pgrep -f "uvicorn|celery|next" > /dev/null; then
    echo -e "${RED}⚠️  Some processes still running:${NC}"
    ps aux | grep -E "uvicorn|celery|next" | grep -v grep
    echo -e "\n${YELLOW}Run with --force to kill them:${NC}"
    echo "  pkill -9 -f 'uvicorn|celery|next'"
else
    echo -e "${GREEN}✅ All services stopped successfully!${NC}"
fi

echo -e "\n📝 Logs still available at:"
echo "  • /tmp/backend.log"
echo "  • /tmp/celery.log"
echo "  • /tmp/frontend.log"
