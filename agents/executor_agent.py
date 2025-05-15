from prompt_reference.executor_agent_prompts import executor_prompt, sql_query_prompt
from tools.postgres_agent_tools import PostGresAgentTools
from tools.vector_db_tools import vectorDbAgentTools

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from config import Config


class ExecutorAgent(BaseAgent):
    def __init__(self, name="executor_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.executor_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            PostGresAgentTools.run_query,
            vectorDbAgentTools.similarity_search,
            PostGresAgentTools.generate_sql_query
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # define the system message for the sql query generation agent.
        self.sql_generator_params = Config.sql_generator_params
        self.sql_generator = get_llm(self.sql_generator_params)


    def handle_input(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = executor_prompt.format(state=state)
        message = [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"{state['user_input']}")
        ]
        # call the llm with the message
        agent_response = self.llm_with_tools.invoke(message)

        # update the state with the agent response
        if hasattr(agent_response, 'tool_calls'):
            try:
                state['tool_calls'] = agent_response.tool_calls[0]['name']
            except IndexError:
                pass

        return state
    

    def use_tools(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
        print(f"Calling: {selected_tool}")
        # invoke the tools and udpate the states depending on the tool use.
        if selected_tool == "query_data":
            # set the input parameters or arguments for the tool.
            tool_input = {
                "query": state['postgres_query'],
                "params": None
            }

            # invoke the tool and get the result.
            postgres_agent_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['postgres_agent_response'] = postgres_agent_response
            state['memory_chain'].append({
                'postgres_agent_response': state['postgres_agent_response']
            })

        elif selected_tool == "similarity_search":
            # set the input parameters or arguments for the tool.
            tool_input = {
                "query": state['user_input'],
                "k": 3 # state['top searches']
            }

            # invoke the tool and get the result.
            vector_db_agent_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['vector_db_agent_response'] = vector_db_agent_response
            state['memory_chain'].append({
                'vector_db_agent_response': state['vector_db_agent_response']
            })

        elif selected_tool == "generate_sql_query":

            system_prompt = sql_query_prompt.format(user_input=state['user_input'])

            system_prompt = SystemMessage(
                content=system_prompt
            )
            # set the input parameters or arguments for the tool.
            tool_input = {
                "user_input": state['user_input'],
                "system_prompt": system_prompt,
                "llm": self.sql_generator
            }
            
            # invoke the tool and get the result.
            try:
                sql_query = self.tools_dict[selected_tool].invoke(tool_input)

                # update the state with the tool result.
                state['postgres_query'] = sql_query
                state['memory_chain'].append({
                    'postgres_query': state['postgres_query']
                })
            except:
                state['agent_tool_retries'] += 1
                pass

        return state
    
    @staticmethod
    def router(state: AgentState):
        """
        The router function to route the agent to the next step.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """
        # check if the user input is classified as a SQL query or a vector db search.
        if state['agent_tool_retries'] > state['agent_max_tool_retries']:
            # if the agent has retried the tool use more than the max retries, then return the state.
            return END
        elif len(state['postgres_agent_response']) < 1 and len(state['vector_db_agent_response']) < 1:
            return "executor_tools"
        else:
            return "executor"