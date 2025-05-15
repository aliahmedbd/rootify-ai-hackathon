import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from connectors.db_connector import PostgresConnector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

connector = PostgresConnector()
class ReportGenerator(ABC):
    @abstractmethod
    def generate_report(self, df):
        pass

class HTMLReportGenerator(ReportGenerator):
    def generate_report(self, df, output_file='reports/report.html'):
        """
        Generates an HTML report from the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to convert to HTML.
            output_file (str): The output file path.
        """
        html_table = df.to_html()
        with open(output_file, 'w') as f:
            f.write(html_table)

class MatplotlibChartGenerator(ReportGenerator):
    def generate_report(self, df, output_file='reports/severity_chart.png'):
        """
        Generates a Matplotlib chart for the 'severity' column in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the 'severity' column.
            output_file (str): The output file path.
        """
        plt.figure(figsize=(10, 6))
        sns.countplot(x='severity', data=df)
        plt.title('Severity Distribution')
        plt.xlabel('Severity')
        plt.ylabel('Count')
        plt.savefig(output_file)

class SummaryReportGenerator(ReportGenerator):
    def generate_report(self, df, output_file='reports/summary_report.txt'):
        """
        Generates a summary report of the DataFrame and saves it as a text file.

        Args:
            df (pd.DataFrame): The DataFrame to summarize.
            output_file (str): The output file path.
        """
        summary_table = tabulate(df.describe(), headers='keys', tablefmt='psql')
        with open(output_file, 'w') as f:
            f.write(summary_table)

class DataFetcher:
    def __init__(self, connector):
        self.connector = connector

    def fetch_data(self, query):
        """
        Fetches data from the database using the provided query.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The query result as a Pandas DataFrame.
        """
        data = self.connector.query_data(query=query)
        cols = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=cols)
        self.connector.close_connection()
        return df

class ReportAgent:
    def __init__(self, data_fetcher, report_generators):
        self.data_fetcher = data_fetcher
        self.report_generators = report_generators

    def generate_reports(self, query):
        df = self.data_fetcher.fetch_data(query)
        if df is not None:
            for generator in self.report_generators:
                generator.generate_report(df)
            print("Reports generated successfully.")
        else:
            print("Failed to generate reports due to a database error.")

# Example usage
if __name__ == "__main__":
    connector = PostgresConnector()
    data_fetcher = DataFetcher(connector)

    html_generator = HTMLReportGenerator()
    matplotlib_generator = MatplotlibChartGenerator()
    summary_generator = SummaryReportGenerator()

    report_generators = [html_generator, matplotlib_generator, summary_generator]
    report_agent = ReportAgent(data_fetcher, report_generators)

    query = 'SELECT * FROM "TEST"'
    report_agent.generate_reports(query)
