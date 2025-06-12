# interaction.py

from agents.agent_langchain import LangchainAgent


class A2AInteraction:
    def __init__(self):
        self.langchain_agent = LangchainAgent()
        self.history = []

    def ask(self, question: str) -> str:
        self.history.append({"role": "user", "content": question})
        
        print("\n🤖 Запрашиваю ответ через Langchain-агента...\n")
        answer = self.langchain_agent.run(question)
        
        self.history.append({"role": "agent", "content": answer})
        return answer
