import os
import yaml
from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END


def load_settings():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class EmotionState(TypedDict):
    comment: str
    emotion: str
    speed: float
    pitch: float


VALID_EMOTIONS = {"嬉しい", "普通", "ワクワク", "驚き", "悲しい"}


def adjust_happy(state: EmotionState) -> dict:
    return {"speed": 1.2, "pitch": 0.1}


def adjust_excited(state: EmotionState) -> dict:
    return {"speed": 1.3, "pitch": 0.15}


def adjust_surprised(state: EmotionState) -> dict:
    return {"speed": 1.1, "pitch": 0.2}


def adjust_sad(state: EmotionState) -> dict:
    return {"speed": 0.9, "pitch": -0.05}


def adjust_normal(state: EmotionState) -> dict:
    return {"speed": 1.0, "pitch": 0.0}


class EmotionAgent:
    def __init__(self):
        load_dotenv()
        settings = load_settings()
        llm = settings["llm"]
        self.llm = ChatOpenAI(
            model=llm["model"],
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=llm.get("base_url"),
        )
        graph = StateGraph(EmotionState)
        graph.add_node("analyze_emotion", self._analyze_emotion)
        graph.add_node("adjust_happy", adjust_happy)
        graph.add_node("adjust_excited", adjust_excited)
        graph.add_node("adjust_surprised", adjust_surprised)
        graph.add_node("adjust_sad", adjust_sad)
        graph.add_node("adjust_normal", adjust_normal)
        graph.set_entry_point("analyze_emotion")
        graph.add_conditional_edges(
            "analyze_emotion",
            lambda state: state["emotion"],
            {
                "嬉しい": "adjust_happy",
                "ワクワク": "adjust_excited",
                "驚き": "adjust_surprised",
                "悲しい": "adjust_sad",
                "普通": "adjust_normal",
            },
        )
        graph.add_edge("adjust_happy", END)
        graph.add_edge("adjust_excited", END)
        graph.add_edge("adjust_surprised", END)
        graph.add_edge("adjust_sad", END)
        graph.add_edge("adjust_normal", END)
        self.app = graph.compile()

    def _analyze_emotion(self, state: EmotionState) -> dict:
        prompt = (
            "あなたは感情分析AIです。以下のコメントから視聴者の感情を読み取り、ナナカが感じるべき感情を1つ選んでください。\n\n"
            "判定基準:\n"
            "- 嬉しい: 視聴者からの称賛、感谢、褒め言葉、好意的な反応\n"
            "- ワクワク: 視聴者が知識を求めている、好奇心、新しいことへの興味\n"
            "- 驚き: 視聴者が意外だと感じている、「えっ」「！？」「信じられない」等の表現\n"
            "- 悲しい: 視聴者の心配、同情、ネガティブな出来事への言及\n"
            "- 普通: 単なる事実確認、短い挨拶のみ、上記のどれにも当てはまらない\n\n"
            "感情ラベルのみを1つ出力してください。他の文字は一切含めないでください。\n"
            "選択肢: 嬉しい / 普通 / ワクワク / 驚き / 悲しい\n\n"
            f"コメント: {state['comment']}"
        )
        response = self.llm.invoke(prompt)
        emotion = response.content.strip()
        if emotion not in VALID_EMOTIONS:
            emotion = "普通"
        return {"emotion": emotion}

    def analyze(self, comment: str) -> dict:
        result = self.app.invoke({
            "comment": comment,
            "emotion": "",
            "speed": 1.0,
            "pitch": 0.0,
        })
        return {
            "emotion": result["emotion"],
            "speed": result["speed"],
            "pitch": result["pitch"],
        }


if __name__ == "__main__":
    agent = EmotionAgent()
    test_comments = [
        "こんにちは！ナナカちゃん可愛い！",
        "クレソンの育て方を教えて！",
        "えっ、熊本でクレソン育ってるの！？",
        "ナナカさん、好きな食べ物は何？",
        "農家って大変そう…応援してるよ",
    ]
    for c in test_comments:
        result = agent.analyze(c)
        print(f"コメント: {c}")
        print(f"  → 感情: {result['emotion']}, speed={result['speed']}, pitch={result['pitch']}")
