from prompt_reference.reportgenerate_agent_prompts import reportgenerate_prompt
from tools.report_generator_tools import generate_reports

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from config import Config


class ReportGeneratorAgent(BaseAgent):
    def __init__(self, name="report_generator_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.report_generator_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            generate_reports,
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
        system_msg = reportgenerate_prompt.format(state=state)
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
                state['query'] = agent_response.tool_calls[0]['args']['query']
            except IndexError:
                pass

        return state
    

    def use_tools(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
        print(f"Calling: {selected_tool}")
        # invoke the tools and udpate the states depending on the tool use.
        if selected_tool == "generate_reports":
            # set the input parameters or arguments for the tool.
            tool_input = {
                "query": state['query']
            }

            # invoke the tool and get the result.
            report_generator_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['report_generator_response'] = report_generator_response
            state['memory_chain'].append({
                'report_generator_response': state['report_generator_response']
            })

        return state
