from datetime import date
from dotenv import load_dotenv
_ = load_dotenv()
from connectors.db_connector import PostgresConnector
from connectors.db_schemas.table_schema import TablesSchema


pg_connector = PostgresConnector()

# schema = TablesSchema.postgres_metadata_schema
# print(schema)

# pg_connector.create_table(table_name="TEST", schema=schema)

# data = {
#     "id": 1,
#     "query": "This is a Test",
#     "issue": "Test Issue",
#     "severity": 1,
#     "createdate": date.today(),
#     "status": "Open",
#     "resolutiondate": None
# }

# pg_connector.insert_data(table_name="TEST", data=data)

# breakpoint()
query = 'SELECT * FROM "TEST"'

pg_connector.query_data(query=query)