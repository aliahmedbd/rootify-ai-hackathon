import argparse
from dotenv import load_dotenv
_ = load_dotenv()

from tests.test_api import (
    test_postgres_create_table, 
    test_postgres_insert_data, 
    test_postgres_query_data
)
from tools.generate_report import generate_reports
from dotenv import load_dotenv
_ = load_dotenv()

# Function map
FUNCTION_MAP = {
    "test_generate_reports": generate_reports,
    "test_postgres_create_table": test_postgres_create_table,
    "test_postgres_insert_data": test_postgres_insert_data,
    "test_postgres_query_data": test_postgres_query_data,
}
# Parse command line arguments
parser = argparse.ArgumentParser(description="Run specific tests.")
parser.add_argument(
    "--function",
    choices=FUNCTION_MAP.keys(),
    help="Name of the test test function to run.",
)
args = parser.parse_args()
# Run the specified test function
if args.function:
    test_function = FUNCTION_MAP[args.function]
    data = test_function()
    print(data)
    print("Test Successfully Completed!")
else:
    # If no test name get them to choose one.
    print("Select function based on FUNCTION_MAP to run.")
