import uuid
from typing import TypedDict
from langgraph.graph import StateGraph, END


class RecipeValidationState(TypedDict):
    recipe_name: str
    recipe_id: str
    ai_suggestion: str
    taste_score: float
    appearance_score: float
    difficulty_score: float
    feedback_text: str
    overall_score: float
    neo4j_updated: bool
    validated_at: str


def fetch_recipe(state: RecipeValidationState) -> dict:
    recipe_name = state["recipe_name"]
    recipe_id = state.get("recipe_id") or str(uuid.uuid4())[:8]
    return {
        "recipe_id": recipe_id,
        "ai_suggestion": f"「{recipe_name}」を作ってみましょう！新鮮なクレソンの風味を活かした一品です。",
    }


def suggest_cooking(state: RecipeValidationState) -> dict:
    suggestion = state["ai_suggestion"]
    print(f"[suggest_cooking] {suggestion}")
    return {}


def await_evaluation(state: RecipeValidationState) -> dict:
    print("[await_evaluation] WebUIからの評価入力を待機中...")
    return {}


def calculate_score(state: RecipeValidationState) -> dict:
    taste = state.get("taste_score", 0.0)
    appearance = state.get("appearance_score", 0.0)
    difficulty = state.get("difficulty_score", 0.0)
    overall = round(taste * 0.6 + appearance * 0.2 + difficulty * 0.2, 2)
    print(f"[calculate_score] overall={overall} (taste={taste} appearance={appearance} difficulty={difficulty})")
    return {"overall_score": overall}


def update_neo4j(state: RecipeValidationState) -> dict:
    from memory.memory_agent import MemoryAgent
    agent = MemoryAgent()
    if not agent._use_fallback:
        agent.save_validation(state["recipe_name"], state)
        agent.close()
        return {"neo4j_updated": True}
    else:
        print("[update_neo4j] AuraDB未接続、スキップ")
        agent.close()
        return {"neo4j_updated": False}


def build_validation_graph():
    graph = StateGraph(RecipeValidationState)
    graph.add_node("fetch_recipe", fetch_recipe)
    graph.add_node("suggest_cooking", suggest_cooking)
    graph.add_node("await_evaluation", await_evaluation)
    graph.add_node("calculate_score", calculate_score)
    graph.add_node("update_neo4j", update_neo4j)

    graph.set_entry_point("fetch_recipe")
    graph.add_edge("fetch_recipe", "suggest_cooking")
    graph.add_edge("suggest_cooking", "await_evaluation")
    graph.add_edge("await_evaluation", "calculate_score")
    graph.add_edge("calculate_score", "update_neo4j")
    graph.add_edge("update_neo4j", END)

    return graph.compile()
