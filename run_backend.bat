@echo off
echo Starting LoseWeightEasily Backend on port 16666...
cd backend
uv run uvicorn src.app:app --host 0.0.0.0 --port 16666 --reload
pause
