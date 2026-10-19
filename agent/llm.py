import re
import ollama

MODEL = "qwen2.5-coder:7b"

def ask(system: str, user: str, json_mode: bool = False) -> str:
    resp = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        format="json" if json_mode else None,
        options={"temperature": 0.1},  # faible = réponses stables et reproductibles
    )
    return resp["message"]["content"]

def extract_code(text: str) -> str:
    """Récupère le bloc ```python``` de la réponse du LLM."""
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()