from prompt_reference.reportgenerate_agent_prompts import reportgenerate_prompt
from tools.report_generator_tools import generate_reports, generate_query, run_query 

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from config import Config
from tools.postgres_agent_tools import PostGresAgentTools
from prompt_reference.general_agent_prompts import general_prompt, sql_query_prompt


class ReportGeneratorAgent(BaseAgent):
    def __init__(self, name="report_generator_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.report_generator_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            generate_reports,
            PostGresAgentTools.generate_query,
            PostGresAgentTools.run_query,
            
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)        
        # define the agent for output handling.
        self.response_agent = Config.general_agent_response_params
        self.response_agent = get_llm(self.response_agent)
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
    def handle_output(self, state: AgentState):
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
        agent_response = self.response_agent.invoke(message)

        # update the state with the agent response
        state['final_response'] = agent_response.content
        state['memory_chain'].append({
            'final_response': state['final_response']
        })
        return state

    def use_tools(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
        print(f"Calling: {selected_tool}")
        # invoke the tools and udpate the states depending on the tool use.
        if selected_tool == "generate_reports":
            # set the input parameters or arguments for the tool.
            tool_input = {
                "query": state['postgres_query']
            }

            # invoke the tool and get the result.
            report_generator_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['report_generator_response'] = report_generator_response
            state['memory_chain'].append({
                'report_generator_response': state['report_generator_response']
            })

        return state
    def generate_sql_query(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
        print(f"Calling: {selected_tool}")

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
    
    def run_sql_query(self, state: AgentState):
        # check the tool to use.
        print(f"Running SQL Query: {state['postgres_query']}")
        selected_tool = 'run_query'

        # set the input parameters or arguments for the tool.
        tool_input = {
            "query": state['postgres_query'],
            "params": None
        }

        try:
            # invoke the tool and get the result.
            postgres_agent_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['postgres_agent_response'] = postgres_agent_response
            state['memory_chain'].append({
                'postgres_agent_response': state['postgres_agent_response']
            })
        except:
            state['agent_tool_retries'] += 1
            pass

        return state