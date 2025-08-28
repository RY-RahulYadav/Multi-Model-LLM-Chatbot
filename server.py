from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes
from langchain_groq import ChatGroq
import uvicorn, os
from langchain.schema.runnable import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
port = int(os.environ.get("PORT", 8000)) 

app = FastAPI(
    title="Langchain Server",
    version="1.0",
    description="A simple API Server"
)

GOOGLE_MODELS = ["gemini-2.5-flash","gemini-2.5-flash-lite","gemini-2.5-flash"  ]
GROQ_MODELS   = ["llama-3.3-70b-versatile","llama-3.1-8b-instant","meta-llama/llama-4-maverick-17b-128e-instruct","gemma2-9b-it","deepseek-r1-distill-llama-70b"]

def google_dynamic_chain(inputs: dict):
    user_input = inputs.get("input")
    model_name = inputs.get("model", "gemini-1.5-flash")
    
    # Create the model and prompt
    model = ChatGoogleGenerativeAI(model=model_name)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("user", "{input}")
    ])
    
    # Create and invoke the chain, return the result
    chain = prompt | model
    result = chain.invoke({"input": user_input})
    return result

def groq_dynamic_chain(inputs: dict):
    user_input = inputs.get("input")
    model_name = inputs.get("model", "llama-3.1-8b-instant")
    
    # Create the model and prompt
    model = ChatGroq(model=model_name)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("user", "{input}")
    ])
    
    # Create and invoke the chain, return the result
    chain = prompt | model
    result = chain.invoke({"input": user_input})
    return result

# Create the runnable lambdas
google_chain = RunnableLambda(google_dynamic_chain)
groq_chain = RunnableLambda(groq_dynamic_chain)

# Add routes
add_routes(app, google_chain, path="/google-chat-api")
add_routes(app, groq_chain, path="/groq-chat-api")

@app.get("/models")
def get_models():
    return {"google": GOOGLE_MODELS, "groq": GROQ_MODELS}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=port)