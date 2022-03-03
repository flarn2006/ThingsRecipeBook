#!/usr/bin/python3
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

def add_thing_id(db: sqlite3.Connection, thing: str, gameid: None) -> int:
	cur = db.cursor()

	cur.execute('SELECT id FROM Thing WHERE name = ?', (thing,))
	if (record := cur.fetchone()) is None:
		cur.execute('INSERT INTO Thing VALUES (NULL, ?)', (thing,))
		db.commit()
		thing_id = cur.lastrowid
	else:
		thing_id = record[0]
	
	if gameid is not None:
		cur.execute('SELECT id FROM Game WHERE gameid = ?', (gameid,))
		if (record := cur.fetchone()) is None:
			cur.execute('INSERT INTO Game VALUES (NULL, ?)', (gameid,))
			gameid_id = cur.lastrowid
		else:
			gameid_id = record[0]

		try:
			cur.execute('INSERT INTO ThingInGame VALUES (NULL, ?, ?)', (thing_id, gameid_id))
			db.commit()
		except sqlite3.IntegrityError:
			pass

	return thing_id

def add_to_db(recipe: Recipe, gameid: str=None):
	with sqlite3.connect(RECIPES_DB) as con:
		cur = con.cursor()
		things = (('ingredient1', recipe.ingredients[0]), ('ingredient2', recipe.ingredients[1]), ('product', recipe.product))
		thing_ids = {}
		for (field, name) in things:
			thing_ids[field] = add_thing_id(con, name, gameid)
		
		try:
			cur.execute('INSERT INTO Recipe VALUES (NULL, ?, ?, ?, ?, ?)', (thing_ids['ingredient1'], thing_ids['ingredient2'], thing_ids['product'], recipe.means, int(recipe.was_first)))
		except sqlite3.IntegrityError:
			print('Looks like this recipe is already in the database.')

if __name__ == '__main__':
	if not isfile(RECIPES_DB):
		with open('schema.sql', 'r') as f:
			schema = f.read()
			with sqlite3.connect(RECIPES_DB) as con:
				con.cursor().executescript(schema)

	flask_app = flask.Flask(__name__)
	CORS(flask_app, resources={'*': {'origins': 'https://lab.latitude.io/*'}})

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
				try:
					add_to_db(recipe, flask.request.json['gameid'])
				except KeyError:
					add_to_db(recipe)
			return 'ok'
		
		@flask_app.route('/recipe/<product>')
		def flask_recipe_for(product):
			with sqlite3.connect(RECIPES_DB) as con:
				cur = con.cursor()
				query = '''
					SELECT ti1.name, ti2.name, tp.name, Recipe.means, Recipe.was_first, ti1.id, ti2.id, tp.id
					FROM Thing ti1, Thing ti2, Thing tp, Recipe
					WHERE ingredient1 = ti1.id AND ingredient2 = ti2.id AND product = tp.id
					AND UPPER(tp.name) LIKE UPPER(?)||"%"
					ORDER BY UPPER(tp.name)
				'''
				recipe_list = []
				for (i1, i2, product, means, was_first, i1_id, i2_id, product_id) in cur.execute(query, (product,)):
					json = {'ingredients':[{'name':i1, 'id':i1_id}, {'name':i2, 'id':i2_id}], 'product':{'name':product, 'id':product_id}, 'means':means, 'was_first':bool(was_first)}
					recipe_list.append(json)
				return {'recipes':recipe_list}

		@flask_app.route('/all_recipes')
		def flask_all_recipes():
			return flask_recipe_for('')

		@flask_app.route('/things_in_game', methods=['POST'])
		def flask_things_in_game():
			with sqlite3.connect(RECIPES_DB) as con:
				cur = con.cursor()
				things = flask.request.json['things']
				for thing in things:
					add_thing_id(con, thing, flask.request.json['gameid'])
			return 'ok'

		@flask_app.route('/thing/<thing_id>')
		def flask_thing(thing_id):
			json = {}
			with sqlite3.connect(RECIPES_DB) as con:
				cur = con.cursor()
				cur.execute('SELECT name FROM Thing WHERE id = ?', (thing_id,))
				if (record := cur.fetchone()) is None:
					flask.abort(404)
				else:
					json['name'] = record[0]
					json['games'] = list(cur.execute('SELECT Game.gameid FROM ThingInGame INNER JOIN Game ON ThingInGame.game = Game.id WHERE thing = ?', (thing_id,)))
					return json

		@flask_app.route('/')
		def flask_index():
			with open('static/recipe_book.html', 'r') as f:
				return f.read()

		flask_app.run(port=8765)
