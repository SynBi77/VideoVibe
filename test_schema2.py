from google.genai import types

schema_dict = {
    "type": "OBJECT",
    "properties": {
        "options": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "description": {"type": "STRING"},
                    "lyria_prompt": {"type": "STRING"}
                },
                "required": ["title", "description", "lyria_prompt"]
            }
        }
    },
    "required": ["options"]
}

schema = types.Schema(**schema_dict)
print("Schema dict accepted!")
