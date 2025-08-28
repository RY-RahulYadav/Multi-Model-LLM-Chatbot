import requests
import streamlit as st
import json
import os
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def get_google_response(input_text, model):
    try:
        payload = {
            "input": {
                "input": input_text,
                "model": model
            },
            "config": {},
            "kwargs": {}
        }
        
        response = requests.post(
            f"{API_BASE_URL}/google-chat-api/invoke",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get('output', {}).get('content', 'No content received')
        
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"
    except KeyError as e:
        return f"Response parsing error: {e}"
    except Exception as e:
        return f"Error: {e}"

def get_groq_response(input_text, model):
    try:
        payload = {
            "input": {
                "input": input_text,
                "model": model
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}/groq-chat-api/invoke",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get('output', {}).get('content', 'No content received')
        
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"
    except KeyError as e:
        return f"Response parsing error: {e}"
    except Exception as e:
        return f"Error: {e}"

# Set page configuration
st.set_page_config(page_title="Multi-Model Chatbot", layout="wide")
st.title('Multi-Modal Chatbot')

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get available models
try:
    models_resp = requests.get(f"{API_BASE_URL}/models").json()
    google_models = models_resp.get("google", [])
    groq_models = models_resp.get("groq", [])
except Exception as e:
    st.error(f"Could not fetch models: {e}")
    google_models = ["gemini-1.5-flash"]
    groq_models = ["llama-3.1-8b-instant"]

# Provider selection in sidebar
provider = st.sidebar.selectbox("Choose provider", ["Google", "Groq"])

# Model selection based on provider in sidebar
if provider == "Google":
    model_option = st.sidebar.selectbox("Choose Google model", google_models)
else:
    model_option = st.sidebar.selectbox("Choose Groq model", groq_models)

# Add a button to clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Chat input
if prompt := st.chat_input("Enter your prompt"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if provider == "Google":
                response = get_google_response(prompt, model_option)
            else:
                response = get_groq_response(prompt, model_option)
            
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})