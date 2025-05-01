import psycopg
from psycopg import sql
import os

class PostgresConnector:
    def __init__(self):
        """
        Initialize the PostgresConnector class.
        Establishes a connection to the PostgreSQL database.
        """
        try:
            self.conn = psycopg.connect(
                dbname=os.environ['PostGresDB'],
                user=os.environ['PostGresUser'],
                password=os.environ['PostGresPass'],
                host=os.environ['PostGresHost'],
                port=os.environ['PostGresPort'],
                connect_timeout=10
            )
            self.conn.autocommit = True  # Optional: Set autocommit mode
            print("Connection to PostgreSQL database established successfully.")
        except psycopg.Error as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            raise

    def create_table(self, table_name, schema):
        """
        Create a sample table with specified name.
        """
        create_table_query = sql.SQL("""CREATE TABLE IF NOT EXISTS {}""").format(sql.Identifier(table_name)) + sql.SQL(schema)

        with self.conn.cursor() as cur:
            cur.execute(create_table_query)
            print(f"Table '{table_name}' created or already exists.")

    def insert_data(self, table_name, data: dict):
        """
        Insert a single row into the specified table.
        `data` should be a dictionary where keys are column names and values are the values to insert.
        """
        columns = data.keys()
        values = data.values()

        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        with self.conn.cursor() as cur:
            cur.execute(insert_query, list(values))
            print(f"Inserted data into '{table_name}': {data}")


    def query_data(self, query, params=None):
        """
        Execute a custom SQL query and return the results.
        `query` should be a string or a psycopg.sql.SQL object.
        `params` is an optional tuple or list of parameters to bind to the query.
        """
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            print("Query results:")
            for row in rows:
                print(row)
            return rows


    def close_connection(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            print("PostgreSQL database connection closed.")
