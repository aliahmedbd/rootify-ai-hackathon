import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Make sure the following import matches the actual function name in report_generator_updated_tools.py
#from tools.report_generator_updated_tools import generate_reports_tools as generate_reports
from tools.report_generatorC_tools import generate_reports_tools as generate_reports
def test_report_generation_tools():
    # Count the number of issues
     # Count the number of issues
  #query = "SELECT COUNT(*) FROM jira_data"
  #result = generate_reports.invoke({"query": query})
  #print(result)

# Count the number of issues by status
  query = "SELECT \"Status\", COUNT(*) FROM jira_data GROUP BY \"Status\""
  result = generate_reports.invoke({"query":query})
  print(result)

# Count the number of issues by assignee
  #query = "SELECT \"Assignee\", COUNT(*) FROM jira_data GROUP BY \"Assignee\""
  #result = generate_reports.invoke({"query": query})
  #print(result)

# Count the number of issues by issue type
  #query = "SELECT \"Issue Type\", COUNT(*) FROM jira_data GROUP BY \"Issue Type\""
  #result = generate_reports.invoke({"query": query})
  #print(result)

# Count the number of issues by reporter
  #query = "SELECT \"Reporter\", COUNT(*) FROM jira_data GROUP BY \"Reporter\""
  #result = generate_reports.invoke({"query": query})
  #print(result)
