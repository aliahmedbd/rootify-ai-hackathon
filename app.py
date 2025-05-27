# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
from graphs.build_graph import build_general_agent_graph, build_general_agent_graph_with_report


# initiate the graph_build
print("Building the graph...")
graph = build_general_agent_graph_with_report()
print("Graph has been built.")

# Streamlit UI components
st.title("DevOpsAssist")
st.sidebar.image('images/Finastra-logo.jpg', use_container_width=True)
# st.subheader("Agent to Assist you with Maximo Work Orders")

import streamlit as st

# Initialize session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
query = st.text_input("Type your query here")

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

    with st.spinner("Generating response..."):
        # for output in graph.stream({
        #         'user_input': query,
        #         'supervisor_decision': '',
        #         'tool_calls': '',
        #         'agent_tool_retries':0,
        #         'agent_max_tool_retries': 3,
        #         'postgres_query': '',
        #         'postgres_agent_response': '',
        #         'vector_db_agent_response': '',
        #         'report_generation_requested': '',
        #         'report_generation_response': '',
        #         'final_response': '',
        #         'memory_chain': []
        #     }, thread):
        #     # Display the output in real-time
        #     st.write(output)

        result = graph.invoke(            
            {
                'user_input': query,
                'supervisor_decision': '',
                'tool_calls': '',
                'agent_tool_retries':0,
                'agent_max_tool_retries': 3,
                'postgres_query': '',
                'postgres_agent_response': '',
                'vector_db_agent_response': '',
                'report_generation_requested': '',
                'report_generation_response': '',
                'final_response': '',
                'memory_chain': []
            }
        )

    response = result['final_response']

    st.markdown("\n")

    col3, col4 = st.columns([5, 1])
    with col3:
        st.markdown(
            f"<div style='text-align: left; font-style: italic;'>{response}</div>",
            unsafe_allow_html=True,
        )

    with st.expander("Show Full Model Process", expanded=False):
        st.write("\n\n")
        st.write(result['memory_chain'])

    if result['report_generation_response'] == "Report Generated":
        with open("reports/combined_report.html", "r") as file:
            report_content = file.read()
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
    st.session_state.chat_history.append({
        "query": query,
        "response": response,
        "raw": result['memory_chain']
    })
