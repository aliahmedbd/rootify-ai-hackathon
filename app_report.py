# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
from graphs.build_graph import build_supervisor_graph
from tools.report_generatorC_tools import generate_reports_tools
import psycopg2
import json
from streamlit_option_menu import option_menu
import smtplib
from email.message import EmailMessage


def send_report_via_gmail(
    to_email,
    subject="Your DevOpsAssist Report",
    body="Please find the attached report.",
    report_path="reports/combined_report.html",
    from_email="sivajimanju11@gmail.com",         # <-- your Gmail address
    from_password="yqny bukq oeit rsgd",         # <-- your Gmail App Password
    smtp_server="smtp.gmail.com",
    smtp_port=587
):
    # Read the report file
    with open(report_path, "rb") as f:
        report_data = f.read()

    # Create the email
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)
    msg.add_attachment(report_data, maintype="text", subtype="html", filename="report.html")

    # Send the email via Gmail SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)


@st.cache_resource
def get_graph():
    print("Building the graph...")
    graph = build_supervisor_graph()
    print("Graph has been built.")
    return graph

 

graph = get_graph()

# Streamlit UI components
st.title("DevOpsAssist")
st.sidebar.image('images/Finastra-logo.jpg', use_container_width=True)

# --- Sidebar: Report generation query and parameters ---
st.sidebar.markdown("## Generate Report")

column_options = [
    "🔴 Issue Type",
    "🟢 Status",
    "🔵 Assignee",
    "🟡 Summary",
    "🟣 Resolution",
    "⚫ Created",
    "🔵 Key",
    "🔴 Priority",
]

column_map = {
    "🔴 Issue Type": "Issue Type",
    "🟢 Status": "Status",
    "🔵 Assignee": "Assignee",
    "🟡 Summary": "Summary",
    "🟣 Resolution": "Resolution",
    "⚫ Created": "Created",
    "🔵 Key": "Key",
    "🔴 Priority": "Priority",
}

agg_functions = ["COUNT"]
chart_types = [
    "📊 bar",
    "🥧 pie",
    "📈 line"
]
chart_type_map = {
    "📊 bar": "bar",
    "🥧 pie": "pie",
    "📈 line": "line",
    "bar": "bar",
    "pie": "pie",
    "line": "line"
}
selected_columns = st.sidebar.multiselect("Select columns", column_options, default=["🔴 Issue Type"])
selected_agg = st.sidebar.selectbox("Aggregate Function", agg_functions)
selected_chart = st.sidebar.selectbox("Chart Type", chart_types)

generate_report_clicked = st.sidebar.button("Generate Jira Inflows and Outflows Report")

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
    # Set a session flag to keep the report/email section visible
    st.session_state["report_ready"] = True
    if selected_columns:
        group_by = ", ".join([f'"{column_map[col]}"' for col in selected_columns])
        agg_col = column_map[selected_columns[0]]  # You may want to let user pick this for SUM/AVG/MIN/MAX
        if selected_agg == "COUNT":
            agg_expr = "COUNT(*)"
        else:
            agg_expr = f"{selected_agg}(\"{agg_col}\")"
        sql_query = f"SELECT {group_by}, {agg_expr} as agg_value FROM jira_data GROUP BY {group_by}"

        # Call your report generation tool with the built query
        tool_input = {
            "query": sql_query,
            "chart_type": chart_type_map.get(selected_chart, "bar")
        }
        generate_reports_tools(tool_input)

        st.success("Report triggered with your selected parameters.")
        # Save report content to session state for later use
        with open("reports/combined_report.html", "r") as file:
            report_content = file.read()
        st.session_state["report_content"] = report_content

