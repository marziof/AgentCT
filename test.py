import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load your API key from the .env file automatically
load_dotenv()

# Initialize the Gemini model (gemini-2.5-flash is ideal for quick testing)
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash",temperature=0.3)

# Test the connection
# response = llm.invoke("Hello Gemini! Are you online?")
# print(response.content)


from pydantic import BaseModel

class InputModel(BaseModel):
    user_input: str
    assessment: str

from langchain.agents import create_agent
agent = create_agent(llm, tools=[], response_format=InputModel)
result = agent.invoke({"messages": "Hello Gemini! Are you online?"})

print(result)