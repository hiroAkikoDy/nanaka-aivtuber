import os
import yaml
from dotenv import load_dotenv
from openai import OpenAI


def load_settings():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class OpenAIAdapter:
    SAVE_PREVIOUS_CHAT_NUM = 5

    def __init__(self):
        load_dotenv()
        settings = load_settings()
        llm = settings["llm"]
        self.model = llm["model"]
        self.system_prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), llm["system_prompt_file"])
        with open(self.system_prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()
        self.chat_log = []
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=llm.get("base_url"),
        )

    def _create_message(self, role, message):
        return {"role": role, "content": message}

    def create_chat(self, question):
        messages = self._get_messages()
        user_message = self._create_message("user", question)
        messages.append(user_message)

        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        answer = res.choices[0].message.content
        self._update_messages(question, answer)
        return answer

    def _get_messages(self):
        system_message = self._create_message("system", self.system_prompt)
        messages = [system_message]
        for chat in self.chat_log:
            messages.append(self._create_message("user", chat["question"]))
            messages.append(self._create_message("assistant", chat["answer"]))
        return messages

    def _update_messages(self, question, answer):
        self.chat_log.append({"question": question, "answer": answer})
        if len(self.chat_log) > self.SAVE_PREVIOUS_CHAT_NUM:
            self.chat_log.pop(0)
        return True


if __name__ == "__main__":
    adapter = OpenAIAdapter()
    while True:
        question = input("質問を入力してください:")
        response_text = adapter.create_chat(question)
        print(response_text)
        print(adapter.chat_log)
