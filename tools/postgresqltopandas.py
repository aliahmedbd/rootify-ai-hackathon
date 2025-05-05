import psycopg2
import pandas as pd
# from connectors.db_connector import PostgresConnector

# Establish connection
# pg_connector = PostgresConnector()
conn = psycopg2.connect(
    host="50e2a09d-d988-405b-b8de-7a885f365743.497129fd685f442ca4df759dd55ec01b.databases.appdomain.cloud",
    port="31244",
    database="ibmclouddb",
    user="ibm_cloud_9a3059c8_df57_4e99_ae38_a34e20de34d4",
    password="qko9r5ISR5ip4BFD3nr7n4yP5g0ykT9A"
)

# Create a cursor object
cur = conn.cursor()

# Execute the query
query = 'SELECT * FROM "TEST"'
cur.execute(query)

# Fetch all rows from the executed query
rows = cur.fetchall()

# Get column names from the cursor description
colnames = [desc[0] for desc in cur.description]

# Convert to Pandas DataFrame
df = pd.DataFrame(rows, columns=colnames)

# Close the cursor and connection
cur.close()
conn.close()

# Display the DataFrame
print(df)