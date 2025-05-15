from langgraph.graph import StateGraph, END

from agents.base_agent import AgentState
from agents.postgres_agent import PostGresAgent
from agents.supervisor import  SupervisorAgent
from agents.vector_db_agent import VectorDbAgent
from agents.executor_agent import ExecutorAgent


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


def build_executor_graph():
    graph = StateGraph(AgentState)

    executor_agent = ExecutorAgent()

    # Add agent to the graph
    graph.add_node(executor_agent.name, executor_agent.handle_input)
    graph.add_node("executor_tools", executor_agent.use_tools)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_edge(executor_agent.name, "executor_tools")
    graph.add_edge("executor_tools", executor_agent.name)

    graph.set_entry_point(executor_agent.name)
    graph.set_finish_point(executor_agent.name)

    return graph.compile()