from connectors.db_connector import PostgresConnector

from pydantic import BaseModel, Field
from typing import Dict, Union, Any
from langchain.agents import tool
from langchain_core.messages import HumanMessage, SystemMessage


class PostGresAgentTools:

    class QueryInput(BaseModel):
        query:str = Field(description="The SQL query for postgres to run.")
        params: Any = Field(description="The parameters for the query to configure it/optimise it.")

    @tool(args_schema=QueryInput)
    def query_data(query: str, params=None):
        """
        Perform search on a vector db.
        :user_input: the query to search in the vector db.
        :return: List of search results.
        """

        pg_connector = PostgresConnector()
        response = pg_connector.query_data(query=query, params=params)
        return response
    

    @tool(args_schema=QueryInput)
    def run_query(query: str, params=None):
        """
        Perform search on a vector db.
        :user_input: the query to search in the vector db.
        :return: List of search results.
        """

        pg_connector = PostgresConnector()
        response = pg_connector.query_data(query=query, params=params)
        return response
    
    
    class GenerateSQLQuery(BaseModel):
        user_input: str = Field(description="The natural language user query to translate to a SQL Query.")
        system_prompt: Any = Field(description="The system prompt to use for generating the SQL query.")
        llm: Any = Field(description="LLM to use for generating the SQL query.")

    @tool(args_schema=GenerateSQLQuery)
    def generate_sql_query(user_input: str, system_prompt: str, llm: Any) -> Dict[str, Any]:
        """
        Generates the SQL query based on the user input.
        :param user_input: The user_input.
        :param system_prompt: The system prompt to use for generating the SQL query.
        :param llm: The LLM to use for generating the SQL query.
        :return: A dictionary containing the SQL query.
        """

        user_input = HumanMessage(
            content=user_input
        )
        messages = [
            system_prompt,
            user_input,
        ]

        response = llm.invoke(messages)
        query = response.content

        return query


