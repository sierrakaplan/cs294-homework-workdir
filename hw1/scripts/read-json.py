import json

def remove_properties(schema):
	# print(schema)
	if isinstance(schema, dict):
		if "properties" in schema:
			for prop in schema["properties"]:
				schema[prop] = schema["properties"][prop]
			del schema["properties"]
		for key in schema:
			if isinstance(schema[key], list):
				for item in schema[key]:
					remove_properties(item)
			else:
				remove_properties(schema[key])

def main():
	with open('./source-data/books/books-goodreads-reviews.json') as json_file:
		data = json.load(json_file)
		for i in range(len(data)):
			schema = data[i]
			remove_properties(schema) 
		with open('./source-data/books/sample', 'w') as f:
			json.dump(data, f, indent=2, ensure_ascii=False)



if __name__ == '__main__':
    main()