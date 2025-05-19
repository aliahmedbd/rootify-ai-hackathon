import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import necessary modules and functions from langgraph
from langgraph import Graph, Node, add_edge


def build_report_generator_graph():
    # Define the nodes
    vector_db_agent = Node("vector_db_agent")
    generate_sql_query = Node("generate_sql_query")
    run_query = Node("run_query")
    generate_report = Node("generate_report")

    # Create the graph
    report_generator_agent_graph = Graph("report_generator_agent_graph")

    # Add nodes to the graph
    report_generator_agent_graph.add_node(vector_db_agent)
    report_generator_agent_graph.add_node(generate_sql_query)
    report_generator_agent_graph.add_node(run_query)
    report_generator_agent_graph.add_node(generate_report)

    # Link the nodes with add_edge()
    add_edge(report_generator_agent_graph, vector_db_agent, generate_sql_query)
    add_edge(report_generator_agent_graph, generate_sql_query, run_query)
    add_edge(report_generator_agent_graph, run_query, generate_report)

    # Save the graph to the graphs/ folder
    report_generator_agent_graph.save("graphs/report_generator_agent_graph")
