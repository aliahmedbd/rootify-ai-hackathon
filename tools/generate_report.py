from connectors.db_connector import PostgresConnector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate


def query_postgres_to_pandas(query):
    """
    Queries a PostgreSQL database and retrieves the result as a Pandas DataFrame.
    
    Args:
        host (str): The database host.
        port (int): The database port.
        database (str): The database name.
        username (str): The username for authentication.
        password (str): The password for authentication.
        query (str): The SQL query to execute.
    
    Returns:
        pd.DataFrame: The query result as a Pandas DataFrame, or None if there's an error.
    """
    # Establish a connection to the PostgreSQL database
    conn = PostgresConnector()
    
    # fetch data with query (returns a list with item 0 being the list of cols)
    data = conn.query_data(query=query)
    cols = data[0]
    rows = data[1:]
    # Convert to Pandas DataFrame
    df = pd.DataFrame(rows, columns=cols)
    
    # Close the cursor and connection
    conn.close_connection()
    
    return df

def generate_html_report(df):
    """
    Generates an HTML report from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to convert to HTML.
    """
    html_table = df.to_html()
    with open('reports/report.html', 'w') as f:
        f.write(html_table)

def generate_matplotlib_chart(df):
    """
    Generates a Matplotlib chart for the 'severity' column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the 'severity' column.
    """
    plt.figure(figsize=(10, 6))
    sns.countplot(x='severity', data=df)
    plt.title('Severity Distribution')
    plt.xlabel('Severity')
    plt.ylabel('Count')
    plt.savefig('reports/severity_chart.png')

def generate_summary_report(df):
    """
    Generates a summary report of the DataFrame and saves it as a text file.

    Args:
        df (pd.DataFrame): The DataFrame to summarize.
    """
    summary_table = tabulate(df.describe(), headers='keys', tablefmt='psql')
    with open('reports/summary_report.txt', 'w') as f:
        f.write(summary_table)

def generate_reports():
    query = 'SELECT * FROM "TEST"'

    # Fetch data from PostgreSQL database
    df = query_postgres_to_pandas(query)

    # Check if data was successfully retrieved
    if df is not None:
        generate_html_report(df)
        generate_matplotlib_chart(df)
        generate_summary_report(df)
        print("Reports generated successfully.")
    else:
        print("Failed to generate reports due to a database error.")
