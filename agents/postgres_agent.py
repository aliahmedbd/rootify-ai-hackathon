from prompt_reference.postgres_agent_prompts import postgres_prompt
from tools.postgres_agent_tools import PostGresAgentTools

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from config import Config


class PostGresAgent(BaseAgent):
    def __init__(self, name="postgres_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.postgres_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            PostGresAgentTools.query_data,
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)        


    def handle_input(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = postgres_prompt.format(state=state)
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
    

    def use_postgres_tools(self, state: AgentState):
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

        return state