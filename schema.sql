CREATE TABLE Thing(
	id      INTEGER PRIMARY KEY AUTOINCREMENT,
	name    TEXT UNIQUE NOT NULL
);

CREATE TABLE Recipe(
	id          INTEGER PRIMARY KEY AUTOINCREMENT,
	ingredient1 INTEGER NOT NULL,
	ingredient2 INTEGER NOT NULL,
	product     INTEGER NOT NULL,
	means       TEXT,
	was_first   INTEGER,
	FOREIGN KEY(ingredient1) REFERENCES Thing(id),
	FOREIGN KEY(ingredient2) REFERENCES Thing(id),
	FOREIGN KEY(product) REFERENCES Thing(id),
	UNIQUE(ingredient1, ingredient2)
);
