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

import psycopg2

# Define your connection details
conn = psycopg2.connect(
    dbname="ibmclouddb",
    user="ibm_cloud_9a3059c8_df57_4e99_ae38_a34e20de34d4",
    password="qko9r5ISR5ip4BFD3nr7n4yP5g0ykT9A",
    host="50e2a09d-d988-405b-b8de-7a885f365743.497129fd685f442ca4df759dd55ec01b.databases.appdomain.cloud",
    port="31244"
)

cur = conn.cursor()

# List all tables in the public schema
cur.execute("""
    SELECT * from user_feedback;
""")
rows = cur.fetchall()
print("Rows in the 'user_feedback' table:")
for row in rows:
    print(row)

cur.close()
conn.close()
