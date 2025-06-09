# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
from graphs.build_graph import build_supervisor_graph
from tools.report_generatorC_tools import generate_reports_tools


# initiate the graph_build
print("Building the graph...")
graph = build_supervisor_graph()
print("Graph has been built.")

# Streamlit UI components
st.title("DevOpsAssist")
st.sidebar.image('images/Finastra-logo.jpg', use_container_width=True)

# --- Sidebar: Report generation query and parameters ---
st.sidebar.markdown("## Generate Report")

column_options = ["Issue Type", "Status", "Assignee", "Priority", "Created", "Resolved"]
agg_functions = ["COUNT", "SUM", "AVG", "MIN", "MAX"]
chart_types = ["Bar", "Pie", "Line"]

selected_columns = st.sidebar.multiselect("Select columns", column_options, default=["Issue Type", "Status"])
selected_agg = st.sidebar.selectbox("Aggregate Function", agg_functions)
selected_chart = st.sidebar.selectbox("Chart Type", chart_types)

generate_report_clicked = st.sidebar.button("Generate Report")

# --- Main UI: General chat input and response ---
st.markdown("## General Chat")
query = st.text_input("Type your query here", key="main_query")

col1, col2 = st.columns([2, 5])
# When query is submitted (Enter pressed)
if query:
    with col2:
        st.markdown(
            f"<div style='text-align: right; font-style: italic;'>{query}</div>",
            unsafe_allow_html=True,
        )
    # Generate response (can still show spinner)
    thread = {"configurable": {"thread_id": "1"}}

    results = []
    # Create a temporary placeholder for interim updates
    placeholder = st.empty()

    with st.spinner("Processing..."):
        for output in graph.stream({
                'user_input': query,
                'supervisor_decision': '',
                'tool_calls': '',
                'agent_tool_retries': 0,
                'agent_max_tool_retries': 3,
                'postgres_query': '',
                'postgres_agent_response': '',
                'vector_db_agent_response': '',
                'report_generation_requested': '',
                'report_generation_response': '',
                'final_response': '',
                'memory_chain': []
            }, thread):
            
            # Optionally print something useful during the stream
            current_step = output.keys()
            placeholder.markdown(f"Running step: `{list(current_step)[0]}`")  # Or any useful info
            
            results.append(output)

    # Clear the placeholder after processing
    placeholder.empty()

    response = results[-1]['handle_response']['final_response']

    st.markdown("\n")
    st.markdown("\n")

    col3, col4 = st.columns([5, 1])
    with col3:
        # Display response left-aligned
        st.markdown(
            f"<div style='text-align: left; font-style: italic;'>{response}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("\n")
    st.markdown("\n")

    with st.expander("Show Full Model Process", expanded=False):
        st.write("\n")
        st.write("\n")
        st.write(results[-1]['handle_response']['memory_chain'])

    if results[-1]['handle_response']['report_generation_response'] == "Report Generated":
        with open("reports/combined_report.html", "r") as file:
            report_content = file.read()
            # Display report left-aligned
            components.html(
                report_content,
                height=800,
                scrolling=True,
            )
        
        # Add a download button for the report
        st.download_button(
            label="Download Report",
            data=report_content,
            file_name="report.html",
            mime="text/html"
        )
    # Save query and response to session_state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.session_state.chat_history.append({
        "query": query,
        "response": response,
        "raw": results[-1]['handle_response']['memory_chain']
    })

# --- Report Generation Section ---
if generate_report_clicked:
    if selected_columns:
        group_by = ", ".join([f'"{col}"' for col in selected_columns])
        agg_col = selected_columns[0]  # You may want to let user pick this for SUM/AVG/MIN/MAX
        if selected_agg == "COUNT":
            agg_expr = "COUNT(*)"
        else:
            agg_expr = f"{selected_agg}(\"{agg_col}\")"
        sql_query = f"SELECT {group_by}, {agg_expr} as agg_value FROM jira_data GROUP BY {group_by}"

        # Call your report generation tool with the built query
        # If using generate_reports_tools as a LangChain tool:
        result = generate_reports_tools(sql_query)

        st.success("Report triggered with your selected parameters.")
        # Optionally, display the report or a download button here
        # (e.g., open and show reports/combined_report.html)
        import streamlit.components.v1 as components
        with open("reports/combined_report.html", "r") as file:
            report_content = file.read()
            components.html(report_content, height=800, scrolling=True)
        st.download_button(
            label="Download Report",
            data=report_content,
            file_name="report.html",
            mime="text/html"
        )
    else:
        st.error("Please select at least one column for the report.")

# --- Feedback Section (Sidebar) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Feedback")

with st.sidebar.form("feedback_form"):
    feedback_text = st.text_area("Your feedback", height=100)
    submit_feedback = st.form_submit_button("Submit Feedback")
    if submit_feedback and feedback_text.strip():
        # You can save feedback to a file, database, or send to an API here
        st.sidebar.success("Thank you for your feedback!")