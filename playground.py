# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from langchain.prompts import ChatPromptTemplate
# from langchain.agents import Tool
# from langchain_ibm import ChatWatsonx
# from langchain.agents import initialize_agent
# import os
import re
from connectors.db_connector import PostgresConnector
from agents.general_agent import GeneralAgent
from agents.base_agent import AgentState
from agents.general_agent import GeneralAgent
from agents.base_agent import AgentState
clinet = PostgresConnector()

state = AgentState(
    {
                'user_input': 'How many JIRA tickets are in the "in-progress" status?',
                'supervisor_decision': '',
                'tool_calls': 'generate_query',
                'agent_tool_retries':0,
                'agent_max_tool_retries': 3,
                'postgres_query': '',
                'postgres_agent_response': '',
                'vector_db_agent_response': '',
                'report_generation_requested': '',
                'report_generation_response': '',
                'final_response': '',
                'memory_chain': []
            }
)
agents = GeneralAgent()
state = agents.generate_sql_query(state=state)
query = state['postgres_query']
sql_query = re.search(r"SELECT.*;|UPDATE.*;|INSERT.*;", query)
#query = "SELECT COUNT(*) 'Status' = 'in-progress;"
#sql_query = re.search(r"SELECT.*;|UPDATE.*;|INSERT.*;", query)
#print(query)
#state['postgres_query'] = query   
#         state['postgres_agent_response'] = response
#response = clinet.run_query(query=query)    
#print(response) 
#PostgresConnector.validate_with_pglast = clinet.validate_with_pglast
#breakpoint()
#response = PostgresConnector.validate_with_pglast_Latest(sql=query)
print('query is :', sql_query.group(0))
response = PostgresConnector .validate_with_pglast_Latest(sql=sql_query.group(0))
#response = PostgresConnector.validate_with_pglast_Latest(sql=query)
print(response)