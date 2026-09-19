'''
config.py
Configuration settings for the AgentCT application.
'''

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load your API key from the .env file automatically
load_dotenv()

# Initialize the Gemini model 
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash",temperature=0.3)