#!/bin/bash
# Build script for Render deployment

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Downloading NLTK data..."
python download_nltk_data.py

echo "Setting up database..."
python -c "from backend.database import init_db; init_db()"

echo "Importing initial data..."
python backend/import_all_csv.py
python backend/import_admission_quotas.py

echo "Build complete!"
