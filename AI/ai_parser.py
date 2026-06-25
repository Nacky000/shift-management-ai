from openai import OpenAI
from AI.prompts import SHIFTBOT_PROMPT
import json

client = OpenAI()

def arse_message(user_text):

    try:
        response = client.responses.create(
            model="gpt-5.5-mini",
            instructions=SHIFTBOT_PROMPT,
            input=user_text
        )

    except Exception:
        return {
            "tasks":[
                {
                    "action": None,
                    "type": "other",
                    "content": user_text
                }
            ]
        }

    try:
        data = json.loads(response.output_text)

    except json.JSONDecodeError:
        data = {
            "tasks":[
                {
                    "action": None,
                    "type": "other",
                    "content": user_text
                }
            ]
        }

    print(response.output_text)

    return data