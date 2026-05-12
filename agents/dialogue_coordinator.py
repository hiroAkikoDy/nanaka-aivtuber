import os
import yaml
from agents.persona_agent import PersonaAgent


def load_settings():
    """settings.yaml を読み込む"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "settings.yaml"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class DialogueCoordinator:
    """
    複数ペルソナの会話を調整するコーディネーター
    視聴者コメントを受け取り、ナナカとリョウの対話を生成する
    """

    def __init__(self):
        """
        DialogueCoordinator を初期化
        """
        self.nanaka = PersonaAgent("nanaka")
        self.ryou = PersonaAgent("ryou")

        # settings.yaml から設定を読み込み
        settings = load_settings()
        self.turn_limit = settings["multi_persona"]["turn_limit"]

    def coordinate_dialogue(self, viewer_comment: str, emotion: str) -> list[dict]:
        """
        視聴者コメントを元に、2人のAIが会話を展開

        Args:
            viewer_comment: 視聴者のコメント
            emotion: EmotionAgentで分析された感情

        Returns:
            list[dict]: [
                {"persona": "nanaka", "text": "...", "speaker_id": 46},
                {"persona": "ryou", "text": "...", "speaker_id": 3},
                ...
            ]
        """
        dialogue = []
        context = f"視聴者: {viewer_comment}\n"

        # ターン1: ナナカが最初に応答
        nanaka_response = self.nanaka.respond(context, emotion)
        dialogue.append({
            "persona": "nanaka",
            "text": nanaka_response,
            "speaker_id": self.nanaka.get_speaker_id()
        })
        context += f"{self.nanaka.name}: {nanaka_response}\n"

        # ターン2〜N: リョウとナナカが交互に会話
        for turn in range(1, self.turn_limit):
            if turn % 2 == 1:  # リョウのターン（奇数ターン）
                ryou_response = self.ryou.respond(context, emotion)
                dialogue.append({
                    "persona": "ryou",
                    "text": ryou_response,
                    "speaker_id": self.ryou.get_speaker_id()
                })
                context += f"{self.ryou.name}: {ryou_response}\n"
            else:  # ナナカのターン（偶数ターン）
                nanaka_response = self.nanaka.respond(context, emotion)
                dialogue.append({
                    "persona": "nanaka",
                    "text": nanaka_response,
                    "speaker_id": self.nanaka.get_speaker_id()
                })
                context += f"{self.nanaka.name}: {nanaka_response}\n"

        return dialogue


if __name__ == "__main__":
    # テスト用コード
    coordinator = DialogueCoordinator()

    test_comment = "クレソンってどんな味なの？"
    print(f"視聴者: {test_comment}\n")

    dialogue = coordinator.coordinate_dialogue(test_comment, emotion="嬉しい")

    for i, turn in enumerate(dialogue, 1):
        print(f"[ターン{i}] [{turn['persona']}] {turn['text']} (speaker_id={turn['speaker_id']})")
