from dotenv import load_dotenv
_ = load_dotenv()

from src.build_graph import build_graph


if __name__ == "__main__":
    
    graph = build_graph()

    with open("graph_postgres.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    # # for vectordb test
    # user_input="What are some issues with noise on a ventilation system?"
    # # for maximo test
    # # user_input = "How many work orders were recorded to have priority 1 in december 31, 1998?"
    # result = graph.invoke(
    #         {
    #             'user_input': user_input,
    #             'supervisor_decision': '',
    #             'maximo_payload': '',
    #             'tool_calls': '',
    #             'maximo_agent_response': '',
    #             'vector_db_agent_response': '',
    #             'final_response': '',
    #             'memory_chain': []
    #         }
    #     )
    # print(result)

    # breakpoint()
