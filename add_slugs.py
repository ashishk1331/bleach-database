import json
from slugify import slugify
from collections import defaultdict

with open('data/log.json', 'r', encoding="utf-8") as file:
	data = json.loads(file.read())

cache = defaultdict(lambda: 0)
for ch in data.keys():
	with open(f'data/{ch}.json', 'r', encoding="utf-8") as file:
		characters = json.loads(file.read())
		for index, each in enumerate(characters):
			name = slugify(each['id'])
			slug = f'{name}-{cache[name]}' if name in cache else name
			characters[index]['slug'] = slug

			cache[name] += 1

	with open(f'data/{ch}.json', 'w', encoding="utf-8") as file:
		file.write(json.dumps(characters, indent=4))