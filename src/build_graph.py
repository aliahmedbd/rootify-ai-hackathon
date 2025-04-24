from langgraph.graph import StateGraph, END

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.maximo_agent import MaximoAgent
from agents.vector_db_agent import ChromaAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    maximo_agent = MaximoAgent()
    vector_db_agent = ChromaAgent()

    # Add agent to the graph
    graph.add_node(supervisor.name, supervisor.handle_input)
    graph.add_node("postgres_agent", maximo_agent.handle_input)
    graph.add_node(vector_db_agent.name, vector_db_agent.handle_input)
    # Add tools nodes
    graph.add_node("postgres_tools", maximo_agent.use_maximo_tools)
    graph.add_node("vector_db_tools", vector_db_agent.use_vector_db_tools)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        supervisor.name,
        supervisor.router, 
        {
            maximo_agent.name: "postgres_agent", 
            vector_db_agent.name: vector_db_agent.name, 
            supervisor.name: supervisor.name, 
            END: END
        }
    )
    graph.add_conditional_edges(
        "postgres_agent", 
        maximo_agent.router,
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
