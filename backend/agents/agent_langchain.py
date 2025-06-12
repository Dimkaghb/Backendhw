# agents/agent_langchain.py

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain import hub
from agents.agent_llamaindex import LlamaIndexAgent


class LangchainAgent:
    def __init__(self):
        # Create an instance of the LlamaIndex agent
        self.llama_agent = LlamaIndexAgent()

        # Create LangChain tool that calls query_knowledge
        tools = [
            Tool(
                name="LlamaIndex_Knowledge_Search",
                func=self.llama_agent.query_knowledge,
                description="Useful when you need to find information in documents about people, company information, or any stored knowledge",
            )
        ]

        # Get the react prompt from LangChain hub
        try:
            prompt = hub.pull("hwchase17/react")
        except:
            # Fallback prompt if hub is not available
            from langchain.prompts import PromptTemplate
            prompt = PromptTemplate.from_template("""
            Answer the following questions as best you can. You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}
            Thought:{agent_scratchpad}
            """)

        # Create LangChain agent with newer API
        llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")
        agent = create_react_agent(llm, tools, prompt)
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def run(self, question: str) -> str:
        try:
            result = self.agent_executor.invoke({"input": question})
            return result.get("output", "I couldn't find an answer to your question.")
        except Exception as e:
            print(f"Error in LangChain agent: {e}")
            # Fallback to direct LlamaIndex query
            return self.llama_agent.query_knowledge(question)
