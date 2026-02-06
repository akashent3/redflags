@echo off
REM Start Celery worker for RedFlag AI

echo Starting Celery worker...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start Celery worker with analysis queue
celery -A app.celery_app worker --loglevel=info --pool=solo --queues=analysis --concurrency=1

pause
