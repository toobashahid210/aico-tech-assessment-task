#!/bin/bash

# Run FastAPI app (on port 8000)
uvicorn app2:app --reload --host 0.0.0.0 --port 8000 &

# Run Streamlit app (on port 8501)
streamlit run streamlit_app.py --server.port 8501 &

# Wait for both to finish
wait
