import json, base64

with open('contest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for user_id, encoded in data.items():
    raw = base64.b64decode(encoded).decode('utf-8')
    name, surname, answer = raw.split('|')
    print(f"Участник {name} {surname}: {answer} ключей")