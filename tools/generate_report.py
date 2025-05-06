import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate


def query_postgres_to_pandas(host, port, database, username, password, query):
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
    try:
        # Establish a connection to the PostgreSQL database
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
        
        return df
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return None

def generate_html_report(df):
    """
    Generates an HTML report from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to convert to HTML.
    """
    html_table = df.to_html()
    with open('report.html', 'w') as f:
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
    plt.savefig('severity_chart.png')

def generate_summary_report(df):
    """
    Generates a summary report of the DataFrame and saves it as a text file.

    Args:
        df (pd.DataFrame): The DataFrame to summarize.
    """
    summary_table = tabulate(df.describe(), headers='keys', tablefmt='psql')
    with open('summary_report.txt', 'w') as f:
        f.write(summary_table)

# Example usage
if __name__ == "__main__":
    # Database credentials and query
    host = "50e2a09d-d988-405b-b8de-7a885f365743.497129fd685f442ca4df759dd55ec01b.databases.appdomain.cloud"
    port = 31244
    database = "ibmclouddb"
    username = "ibm_cloud_9a3059c8_df57_4e99_ae38_a34e20de34d4"
    password = "qko9r5ISR5ip4BFD3nr7n4yP5g0ykT9A"
    query = 'SELECT * FROM "TEST"'

    # Fetch data from PostgreSQL database
    df = query_postgres_to_pandas(host, port, database, username, password, query)

    # Check if data was successfully retrieved
    if df is not None:
        generate_html_report(df)
        generate_matplotlib_chart(df)
        generate_summary_report(df)
        print("Reports generated successfully.")
    else:
        print("Failed to generate reports due to a database error.")



