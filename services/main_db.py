import sqlite3
import re
import hashlib
import time
from datetime import date
import datetime

dbfile = 'database/main.sqlt'

def createTableUsers():
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
user_name VARCHAR(30) NOT NULL,
user_pass VARCHAR(255) NOT NULL,
user_email VARCHAR(255) NOT NULL,
user_date DATETIME NOT NULL,
user_permissions VARCHAR(255) NOT NULL,
user_avatar VARCHAR(255) NOT NULL
);''')
    conn.commit()

def createTableNews():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS news (
post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
post_title TEXT NOT NULL,
post_content TEXT NOT NULL,
post_date DATETIME NOT NULL
);''')
	conn.commit()

def registerUser(user_name, user_pass, user_email, user_permissions = ''):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	user_avatar = 'https://www.gravatar.com/avatar/' + hashlib.md5(user_email.lower().encode('utf-8')).hexdigest()
	c.execute('INSERT INTO users (user_name, user_pass, user_email, user_date, user_permissions, user_avatar) VALUES (?, ?, ?, DATETIME("NOW"), ?, ?);', 
(user_name, hashlib.sha512(user_pass.encode('utf-8')).hexdigest(), user_email, user_permissions, user_avatar))
	conn.commit()

def signIn(user_name, user_pass):
	user_pass = user_pass.encode('utf-8')
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	res = c.execute('SELECT 1 FROM users WHERE user_name = ? AND user_pass = ?;', 
(user_name, hashlib.sha512(user_pass).hexdigest())).fetchall()
	conn.commit()
	return res if res else 0

def getPermissions(name):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT user_permissions FROM users WHERE user_name = ?", (name,))
 
	rows = c.fetchone()
	if not rows: return -1
	return rows[0] if rows[0] else -1

def getPermissionsByID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT user_permissions FROM users WHERE user_id = ?", (id,))
 
	rows = c.fetchone()
	return rows[0] if rows[0] else -1

def getActionRequired():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT COUNT(user_id) FROM users WHERE user_permissions = ''")
	
	rows = c.fetchone()
	return rows[0] if rows[0] else -1

def updatePermissions(id, permissions):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('UPDATE users SET user_permissions = ? WHERE user_id = ?;', (permissions, id))
	conn.commit()

def userInDB(name):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_name = ? COLLATE NOCASE LIMIT 1);", (name,))
 
	rows = c.fetchall()[0]
	return rows if rows else -1

def getUsers():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT * FROM users")
	
	rows = c.fetchall()
	return rows if rows else -1

def getUserByID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT * FROM users WHERE user_id = ?", (id,))
	
	rows = c.fetchall()
	return rows[0] if rows[0] else -1

def getIDFromName(name):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT user_id FROM users WHERE user_name = ?;", (name,))

	rows = c.fetchone()
	if not rows:
		return -1
	return rows[0] if rows[0] else -1

def getNameFromID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT user_name FROM users WHERE user_id = ?;", (id,))

	rows = c.fetchone()
	return rows[0] if rows[0] else -1

if __name__ == "__main__":
	createTableUsers()
	import getpass
	print ("Add user account: ")
	user_name = input("Please enter the username: ")
	user_email = input("Please enter the email: ")
	user_pass = getpass.getpass("Please enter the password: ")
	user_permissions = "*"
	registerUser(user_name, user_pass, user_email, user_permissions)