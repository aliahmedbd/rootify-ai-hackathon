#import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.report_generator_tools import generate_reports

def test_report_generation_tools():
    query = 'SELECT * FROM "TEST"'
    result = generate_reports.invoke({"query": query})
    print(result)

def main():
    test_report_generation_tools()

if __name__ == "__main__":
    main()
