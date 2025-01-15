# ai-chatbot
# **AI Chatbot Using Flask and Streamlit**

This project is an AI-powered chatbot built using **Flask** for backend API handling and **Streamlit** for frontend user interaction. The chatbot leverages Google Generative AI (`gemini-1.5-flash`) through the `langchain_google_genai` library and stores user interactions in a **SQLite** database.

---

## **Features**
- Interactive chatbot interface using **Streamlit**.
- Persistent conversation memory stored in a local **SQLite** database.
- Backend API for handling chat requests via **Flask**.
- AI-generated responses using Google Generative AI model.
  
---

## **Project Structure**
```
|-- app.py                  # Main backend logic using Flask
|-- requirements.txt        # List of required dependencies
|-- user_data.db            # SQLite database for user interaction storage
|-- templates/              # Directory for HTML templates (if used)
```

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### **2. Install Required Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**
Create a `.env` file and set your **Google Generative AI API Key**:
```
gen_key=YOUR_API_KEY_HERE
```

### **4. Run the Flask API Backend**
```bash
python app.py
```

### **5. Run the Streamlit Frontend**
In a new terminal, run:
```bash
streamlit run app.py
```

---

## **Usage**
1. Open the Streamlit interface in your browser.
2. Enter your **User ID**, **User Name**, and your message.
3. The chatbot will generate AI-powered responses based on your input.

---

## **Dependencies**
- Flask
- Streamlit
- Langchain-Google-GenAI
- SQLAlchemy
- Requests
- Pickle

---

## **Contributions**
Feel free to fork this repository, submit issues, or create pull requests.

---

## **Acknowledgments**
- [LangChain](https://www.langchain.com/)
- [Streamlit](https://www.streamlit.io/)
- [Flask](https://flask.palletsprojects.com/)

