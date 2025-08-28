import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Set API keys from environment variables
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

# Define available models
GOOGLE_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "meta-llama/llama-4-maverick-17b-128e-instruct", "gemma2-9b-it", "deepseek-r1-distill-llama-70b"]

def get_google_response(input_text, model):
    try:
        # Create the model and prompt
        llm = ChatGoogleGenerativeAI(model=model)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("user", "{input}")
        ])
        
        # Create and invoke the chain
        chain = prompt | llm
        result = chain.invoke({"input": input_text})
        
        return result.content
    except Exception as e:
        return f"Error: {e}"

def get_groq_response(input_text, model):
    try:
        # Create the model and prompt
        llm = ChatGroq(model=model)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("user", "{input}")
        ])
        
        # Create and invoke the chain
        chain = prompt | llm
        result = chain.invoke({"input": input_text})
        
        return result.content
    except Exception as e:
        return f"Error: {e}"

# Set up page config and title
st.set_page_config(page_title="Multi-Model Chatbot", layout="wide")
st.title('Multi-Modal Chatbot')

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Provider selection
provider = st.sidebar.selectbox("Choose provider", ["Google", "Groq"])

# Model selection based on provider
if provider == "Google":
    model_option = st.sidebar.selectbox("Choose Google model", GOOGLE_MODELS)
else:
    model_option = st.sidebar.selectbox("Choose Groq model", GROQ_MODELS)

# Input area
if prompt := st.chat_input("Enter your prompt"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if provider == "Google":
                response = get_google_response(prompt, model_option)
            else:
                response = get_groq_response(prompt, model_option)
            
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Add a button to clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
