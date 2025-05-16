import os
import sys
#import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from connectors.db_connector import PostgresConnector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.tools import tool
from jinja2 import Template
load_dotenv()

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
        Generates a Matplotlib chart for the first column in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to generate a chart from.
            output_file (str): The output file path.
        """
        if not df.empty:
            column = df.columns[0]
            plt.figure(figsize=(10, 6))
            sns.countplot(x=column, data=df)
            plt.title(f'Distribution of {column}')
            plt.xlabel(column)
            plt.ylabel('Count')
            plt.savefig(output_file)
        else:
            print("DataFrame is empty. Cannot generate chart.")


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
    
    
class CombinedReportGenerator(ReportGenerator):
    def __init__(self, report_generators):
        self.report_generators = report_generators

    def generate_report(self, df, output_file='reports/combined_report.html'):
        """
        Generates a combined HTML report from the outputs of the provided report generators.

        Args:
            df (pd.DataFrame): The DataFrame to generate reports from.
            output_file (str): The output file path.
        """
        template = Template("""
<html>
<head>
    <title>Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f0f0f0;
        }
        img {
            width: 100%;
            height: auto;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .tabcontent {
            display: none;
            padding: 6px 12px;
            border: 1px solid #ccc;
            border-top: none;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #ccc;
        }
    </style>
</head>
<body>
    <h1>Combined Report</h1>
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'html-report')">HTML Report</button>
        <button class="tablinks" onclick="openTab(event, 'chart')">Chart</button>
        <button class="tablinks" onclick="openTab(event, 'summary-report')">Summary Report</button>
    </div>
    <div id="html-report" class="tabcontent">
        <h2>HTML Report</h2>
        {{ html_report }}
    </div>
    <div id="chart" class="tabcontent">
        <h2>Chart</h2>
        <img src="severity_chart.png" alt="Severity Chart" />
    </div>
    <div id="summary-report" class="tabcontent">
        <h2>Summary Report</h2>
        <pre>{{ summary_report }}</pre>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
    </script>
</body>
</html>
""")

        # Generate reports using the provided generators
        html_report = ''
        summary_report = ''

        for generator in self.report_generators:
            if isinstance(generator, HTMLReportGenerator):
                generator.generate_report(df, output_file='reports/temp.html')
                with open('reports/temp.html', 'r') as f:
                    html_report = f.read()
            elif isinstance(generator, MatplotlibChartGenerator):
                generator.generate_report(df, output_file='reports/severity_chart.png')
            elif isinstance(generator, SummaryReportGenerator):
                generator.generate_report(df, output_file='reports/summary_report.txt')
                with open('reports/summary_report.txt', 'r') as f:
                    summary_report = f.read()

        html_content = template.render(html_report=html_report, summary_report=summary_report)

        with open(output_file, 'w') as f:
            f.write(html_content)

    
class ReportAgent:
    def __init__(self, data_fetcher, report_generators, combined_report_generator=None):
        self.data_fetcher = data_fetcher
        self.report_generators = report_generators
        self.combined_report_generator = combined_report_generator

    def generate_reports(self, query):
        df = self.data_fetcher.fetch_data(query)
        if df is not None:
            for generator in self.report_generators:
                generator.generate_report(df)
            
            if self.combined_report_generator:
                self.combined_report_generator.generate_report(df)
            
            return "Reports generated successfully."
        else:
            return "Failed to generate reports due to a database error."



class GenerateReportsInput(BaseModel):
    query: str = "SQL query to fetch data for report generation"

@tool(args_schema=GenerateReportsInput)
def generate_reports(query: str):
    """
    Generates reports based on the provided SQL query.

    Args:
        query (str): The SQL query to fetch data for report generation.

    Returns:
        str: A message indicating whether the reports were generated successfully or not.
    """
    connector = PostgresConnector()
    data_fetcher = DataFetcher(connector)

    html_generator = HTMLReportGenerator()
    matplotlib_generator = MatplotlibChartGenerator()
    summary_generator = SummaryReportGenerator()

    report_generators = [html_generator, matplotlib_generator, summary_generator]
    combined_report_generator = CombinedReportGenerator(report_generators)
    report_agent = ReportAgent(data_fetcher, report_generators, combined_report_generator)

    return report_agent.generate_reports(query)

