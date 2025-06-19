# dashboard.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from pydantic import BaseModel
import pandas as pd
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import seaborn as sns
# Assuming ReportAgent is defined in report_agent.py
from tools.report_generatorC_tools import ReportAgent, GenerateReportsInput
from connectors.db_connector import PostgresConnector
from langchain_core.messages import HumanMessage, SystemMessage

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container(
    [
        html.H1("Report Generation Dashboard"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Textarea(
                        id="query-input",
                        placeholder="Enter SQL query",
                        style={"width": "100%", "height": 200},
                    ),
                    md=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Generate Reports", id="generate-reports-button", color="primary"),
                    md=12,
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id="report-status"),
                    md=12,
                ),
            ]
        ),
    ],
    className="p-5",
)

# Define the DataFetcher class
class DataFetcher:
    def __init__(self, connector):
        self.connector = connector

    def fetch_data(self, query):
        data = self.connector.query_data(query=query)
        cols = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=cols)
        self.connector.close_connection()
        return df

# Define the ReportGenerator abstract base class
class ReportGenerator(ABC):
    @abstractmethod
    def generate_report(self, df):
        pass

# Define the HTMLReportGenerator class
class HTMLReportGenerator(ReportGenerator):
    def generate_report(self,df, output_file='reports/report.html'):
        html_table = df.to_html()
        with open(output_file, 'w') as f:
            f.write(html_table)

# Define the MatplotlibChartGenerator class
class MatplotlibChartGenerator(ReportGenerator):
    def generate_report(self, df, output_file='reports/severity_chart.png'):
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

def convert_to_sql(nl_query, llm, prompt):
    messages = [prompt, HumanMessage(content=nl_query)]
    response = llm.invoke(messages)
    return response.content

# Define the callback for generating reports
@app.callback(
    Output("report-status", "children"),
    [Input("generate-reports-button", "n_clicks")],
    [State("query-input", "value")],
    prevent_initial_call=True,
)
def generate_reports(n_clicks, query):
    if n_clicks is not None:
        try:
            # Validate the input query
            GenerateReportsInput(query=query)
            
            # Initialize ReportAgent (assuming data_fetcher and report_generators are defined)
            connector = PostgresConnector()  # or your actual connector class
            data_fetcher = DataFetcher(connector)
            # Replace with actual report generators, e.g., a list of generator instances
            report_generators = [MatplotlibChartGenerator()]  # Example: using HTMLReportGenerator
            #combined_report_generator = CombinedReportGenerator()  # Optional
            
            report_agent = ReportAgent(data_fetcher, report_generators)
            
            # Generate reports
            # If no conversion is needed, use the query directly
            sql_query = query
            status = report_agent.generate_reports(sql_query)
            return dbc.Alert(status, color="success" if "successfully" in status else "danger")
        except Exception as e:
            return dbc.Alert(f"Error: {str(e)}", color="danger")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
