import pickle  # To load the saved model and vectorizer
from fastapi import FastAPI  # FastAPI framework for building the web application
from pydantic import BaseModel  # For defining the structure of the request data
import re  # Regular expressions for text preprocessing
from nltk.corpus import stopwords  # To remove common English stopwords
import nltk  # Natural Language Toolkit for preprocessing
from nltk.stem.porter import PorterStemmer  # To perform stemming (reduce words to their root form)
from sklearn.feature_extraction.text import TfidfVectorizer  # Vectorizer for transforming text data into numerical form
nltk.download('stopwords')  # Download the stopwords dataset

# Initialize the Porter Stemmer for stemming
port_stem = PorterStemmer()

# Load the pre-trained machine learning model
model_path = "your_path"  # Path to the saved model
with open(model_path, 'rb') as f:
    model = pickle.load(f)  # Load the model using pickle

# Load the pre-trained TfidfVectorizer
vectorizer_path = r"your_path"  # Path to the saved vectorizer
with open(vectorizer_path, 'rb') as f:
    vectorizer = pickle.load(f)  # Load the vectorizer using pickle

# Initialize the FastAPI app
app = FastAPI()

# Define the schema for the request body using Pydantic
class TextRequest(BaseModel):
    text: str  # The input text for sentiment analysis

# Define a preprocessing function for text input
def preprocess(text: str):
    """
    Preprocess the input text by:
    - Removing non-alphabetic characters
    - Converting text to lowercase
    - Tokenizing and removing stopwords
    - Applying stemming
    """
    content = re.sub('[^a-zA-Z]', " ", text)  # Remove non-alphabetic characters
    content = content.lower()  # Convert text to lowercase
    content = content.split()  # Tokenize the text into words
    # Remove stopwords and apply stemming
    content = [port_stem.stem(word) for word in content if word not in stopwords.words('english')]
    content = " ".join(content)  # Join the processed words back into a single string
    return content

# Define the API endpoint for sentiment analysis
@app.post("/analyze/")
async def analyze_semantics(request: TextRequest):
    """
    Perform sentiment analysis on the input text.
    - Preprocess the input text
    - Transform it using the TfidfVectorizer
    - Use the loaded model to predict sentiment
    - Return the result as either "POSITIVE" or "NEGATIVE"
    """
    # Preprocess the input text
    preprocessed_txt = preprocess(request.text)
    # Transform the preprocessed text into a numerical vector
    txt = vectorizer.transform([preprocessed_txt])
    # Predict sentiment using the pre-trained model
    prediction = model.predict(txt)
    # Map the prediction to a human-readable result
    result = "POSITIVE" if prediction == 1 else "NEGATIVE"
    # Return the result as a JSON response
    return {"result": result}
