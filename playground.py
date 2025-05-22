import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from langchain.prompts import ChatPromptTemplate
# from langchain.agents import Tool
# from langchain_ibm import ChatWatsonx
# from langchain.agents import initialize_agent
# import os
from connectors.db_connector import PostgresConnector
clinet = PostgresConnector()
