from connectors.db_connector import PostgresConnector

from pydantic import BaseModel, Field
from typing import Dict, Union, Any
from langchain.agents import tool


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