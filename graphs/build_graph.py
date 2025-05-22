from langgraph.graph import StateGraph, END

from agents.base_agent import AgentState
from agents.postgres_agent import PostGresAgent
from agents.supervisor import  SupervisorAgent
from agents.vector_db_agent import VectorDbAgent
from agents.general_agent import GeneralAgent


# ----- Build LangGraph -----
def build_supervisor_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    post_gres_agent = PostGresAgent()
    vector_db_agent = VectorDbAgent()

    # Add agent to the graph
    graph.add_node(supervisor.name, supervisor.handle_input)
    graph.add_node("postgres_agent", post_gres_agent.handle_input)
    graph.add_node(vector_db_agent.name, vector_db_agent.handle_input)
    # Add tools nodes
    graph.add_node("postgres_tools", post_gres_agent.use_maximo_tools)
    graph.add_node("vector_db_tools", vector_db_agent.use_vector_db_tools)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        supervisor.name,
        supervisor.router, 
        {
            post_gres_agent.name: "postgres_agent", 
            vector_db_agent.name: vector_db_agent.name, 
            supervisor.name: supervisor.name, 
            END: END
        }
    )
    graph.add_conditional_edges(
        "postgres_agent", 
        post_gres_agent.router,
        {"maximo_tools": "postgres_tools", supervisor.name: supervisor.name}
    )
    graph.add_conditional_edges(
        vector_db_agent.name,
        vector_db_agent.router,
        {"vector_db_tools": "vector_db_tools", supervisor.name: supervisor.name}
    )
    graph.add_edge("postgres_tools", "postgres_agent")
    graph.add_edge("vector_db_tools", vector_db_agent.name)


    graph.set_entry_point(supervisor.name)
    graph.set_finish_point(supervisor.name)

    return graph.compile()


def build_general_agent_graph():
    graph = StateGraph(AgentState)

    agent = GeneralAgent()

    # Add agent to the graph
    graph.add_node(agent.name, agent.handle_input)
    graph.add_node("generate_sql_query", agent.generate_sql_query)
    graph.add_node("vector_search", agent.vector_search)
    graph.add_node("run_query", agent.run_sql_query)
    graph.add_node("handle_response", agent.handle_output)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        agent.name,
        agent.router,
        {
            "generate_sql_query": "generate_sql_query",
            "vector_search": "vector_search",
            "handle_response": "handle_response",
            END: END
        }
    )
    # add edges
    graph.add_edge("generate_sql_query", "run_query")
    graph.add_edge("vector_search", "handle_response")
    graph.add_edge("run_query", "handle_response")
    
    # set entry and finish points
    graph.set_entry_point(agent.name)
    graph.set_finish_point(agent.name)

    return graph.compile()


def build_general_agent_graph_with_report():
    graph = StateGraph(AgentState)

    agent = GeneralAgent()

    # Add nodes to  the graph
    graph.add_node(agent.name, agent.handle_input)
    graph.add_node("generate_sql_query", agent.generate_sql_query)
    graph.add_node("vector_search", agent.vector_search)
    graph.add_node("run_query", agent.run_sql_query)
    graph.add_node("generate_report", agent.generate_report)
    graph.add_node("handle_response", agent.handle_output)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        agent.name,
        agent.router,
        {
            "generate_sql_query": "generate_sql_query",
            "vector_search": "vector_search",
            "generate_report": "generate_sql_query",
            END: END
        }
    )

    # add edges for sub tasks with postgres queries and report generation.
    graph.add_edge("generate_sql_query", "run_query")
    graph.add_conditional_edges(
        "run_query",
        agent.router_2,
        {
            "generate_report": "generate_report",
            "handle_response": "handle_response"
        }
    )

    # add edges for sub tasks with vector search.
    graph.add_edge("vector_search", "handle_response")

    # set entry and finish points
    graph.set_entry_point(agent.name)
    graph.set_finish_point(agent.name)

    return graph.compile()
    
    