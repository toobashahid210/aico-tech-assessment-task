#!/bin/bash

# activate the virtual environment
source venv/Scripts/activate

# Run FastAPI app (on port 8000)
uvicorn app:app --reload --host 0.0.0.0 --port 8000 &

# Run Streamlit app (on port 8501)
streamlit run ui.py --server.port 8501 &

# Wait for both to finish
wait
