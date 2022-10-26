# -*- coding: utf-8 -*-

from sqlite3 import Row
from sqlite3 import connect as db_connect
from threading import Thread
from time import time

from flask import g

LIND_DB_FILE = "Lind.db"

def get_db(output_type: str = "tuple"):
	# create cursor instance if it doesn't exist yet
	if not (hasattr(g, "db") and hasattr(g, "cursor")):
		g.db = db_connect(LIND_DB_FILE, timeout=20.0)
		g.cursor = g.db.cursor()

	# change output type if needed
	if output_type == "tuple" and g.cursor.row_factory == Row:
		g.cursor.row_factory = None
	elif output_type == "dict" and g.cursor.row_factory == None:
		g.cursor.row_factory = Row

	return g.cursor

def close_db(e=None) -> None:
	if hasattr(g, "db") and hasattr(g, "cursor"):
		g.cursor.close()
		delattr(g, "cursor")
		g.db.commit()
		g.db.close()
		delattr(g, "db")
	return

def setup_db() -> None:
	"""Setup application when starting up

	Returns:
			None
	"""
	cursor = get_db()

	table_creation = """
		CREATE TABLE IF NOT EXISTS linds(
			lind_id VARCHAR(10) PRIMARY KEY,
			url TEXT NOT NULL,
			expiration_time INTEGER(8),
			limit_usage INTEGER,
			access_password BLOB,
			admin_password BLOB
		);
	"""
	cursor.executescript(table_creation)

	return

class maintain_db:
	def __init__(self):
		self.time = time()

	def maintain(self) -> None:
		cursor = db_connect(LIND_DB_FILE, timeout=20.0).cursor()

		cursor.execute("DELETE FROM linds WHERE expiration_time < ?;", (time(),))

		cursor.connection.commit()
		cursor.connection.close()
		return

	def check_maintenance(self) -> None:
		if self.time < time():
			self.time = time() + 43200
			t = Thread(target=self.maintain)
			t.start()
		return
