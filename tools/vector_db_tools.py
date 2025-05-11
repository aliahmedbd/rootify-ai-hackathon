from connectors.vector_db_connector import vectorDbConnector

from pydantic import BaseModel, Field
from typing import Dict, Union, Any
from langchain.agents import tool


class vectorDbAgentTools:

    class SearchInput(BaseModel):
        query: str = Field(description="The search query for vectordb to run")
        k: int = Field(description="Top k results of search")

    @tool(args_schema=SearchInput)
    def similarity_search(query: str, k: int):
        """
        Perform search on a vector db.
        :query: the query to search in the vector db.
        :return: List of search results.
        """

        vdb_connector = vectorDbConnector()
        response = vdb_connector.similarity_search(query=query, k=k)
        return response
