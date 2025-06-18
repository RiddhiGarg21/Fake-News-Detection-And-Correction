from flask import Flask, request, render_template, redirect
import pickle
import requests
import numpy as np
import os
import csv
import pandas as pd

app = Flask(__name__)

# Load model and vectorizer
with open("pa_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

API_KEY = "AIzaSyCzigrdagvpYKtsRe2MA4V_7MdQAZnYmNc"

# Google Fact Check API
def get_correction_sources(text):
    sources = []
    if not API_KEY:
        return sources
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={text}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "claims" in data:
            for claim in data["claims"]:
                for review in claim.get("claimReview", []):
                    if review.get("url"):
                        sources.append({
                            "source": review.get("publisher", {}).get("name", "Unknown"),
                            "url": review["url"],
                            "rating": review.get("textualRating", "Unrated")
                        })
    except Exception as e:
        print(f"Google API error: {e}")
    return sources[:3]

@app.route('/')
def home():
    return render_template("index.html", show_result=False)

@app.route('/prediction', methods=['POST'])
def prediction():
    news_text = request.form.get('news_input')
    if not news_text or news_text.strip() == "":
        return render_template("index.html", error="Please enter news content.", show_result=False)

    try:
        X_input = vectorizer.transform([news_text]).toarray()
        prediction = model.predict(X_input)[0]

        result = "Real News" if prediction == 1 else "Fake News"

        # Confidence estimation
        raw_score = np.dot(X_input, model.w)[0]
        confidence = round(100 * (1 / (1 + np.exp(-abs(raw_score)))), 2)

        correction_sources = get_correction_sources(news_text) if prediction == 0 else []
        correction_message = (
            "This appears to be reliable information."
            if prediction == 1 else
            "⚠ This content may be misleading. Here are verified sources:"
        )

        # Feedback summary check
        feedback_response = None
        feedback_file = 'feedback_votes.csv'
        if os.path.exists(feedback_file):
            df = pd.read_csv(feedback_file)
            matched = df[df['News Text'] == news_text]
            if not matched.empty:
                feedback_counts = matched['User Feedback'].value_counts()
                if 'Yes' in feedback_counts and feedback_counts['Yes'] > feedback_counts.get('No', 0):
                    feedback_response = "Most users agreed ✅ this result is correct."
                elif 'No' in feedback_counts:
                    feedback_response = "Most users disagreed ❌ with this result."

        return render_template(
            "index.html",
            show_result=True,
            result=result,
            confidence=confidence,
            correction=correction_message,
            news_input=news_text,
            correction_sources=correction_sources,
            feedback_response=feedback_response,
            error=None
        )

    except Exception as e:
        print(f"Prediction error: {e}")
        return render_template("index.html", error="An error occurred during prediction.", show_result=False)

@app.route('/feedback_vote', methods=['POST'])
def feedback_vote():
    news_text = request.form.get('news_input')
    predicted_label = request.form.get('predicted_label')
    user_feedback = request.form.get('user_feedback')

    feedback_file = 'feedback_votes.csv'
    file_exists = os.path.isfile(feedback_file)

    try:
        with open(feedback_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['News Text', 'Predicted Label', 'User Feedback'])
            writer.writerow([news_text, predicted_label, user_feedback])
    except Exception as e:
        print(f"Feedback save error: {e}")

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
