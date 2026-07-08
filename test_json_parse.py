import json
import re

def parse_llm_json(text: str):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())

print(parse_llm_json("```json\n{\"options\": []}\n```"))
