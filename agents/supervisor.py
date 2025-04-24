"""
A set of custom Agents to be implemented here. They inheret from the BaseAgent.
"""

# repo specific modules and libraries
from config import Config
from agents.base_agent import BaseAgent, AgentState
from prompt_reference.supervisor_prompt import SupervisorPrompts
from utils.handle_configs import get_llm
# third party libraries
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END



class SupervisorAgent(BaseAgent):
    def __init__(self, name:str="supervisor"):
        """A supervisor agent, which is used to route or delgate user query to other agents best able to assist with the query.
        :state: pydantic.BaseModel: The state that the agent will have access to for reading and updating. It is 
        """

        super().__init__(name)

        # instantiate the parameters for supervisor agent. 
        self.supervisor_params = Config.supervisor_params
        self.llm = get_llm(self.supervisor_params)
    

    def handle_input(self, state: AgentState):

        """To be implemented"""
        # instantiate the prompt with the state.
        user_input = state['user_input']

        # combine responses, will return a string if child agent responses are available. Otherwise, will concat empty strings.
        agent_response = str(state['maximo_agent_response']) + '\n' + str(state['vector_db_agent_response'])
        
        # to ensure a supervisor has already routed to an agent and keep track of that.
        if state['supervisor_decision'] != '':
            agents_consulted = 'yes'
        else:
            agents_consulted = 'no'

        system_message = SupervisorPrompts.supervisor_prompt.format(
            user_input=user_input,
            agent_response=agent_response,
            agents_consulted=agents_consulted
        )

        message = [
            SystemMessage(content=system_message),
            HumanMessage(content=state['user_input'])
        ]

        # call the llm with the message.
        supervisor_response = self.llm.invoke(message).content

        # update the state with the supervisor response.
        state['memory_chain'].append({'supervisor_response': supervisor_response})

        if supervisor_response.lower().replace(" ", "") in ['maximo', 'vector_db', 'unknown']:
            state['supervisor_decision'] = supervisor_response
        else:
            state['final_response'] = supervisor_response

        return state

        
    @staticmethod
    def router(state: AgentState):
        """Routing based on supervisor's response"""

        decision = state['supervisor_decision']
 
        if len(state['final_response']) > 1:
            return END
        if "maximo" in decision:
            return "maximo_agent"
        elif "vector_db" in decision:
            return "vector_db_agent"
        elif 'unknown' in decision:
            return "supervisor"
        