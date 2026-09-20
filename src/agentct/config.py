'''
config.py
Configuration settings for the AgentCT application.
'''

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


# Load your API key from the .env file automatically
load_dotenv()

# Initialize the Gemini model 
#llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash",temperature=0.3)
llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.3)