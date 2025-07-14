from connectors.db_connector import PostgresConnector
import pandas as pd
from connectors.db_schemas.table_schema import TablesSchema
from dotenv import load_dotenv
_ = load_dotenv(override=True)


connector = PostgresConnector()
schema = TablesSchema.patterns_lookup_schema
data = pd.read_csv('data/error_patterns.csv').to_dict(orient='records')


connector.create_table(
    table_name="patterns_lookup",
    schema=schema
)

for row in data:
    connector.insert_data(
        table_name="patterns_lookup",
        data=row
    )
