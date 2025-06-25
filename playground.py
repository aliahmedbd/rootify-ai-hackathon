from connectors.vector_db_connector import MilvusConnector

connector = MilvusConnector()

query = "What technologies are supported for containerized deployment of FCC application?"

results = connector.search_milvus(query_text=query, top_k=3)

print(results)

breakpoint()
