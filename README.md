\# YouTube Comment Emotion Analyzer







\*\*\[Live Demo Link Here]\*\* <!-- We'll get this in the next step -->



\## 🚀 Project Description

A full-stack web application that analyzes the emotional tone of YouTube comments in real-time. Users can input a YouTube video URL, and the application fetches the latest comments, performs a deep contextual analysis using a state-of-the-art AI model, and visualizes the results as an interactive radar chart.



\## The Journey: From Simple Sentiment to Deep Emotion

This project was an iterative journey in Natural Language Processing (NLP).

\* \*\*V1 (Basic Sentiment):\*\* Initially, the app used `TextBlob`, a simple library for positive/negative sentiment. However, it failed to understand context and slang (e.g., classifying "this song is fire" as negative).

\* \*\*V2 (Emotion Model):\*\* I upgraded the backend to use a Transformer-based emotion classification model. This was more accurate but still struggled with modern, informal language.

\* \*\*V3 (State-of-the-Art):\*\* The final version uses a \*\*RoBERTa model trained specifically on millions of tweets\*\*. This model excels at understanding slang, sarcasm, and the cultural context of online comments, providing a highly accurate emotional profile of the audience. This evolution demonstrates a deep understanding of choosing the right tool for a specific NLP task.



\## 🛠️ Tech Stack

\* \*\*Backend:\*\* Python, Flask

\* \*\*AI/NLP:\*\* Hugging Face Transformers, PyTorch, `cardiffnlp/twitter-roberta-base-emotion-latest` model

\* \*\*API:\*\* Google YouTube Data API v3

\* \*\*Frontend:\*\* HTML, CSS, JavaScript

\* \*\*Data Visualization:\*\* Chart.js



\## ⚙️ How to Run Locally

1\.  Clone the repository: `git clone \[your-repo-url]`

2\.  Create and activate a virtual environment.

3\.  Install dependencies: `pip install -r requirements.txt`

4\.  Create a `.env` file and add your YouTube API key: `YOUTUBE\_API\_KEY=YOUR\_API\_KEY\_HERE`

5\.  Run the Flask application: `python app.py`

6\.  Open your browser to `http://127.0.0.1:5000/`





