# Run the Streamlit web application
streamlit run sfia_ai_framework/web/app.py --server.port 8501

# Alternative: Run the FastAPI server
# uvicorn sfia_ai_framework.web.api:app --host 0.0.0.0 --port 8000 --reload