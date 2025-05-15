from langchain.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain_ibm import ChatWatsonx
from langchain.agents import initialize_agent
import os
from connectors.db_connector import PostgresConnector
clinet = PostgresConnector()
