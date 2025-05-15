import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.report_generator_tools import ReportAgent, DataFetcher, HTMLReportGenerator, MatplotlibChartGenerator, SummaryReportGenerator
from connectors.db_connector import PostgresConnector
 
def main():
    # Initialize the Postgres connector
    connector = PostgresConnector()
    data_fetcher = DataFetcher(connector)
 
    # Initialize report generators
    html_generator = HTMLReportGenerator()
    matplotlib_generator = MatplotlibChartGenerator()
    summary_generator = SummaryReportGenerator()
 
    # Create a list of report generators
    report_generators = [html_generator, matplotlib_generator, summary_generator]
 
    # Create a report agent
    report_agent = ReportAgent(data_fetcher, report_generators)
 
    # Define the query to fetch data
    query = 'SELECT * FROM "TEST"'
 
    # Generate reports
    report_agent.generate_reports(query)
 
if __name__ == "__main__":
    main()
