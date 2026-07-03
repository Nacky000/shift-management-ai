from AI.ai_parser import parse_message
from AI.dispatcher import dispatch_tasks

text = "2026-06-10 18:00-22:00"

data = parse_message(text)
print("PARSE:", data)

result = dispatch_tasks(data)
print("RESULT:", result)