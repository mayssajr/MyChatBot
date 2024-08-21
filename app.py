from flask import Flask, render_template, request, jsonify, json
import pickle
import nltk
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)

# Load the saved model, vectorizer, and label encoder
with open('model/label_encoder.pkl', 'rb') as le_file:
    le = pickle.load(le_file)

with open('model/vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

with open('model/model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('model/intents.json', 'r') as intents_file:
    intents = json.load(intents_file)

# NLTK setup
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Text preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(f'[{string.punctuation}]', '', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Prediction function
def predict_intent(text):
    processed_text = preprocess_text(text)
    X_test = vectorizer.transform([processed_text])
    prediction = model.predict(X_test)
    intent = le.inverse_transform(prediction)[0]
    return intent

# Define the home route
@app.route('/')
def home():
    return render_template('index.html')

# Define the chatbot response route
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message']
    intent = predict_intent(user_message)
    
    # Get the response for the predicted intent
    for intent_data in intents['intents']:
        if intent_data['tag'] == intent:
            response = intent_data['responses'][0]  # Get the first response for the predicted intent
            break
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
