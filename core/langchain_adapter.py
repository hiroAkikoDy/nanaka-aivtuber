import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate


def load_settings():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class LangChainAdapter:
    SAVE_PREVIOUS_CHAT_NUM = 5

    def __init__(self):
        load_dotenv()
        settings = load_settings()
        llm = settings["llm"]
        self.model = llm["model"]
        self.system_prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "system_prompt_template.txt",
        )
        with open(self.system_prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()
        self.chat_log = []
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=llm.get("base_url"),
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt_template), ("placeholder", "{chat_history}"), ("human", "{input}")]
        )
        self.chain = self.prompt_template | self.llm

    def create_chat(self, question: str, emotion: str = "普通", memory: str = "") -> str:
        chat_history = self._build_chat_history()
        response = self.chain.invoke(
            {"emotion": emotion, "memory": memory, "chat_history": chat_history, "input": question}
        )
        answer = response.content
        self._update_messages(question, answer)
        return answer

    def _build_chat_history(self):
        history = []
        for chat in self.chat_log:
            history.append(HumanMessage(content=chat["question"]))
            history.append(AIMessage(content=chat["answer"]))
        return history

    def _update_messages(self, question, answer):
        self.chat_log.append({"question": question, "answer": answer})
        if len(self.chat_log) > self.SAVE_PREVIOUS_CHAT_NUM:
            self.chat_log.pop(0)
        return True


if __name__ == "__main__":
    adapter = LangChainAdapter()
    while True:
        question = input("質問を入力してください:")
        response_text = adapter.create_chat(question)
        print(response_text)
        print(adapter.chat_log)
