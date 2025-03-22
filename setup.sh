# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r Requirements.txt  # Ensure all packages are installed

# Force install missing dependencies
pip install nltk gtts python-dotenv

# Download necessary NLTK resources
python -c "import nltk; nltk.download('vader_lexicon')"

# Run the Streamlit app
streamlit run app.py --server.port 7860 --server.address 0.0.0.0