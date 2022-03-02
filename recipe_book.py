import flask
from flask_cors import CORS
import re
from dataclasses import dataclass
import sqlite3
from os.path import isfile

RECIPES_DB = 'recipes.db'

@dataclass
class Recipe:
	ingredients: tuple[str, str]
	product: str
	means: str
	was_first: bool

discover_re = re.compile('^You( are the first person to)? discover that (.*) can be used to combine (.*) with (.*) to form (.*)!$')

def parse(text: str, selection: list[str]) -> Recipe:
	if m := discover_re.match(text):
		was_first = (m.group(1) is not None)
		ingredients = (m.group(3), m.group(4))
		if ' with ' in ingredients[0]:
			ingredients = tuple(selection)
		return Recipe(ingredients=ingredients, product=m.group(5), means=m.group(2), was_first=was_first)
	else:
		return None

def add_to_db(recipe: Recipe):
	with sqlite3.connect(RECIPES_DB) as con:
		cur = con.cursor()
		things = (('ingredient1', recipe.ingredients[0]), ('ingredient2', recipe.ingredients[1]), ('product', recipe.product))
		thing_ids = {}
		for (field, name) in things:
			cur.execute('SELECT id FROM Thing WHERE name = ?', (name,))
			if (record := cur.fetchone()) is None:
				cur.execute('INSERT INTO Thing VALUES (NULL, ?)', (name,))
				thing_id = cur.lastrowid
			else:
				thing_id = record[0]
			thing_ids[field] = thing_id
		
		cur.execute('INSERT INTO Recipe VALUES (NULL, ?, ?, ?, ?, ?)', (thing_ids['ingredient1'], thing_ids['ingredient2'], thing_ids['product'], recipe.means, int(recipe.was_first)))
		con.commit()

if __name__ == '__main__':
	if not isfile(RECIPES_DB):
		with open('schema.sql', 'r') as f:
			schema = f.read()
			with sqlite3.connect(RECIPES_DB) as con:
				con.cursor().executescript(schema)

	flask_app = flask.Flask(__name__)
	CORS(flask_app)

	with open('recipes.txt', 'a') as f:
		@flask_app.route('/recipe', methods=['POST'])
		def flask_recipe():
			text = flask.request.json['toast']
			print(text)
			if 'discover' in text:
				print(text, file=f)
				f.flush()
				recipe = parse(text, selection=flask.request.json['selected'])
				print(recipe)
				add_to_db(recipe)
			return 'ok'
		
		@flask_app.route('/recipe/<product>')
		def flask_recipe_for(product):
			with sqlite3.connect(RECIPES_DB) as con:
				cur = con.cursor()
				query = '''
					SELECT ti1.name, ti2.name, tp.name, Recipe.means, Recipe.was_first
					FROM Thing ti1, Thing ti2, Thing tp, Recipe
					WHERE ingredient1 = ti1.id AND ingredient2 = ti2.id AND product = tp.id
					AND UPPER(tp.name) LIKE UPPER(?)||"%"
					ORDER BY tp.name
				'''
				recipe_list = []
				for (i1, i2, product, means, was_first) in cur.execute(query, (product,)):
					json = {'ingredients':[i1, i2], 'product':product, 'means':means, 'was_first':bool(was_first)}
					recipe_list.append(json)
				return {'recipes':recipe_list}

		flask_app.run(port=8765)
