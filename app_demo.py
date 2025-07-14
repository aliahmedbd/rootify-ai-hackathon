# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
from graphs.build_graph import build_supervisor_graph
import psycopg2



@st.cache_resource
def get_graph():
    print("Building the graph...")
    graph = build_supervisor_graph()
    print("Graph has been built.")
    return graph

graph = get_graph() 

# Streamlit UI components
st.title("Rootify - NatWest Demo")
st.sidebar.image('images/natwest_logo.jpg', use_container_width=True)
st.sidebar.image('images/watsonx_logo.jpg', use_container_width=True)


# Upload file
uploaded_file = st.file_uploader("Upload your log file", type=["txt"])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Read the file content as a string
    file_content = uploaded_file.read().decode("utf-8")

    # Display the file content
    st.subheader("Log Files Uploaded")
    query = file_content  # Use the file content as the query

    if st.button("Process Logs"):

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

        response = results[-1]['handle_response']['final_response']

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
