from dotenv import load_dotenv
_ = load_dotenv(override=True)

from graphs.build_graph import build_executor_graph


if __name__ == "__main__":
    
    graph = build_executor_graph()

    with open("graph_executor.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    # for vectordb test
    user_input="How many records are there in the jira database?"
    # for maximo test
    # user_input = "How many work orders were recorded to have priority 1 in december 31, 1998?"
    result = graph.invoke(
            {
                    'user_input': user_input,
                    'supervisor_decision': '',
                    'tool_calls': '',
                    'agent_tool_retries':0,
                    'agent_max_tool_retries': 3,
                    'postgres_query': '',
                    'postgres_agent_response': '',
                    'vector_db_agent_response': '',
                    'final_response': '',
                    'memory_chain': []
                }
        )
    print(result)

    breakpoint()
