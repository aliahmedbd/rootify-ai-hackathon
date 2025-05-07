import argparse
from dotenv import load_dotenv
_ = load_dotenv()

from tools.generate_report import generate_reports
from dotenv import load_dotenv
_ = load_dotenv()

# Function map
FUNCTION_MAP = {
    "test_generate_reports": generate_reports,
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
else:
    # If no test name is provided, run all tests
    generate_reports()
    print("All tests executed successfully.")

breakpoint()
