import logging
from flask import Flask, request, jsonify, render_template
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from flask_migrate import Migrate
import os
from flask_sqlalchemy import SQLAlchemy
import pickle
import streamlit as sl
import streamlit as st
import requests

# Define the Flask API endpoint
FLASK_API_URL = "http://127.0.0.1:5000/chat"  # Make sure this URL is correct

# Set up Streamlit app title and instructions
st.title("AI Chatbot")

st.markdown("""
    This is a simple chatbot interface where you can talk to an AI.
    Please provide your user ID and name, then enter a message to get a response from the AI.
""")

# Create input fields for user ID, user name, and message
with st.form(key="chat_form"):
    user_id = st.number_input("User ID", min_value=1)
    user_name = st.text_input("User Name")
    user_input = st.text_area("Your Message")
    submit_button = st.form_submit_button(label="Send")

# Check if the form is submitted
if submit_button:
    if not user_name or not user_input:
        st.error("Please fill in all the fields.")
    else:
        # Send the user data to the Flask API
        payload = {
            'user_id': user_id,
            'user_name': user_name,
            'input': user_input
        }
        
        # Make POST request to Flask API
        try:
            response = requests.post(FLASK_API_URL, json=payload)

            if response.status_code == 200:
                # Display the AI's response
                response_data = response.json()
                ai_response = response_data.get('response', 'Sorry, something went wrong!')
                st.write(f"AI: {ai_response}")
            else:
                st.error(f"Error: {response.status_code}, {response.json().get('error')}")
        except Exception as e:
            st.error(f"Error: {e}")



# Initialize Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database Model for storing user interactions
class UserInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    user_name = db.Column(db.String(90), nullable=False)
    conversation_memory = db.Column(db.LargeBinary)

# Retrieve API key from environment variables
api_key = os.getenv('gen_key')

def Model():
    try:
        logger.info("Initializing the model...")
        llm = ChatGoogleGenerativeAI(
            api_key=api_key,
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        logger.info("Model initialized successfully.")
        return llm
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        return None

def set_chain_memory(existing_memory=None):
    try:
        logger.info("Setting up conversation chain...")
        obj = Model()
        if obj is None:
            raise ValueError("Failed to initialize model")

        memory = ConversationBufferMemory(return_messages=True)
        
        # Load existing memory if available
        if existing_memory:
            memory.chat_memory.messages.extend(existing_memory.chat_memory.messages)

        conversation = ConversationChain(
            llm=obj,
            verbose=True,
            memory=memory
        )
        logger.info("Conversation chain setup successfully.")
        return conversation
    except Exception as e:
        logger.error(f"Error setting up conversation chain: {e}")
        return None

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        logger.info("Received a chat request.")

        user_input = request.json.get('input')
        user_id = request.json.get('user_id')
        user_name = request.json.get('user_name')

        if not user_input or not user_id or not user_name:
            logger.warning("Incomplete user data provided.")
            return jsonify({'error': 'Input, user ID, and user name are required'}), 400

        # Check if the user already exists in the database
        existing_user = UserInteraction.query.filter_by(user_id=user_id).first()

        if existing_user:
            logger.info(f"User {user_id} exists. Continuing conversation.")
            existing_memory = pickle.loads(existing_user.conversation_memory)
            conversation = set_chain_memory(existing_memory=existing_memory)
        else:
            logger.info(f"New user {user_id}. Starting new conversation.")
            conversation = set_chain_memory()

        # Generate AI response
        response = conversation.predict(input=user_input)

        # Update or create the user interaction in the database
        if existing_user:
            updated_memory = conversation.memory
            existing_user.conversation_memory = pickle.dumps(updated_memory)
            db.session.commit()
            logger.info(f"Updated conversation memory for user {user_id}")
        else:
            new_interaction = UserInteraction(
                user_id=user_id,
                user_name=user_name,
                conversation_memory=pickle.dumps(conversation.memory)
            )
            db.session.add(new_interaction)
            db.session.commit()
            logger.info(f"New user {user_id} added to the database.")

        logger.info(f"Response generated: {response}")
 

        return jsonify({'response': response})

    except Exception as e:
        logger.error(f"Error during conversation: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, use_reloader=False)
