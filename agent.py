from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
import os.path
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import re
from bs4 import BeautifulSoup
from connection import find_messages, get_creds

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
load_dotenv()

creds = get_creds()

def deleteMessage(messageID):
    service = build("gmail", "v1", credentials=creds)
    service.users().messages().trash(userId="me", id=messageID).execute()

messages_for_llm = find_messages()

tools = [
    Tool(
        name="Delete Email",  # Name of the tool
        func=deleteMessage,  # Function that the tool will execute
        # Description of the tool
        description="Useful to remove unwanted messages.",
    ),
]

prompt = hub.pull("hwchase17/react")

llm = ChatOpenAI(
    model="gpt-4o", temperature=0
)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
)


for i in messages_for_llm:

    initial_response = "You have access to the following email: \n" + i + "\n" + "The user is currently a student applying to jobs, and wants to remove emails that are scams or advirtising things that are unrelated to job hunting. To delete a message use the message ID. Additionally, any emails that are  just a thanks for applying please delete it unless it has information about an online assessment. Explain why you deleted said job."

    response = agent_executor.invoke({"input": initial_response})

    # Print the response from the agent
    print("response:", response)