import subprocess
import sys
import streamlit as st
import requests
import nltk
import time
from nltk.sentiment import SentimentIntensityAnalyzer
from gtts import gTTS
from datetime import datetime
import os
from PIL import Image
import base64

# Force install missing dependencies
missing_packages = ["nltk", "gtts", "python-dotenv"]
for package in missing_packages:
    try:
        __import__(package.replace("-", "_"))
    except ModuleNotFoundError:
        subprocess.run([sys.executable, "-m", "pip", "install", package])

# Import dotenv after ensuring installation
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=True)

# Fetch API Keys securely
API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Download VADER Lexicon for Sentiment Analysis
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

# Streamlit App Title
st.title("📢 News Sentiment Analyzer")


# Sidebar Section
with st.sidebar:
    st.header("📰🔥 Top News Today")

    if "top_news" not in st.session_state:
        def fetch_top_news():
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json().get("articles", [])
            return []

        st.session_state.top_news = fetch_top_news()

    top_news = st.session_state.top_news  # Use cached data

    if top_news:
        st.markdown("""
            <style>
                .news-card {
                    display: inline-block;
                    width: 100%;
                    max-width: 320px;
                    border-radius: 12px;
                    overflow: hidden;
                    background: #1e1e1e;
                    color: white;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                    margin: 10px;
                }
                .news-img {
                    width: 100%;
                    height: 180px;
                    object-fit: cover;
                }
                .news-content {
                    padding: 10px;
                }
                .news-title {
                    font-size: 16px;
                    font-weight: bold;
                }
            </style>
        """, unsafe_allow_html=True)

        for article in top_news[:5]:
            title = article.get("title", "No Title")
            url = article.get("url", "#")
            image_url = article.get("urlToImage", "")

            if image_url:
                st.markdown(f"""
                    <a href="{url}" target="_blank" style="text-decoration: none;">
                        <div class="news-card">
                            <img src="{image_url}" class="news-img">
                            <div class="news-content">
                                <p class="news-title">{title}</p>
                            </div>
                        </div>
                    </a>
                """, unsafe_allow_html=True)
    else:
        st.write("No latest news available.")

# Function to fetch weather data
def get_weather():
    try:
        geo_url = "http://ip-api.com/json/"
        location_data = requests.get(geo_url).json()
        city = location_data["city"]
        country = location_data["country"]

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        weather_data = requests.get(weather_url).json()

        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        weather_desc = weather_data["weather"][0]["description"]
        icon = weather_data["weather"][0]["icon"]

        return city, country, temp, humidity, weather_desc, icon
    except:
        return None, None, None, None, None, None

# Convert an image to Base64 for embedding
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Saving a background image
bg_image_path = "bg_weather.jpg"
bg_image_base64 = get_base64_image(bg_image_path)

# Sidebar Header
st.sidebar.markdown("<h2 style='text-align: center;'>🌤 Weather Update</h2>", unsafe_allow_html=True)

# Custom CSS to apply to background image
st.sidebar.markdown(
    f"""
    <style>
        .weather-card {{
            background: url("data:image/jpg;base64,{bg_image_base64}");
            background-size: cover;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.3);
            position: relative;
        }}
        .weather-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 18px;
            font-weight: bold;
            padding-bottom: 5px;
        }}
        .weather-temp {{
            font-size: 28px;
            font-weight: bold;
            margin-top: -5px;
        }}
        .weather-humidity {{
            font-size: 14px;
        }}
        .forecast-button {{
            display: block;
            background-color: rgba(0, 0, 0, 0.6);
            color: white !important;
            padding: 8px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 14px;
            font-weight: bold;
            margin-top: 10px;
        }}
        .forecast-button:hover {{
            background-color: rgba(0, 0, 0, 0.8);
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Fetch Weather Data
city, country, temp, humidity, weather_desc, icon = get_weather()

# Display in Sidebar
if city:
    st.sidebar.markdown(
        f"""
        <div class="weather-card">
            <div class="weather-header">
                <span>📍 {city}</span>
                <span>💧 {humidity}%</span>
            </div>
            <div class="weather-temp">{temp}°C</div>
            <a class="forecast-button" href="https://www.weather.com/weather/today/l/{city}" target="_blank">See full forecast</a>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.write("⚠ Unable to fetch weather data.")

# Main Sentiment Analysis
company_name = st.text_input("🔎 Enter a company name", "Tesla")

if st.button("Analyze News 🎯"):
    url = f"https://newsapi.org/v2/everything?q={company_name}&language=en&apiKey={API_KEY}"
    response = requests.get(url)
    
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])

        if not articles:
            st.write(f"No news articles found for **{company_name}**.")
        else:
            st.write(f"Found {len(articles)} articles for **{company_name}**. Showing the top 25 recent ones.")

            sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
            article_details = []

            # Process articles before generating Hindi summary
            for idx, article in enumerate(articles[:25]):
                title = article.get("title", "No Title Available")
                summary = article.get("description", "No Summary Available")
                source = article.get("source", {}).get("name", "Unknown Source")
                url = article.get("url", "#")

                # Perform Sentiment Analysis
                sentiment_score = sia.polarity_scores(summary)["compound"]
                sentiment = "Positive" if sentiment_score >= 0.05 else "Negative" if sentiment_score <= -0.05 else "Neutral"
                sentiment_counts[sentiment] += 1

                article_details.append({
                    "index": idx + 1,
                    "title": title,
                    "summary": summary,
                    "source": source,
                    "sentiment": sentiment,
                    "score": sentiment_score,
                    "url": url
                })

            # Generate hindi summary
            hindi_summary = f"""
            {company_name} के लिए कुल 25 समाचार लेखों का विश्लेषण किया गया है।
            सकारात्मक समाचार लेखों की संख्या {sentiment_counts['Positive']} है।
            नकारात्मक समाचार लेखों की संख्या {sentiment_counts['Negative']} है।
            तटस्थ समाचार लेखों की संख्या {sentiment_counts['Neutral']} है।
            """

            # Convert Hindi Summary to Speech
            try:
                tts = gTTS(text=hindi_summary, lang='hi', slow=False)
                tts_path = "hindi_summary.mp3"
                tts.save(tts_path)
                st.subheader("🎙 Listen to Hindi Summary")
                st.audio(tts_path, format="audio/mp3")
            except Exception as e:
                st.error(f"Error generating Hindi summary: {e}")

            # Ensure all 25 articles are displayed after the Hindi summary
            st.subheader(f"📰 Top 25 News Articles for {company_name}")

            for article in article_details:
                st.subheader(f"{article['index']}. {article['title']}")
                st.write(f"📌 **Source:** {article['source']}")
                st.write(f"📝 **Summary:** {article['summary']}")
                st.write(f"📊 **Sentiment:** {article['sentiment']} (Score: {article['score']})")
                st.write(f"🔗 [Read Full Article]({article['url']})")

            # Display sentiment analysis summary
            st.subheader("📊 Sentiment Analysis Summary")
            st.write(sentiment_counts)

    else:
        st.error(f"Failed to fetch news. Status code: {response.status_code}")