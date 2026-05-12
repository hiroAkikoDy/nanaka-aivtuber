import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def load_personas():
    """personas.yaml を読み込む"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "personas.yaml"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_settings():
    """settings.yaml を読み込む"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "settings.yaml"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class PersonaAgent:
    """
    個別のペルソナエージェント
    personas.yamlで定義されたキャラクターごとに応答を生成する
    """

    def __init__(self, persona_name: str):
        """
        Args:
            persona_name: "nanaka" または "ryou"
        """
        load_dotenv()

        # ペルソナ設定を読み込み
        personas = load_personas()
        if persona_name not in personas["personas"]:
            raise ValueError(f"Unknown persona: {persona_name}")

        self.persona_config = personas["personas"][persona_name]
        self.persona_name = persona_name
        self.name = self.persona_config["name"]
        self.role = self.persona_config["role"]
        self.speaker_id = self.persona_config["speaker_id"]
        self.system_prompt = self.persona_config["system_prompt"]

        # LLM設定を読み込み
        settings = load_settings()
        llm = settings["llm"]

        # ChatOpenAI を初期化
        self.llm = ChatOpenAI(
            model=llm["model"],
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=llm.get("base_url"),
        )

    def respond(self, context: str, emotion: str = "普通") -> str:
        """
        コンテキストを元に応答を生成

        Args:
            context: 視聴者コメント + これまでの会話履歴
            emotion: 感情状態（既存のEmotionAgentと連携）

        Returns:
            str: このペルソナの応答テキスト
        """
        # システムメッセージと会話コンテキストを構築
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"【現在の感情】{emotion}\n\n【会話の流れ】\n{context}\n\nあなた（{self.name}）の応答を1文で簡潔に生成してください。")
        ]

        # LLMで応答を生成
        response = self.llm.invoke(messages)
        return response.content

    def get_speaker_id(self) -> int:
        """VOICEVOX speaker_id を返す"""
        return self.speaker_id


if __name__ == "__main__":
    # テスト用コード
    nanaka = PersonaAgent("nanaka")
    ryou = PersonaAgent("ryou")

    print(f"[{nanaka.name}] speaker_id={nanaka.get_speaker_id()}")
    print(f"[{ryou.name}] speaker_id={ryou.get_speaker_id()}")

    context = "視聴者: クレソンってどんな味なの？"
    nanaka_response = nanaka.respond(context, emotion="嬉しい")
    print(f"\n[{nanaka.name}] {nanaka_response}")

    context += f"\n{nanaka.name}: {nanaka_response}"
    ryou_response = ryou.respond(context, emotion="嬉しい")
    print(f"[{ryou.name}] {ryou_response}")
