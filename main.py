from dotenv import load_dotenv
_ = load_dotenv(override=True)

from graphs.build_graph import build_general_agent_graph, build_general_agent_graph_with_report


def test_general_agent():
    graph = build_general_agent_graph()

    with open("general_agent.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    # for vectordb test
    user_input="How many records are there in the jira database?"
    user_input = "What technologies are supported for containerized deployment of FCC application?"

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
    print(result['final_response'])

    breakpoint()

def test_general_agent_with_reports():
    graph = build_general_agent_graph_with_report()

    with open("general_agent_with_report.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    # # for vectordb test
    # user_input="How many records are there in the jira database?"
    # user_input = "What technologies are supported for containerized deployment of FCC application?"

    # result = graph.invoke(
    #         {
    #                 'user_input': user_input,
    #                 'supervisor_decision': '',
    #                 'tool_calls': '',
    #                 'agent_tool_retries':0,
    #                 'agent_max_tool_retries': 3,
    #                 'postgres_query': '',
    #                 'postgres_agent_response': '',
    #                 'vector_db_agent_response': '',
    #                 'final_response': '',
    #                 'memory_chain': []
    #             }
    #     )
    # print(result['final_response'])

    # breakpoint()

# def test_report_generator_agent():
#     graph = build_report_generator_graph()

#     with open("report_generator_agent.png", "wb") as image_file:
#         image_file.write(graph.get_graph().draw_png())
    
#     print("Graph has been built and saved as report_generator_agent.png")
    

if __name__ == "__main__":
    
    test_general_agent_with_reports()