# Show report/email section if report is ready
if st.session_state.get("report_ready", False):
    import streamlit.components.v1 as components
    report_content = st.session_state.get("report_content", "")
    if report_content:
        components.html(report_content, height=800, scrolling=True)
        st.download_button(
            label="Download Report",
            data=report_content,
            file_name="report.html",
            mime="text/html"
        )

    # --- Email Report Section ---
    with st.form("email_report_form"):
        st.markdown("#### Email the generated report")
        to_email = st.text_input("Recipient Email")
        send_email = st.form_submit_button("Send Report")
        if send_email and to_email:
            try:
                send_report_via_gmail(
                    to_email=to_email,
                    from_email="sivajimanju11@gmail.com",
                    from_password="yqny bukq oeit rsgd",
                )
                st.session_state["email_status"] = f"Report sent to {to_email}!"
                st.session_state["email_status_type"] = "success"
            except Exception as e:
                st.session_state["email_status"] = f"Failed to send email: {e}"
                st.session_state["email_status_type"] = "error"

    # Show email status message after form submission
    if "email_status" in st.session_state:
        if st.session_state["email_status_type"] == "success":
            st.success(st.session_state["email_status"])
        else:
            st.error(st.session_state["email_status"])

# --- Feedback Section (Sidebar) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Feedback")

with st.sidebar.form("feedback_form"):
    feedback_text = st.text_area("Your feedback", height=100)
    submit_feedback = st.form_submit_button("Submit Feedback")
    if submit_feedback and feedback_text.strip():
        try:
            # Connect to your Postgres DB
            conn = psycopg2.connect(
                dbname="ibmclouddb",
                user="ibm_cloud_9a3059c8_df57_4e99_ae38_a34e20de34d4",
                password="qko9r5ISR5ip4BFD3nr7n4yP5g0ykT9A",
                host="50e2a09d-d988-405b-b8de-7a885f365743.497129fd685f442ca4df759dd55ec01b.databases.appdomain.cloud",
                port="31244"
            )
            cur = conn.cursor()
            # Optionally, get username from session or input
            username = "anonymous"  # Replace with actual user info if available
            cur.execute(
                "INSERT INTO user_feedback (username, feedback) VALUES (%s, %s);",
                (username, feedback_text)
            )
            conn.commit()
            cur.close()
            conn.close()
            st.sidebar.success("Thank you for your feedback!")
        except Exception as e:
            st.sidebar.error(f"Failed to submit feedback: {e}")

def send_report_via_outlook(
    to_email,
    subject="Your DevOpsAssist Report",
    body="Please find the attached report.",
    report_path="reports/combined_report.html",
    from_email="sivajimanju11@gmail.com",
    from_password="Manju777",
    smtp_server="smtp.office365.com",
    smtp_port=587
):
    # Read the report file
    with open(report_path, "rb") as f:
        report_data = f.read()

    # Create the email
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)
    msg.add_attachment(report_data, maintype="text", subtype="html", filename="report.html")

    # Send the email via Outlook SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)

def send_report_via_gmail(
    to_email,
    subject="Your DevOpsAssist Report",
    body="Please find the attached report.",
    report_path="reports/combined_report.html",
    from_email="sydney.waelchi@ethereal.email",         # <-- your Gmail address
    from_password="heRX4bXF272rNkyRTW",   # <-- your Gmail App Password
    smtp_server="smtp.ethereal.email",
    smtp_port=587
):
    # Read the report file
    with open(report_path, "rb") as f:
        report_data = f.read()

    # Create the email
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)
    msg.add_attachment(report_data, maintype="text", subtype="html", filename="report.html")

    # Send the email via Gmail SMTP
    with smtplib.SMTP("smtp.ethereal.email", 587) as server:
        server.starttls()
        server.login("sydney.waelchi@ethereal.email", "heRX4bXF272rNkyRTW")
        server.send_message(msg)

with st.form("email_report_form"):
    st.markdown("#### Email the generated report")
    to_email = st.text_input("Recipient Email")
    send_email = st.form_submit_button("Send Report")
    if send_email and to_email:
        try:
            send_report_via_gmail(
                to_email=to_email,
                from_email="sydney.waelchi@ethereal.email",         # <-- your Gmail address
                from_password="heRX4bXF272rNkyRTW",   # <-- your Gmail App Password
            )
            st.success(f"Report sent to {to_email}!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")

