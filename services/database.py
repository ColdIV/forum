import sqlite3
import hashlib

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
	
def createTableCategories():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS categories (
cat_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
cat_name VARCHAR(255) NOT NULL,
cat_description VARCHAR(255) NOT NULL,
CONSTRAINT cat_name_unique UNIQUE (cat_name)
);''')
	conn.commit()
	
def createTableTopics():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS topics (
topic_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
topic_subject VARCHAR(255) NOT NULL,
topic_date DATETIME NOT NULL,
topic_cat INTEGER NOT NULL,
topic_by INTEGER NOT NULL
);''')
	conn.commit()
	
def createTablePosts():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS posts (
post_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
post_content TEXT NOT NULL,
post_date DATETIME NOT NULL,
post_topic INTEGER NOT NULL,
post_by INTEGER NOT NULL
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

def updatePermissions(id, permissions):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('UPDATE users SET user_permissions = ? WHERE user_id = ?;', (permissions, id))
	conn.commit()

def getActionRequired():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT COUNT(user_id) FROM users WHERE user_permissions = ''")
	
	rows = c.fetchone()
	return rows[0] if rows[0] else -1

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

def linkTopicsToCategories():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''ALTER TABLE topics ADD FOREIGN KEY(topic_cat) 
REFERENCES categories(cat_id) ON DELETE CASCADE ON UPDATE CASCADE;''')
	conn.commit()
	
def linkTopicsToUsers():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''ALTER TABLE topics ADD FOREIGN KEY(topic_by) 
REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE;''')
	conn.commit()
	
def linkPostsToTopics():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''ALTER TABLE posts ADD FOREIGN KEY(post_topic) 
REFERENCES topics(topic_id) ON DELETE CASCADE ON UPDATE CASCADE;''')
	conn.commit()
	
def linkPostsToUsers():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('''ALTER TABLE posts ADD FOREIGN KEY(post_by) 
REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE;''')
	conn.commit()

def createCategorie(cat_name, cat_description):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('INSERT OR IGNORE INTO categories (cat_name, cat_description) VALUES (?, ?);', 
(cat_name, cat_description))
	conn.commit()

def getCategories():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('SELECT cat_id, cat_name, cat_description FROM categories')

	rows = c.fetchall()
	return rows if rows else -1

def getCategorieByName(name):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('SELECT cat_id, cat_name, cat_description FROM categories WHERE cat_name = ?', (name,))

	rows = c.fetchall()
	return 1 if rows else 0

def createTopic(topic_subject, topic_cat, user_id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('INSERT INTO topics(topic_subject, topic_date, topic_cat, topic_by) VALUES (?, DATETIME("NOW"), ?, ?);', 
(topic_subject, topic_cat, user_id))
	conn.commit()

def addPost(post_content, topic_id, user_id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('INSERT INTO posts(post_content, post_date, post_topic, post_by) VALUES (?, DATETIME("NOW"), ?, ?);', 
(post_content, topic_id, user_id))
	conn.commit()

	return c.lastrowid

def gettopicID(topic_subject, topic_cat, user_id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT topic_id FROM topics WHERE topic_subject= ? AND topic_cat= ? AND topic_by= ? ORDER BY topic_id DESC LIMIT 1;", (topic_subject, topic_cat, user_id))
 
	rows = c.fetchall()
	return rows[0][0] if rows else -1
	
def getCategorieByID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT cat_id, cat_name, cat_description FROM categories WHERE cat_id = ? AND cat_id > 0", (id,))
 
	rows = c.fetchall()
	return rows if rows else -1

def getTopicByCatID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT topic_id, topic_subject, topic_date, topic_cat FROM topics WHERE topic_cat = ?", (id,))
 
	rows = c.fetchall()
	return rows if rows else -1

def getTopicByID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT topic_id, topic_subject FROM topics WHERE topic_id = ?", (id,))
 
	rows = c.fetchall()
	return rows if rows else -1

def deletePostByID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("DELETE FROM posts WHERE post_id=? AND (SELECT COUNT(post_id) FROM posts WHERE post_topic=(SELECT post_topic FROM posts WHERE post_id=?))>1", (id, id))
	conn.commit()

def deleteAllPostsOfTopic(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("DELETE FROM posts WHERE post_topic=?", (id,))
	conn.commit()

def deleteTopicByID(id):
	deleteAllPostsOfTopic(id)
	
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("DELETE FROM topics WHERE topic_id=?", (id,))
	conn.commit()


def getTopicInCatBySubject(category_id, topic_subject):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT COUNT(topic_subject) FROM topics WHERE topic_cat=? AND topic_subject=?", (category_id, topic_subject))
	
	rows = c.fetchone()
	return rows[0] if rows[0] else -1

def getLastTopOfCat(cat_id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT topic_id, topic_subject, topic_date FROM topics WHERE topic_cat = ? ORDER BY topic_date DESC LIMIT 1", (cat_id,))
 
	rows = c.fetchall()
	return rows[0] if rows else (-1, u'-', u'-')

def getLastTopicsOfCat(cat_id, n = 5):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("""SELECT topic_cat, topic_id, topic_subject, topic_date, 
	(SELECT post_id FROM posts WHERE post_topic = topic_id ORDER BY post_id DESC LIMIT 1), 
	(SELECT user_name FROM users WHERE user_id = (SELECT post_by FROM posts WHERE post_topic = topic_id ORDER BY post_id DESC LIMIT 1)), 
	(SELECT post_date FROM posts WHERE post_topic = topic_id ORDER BY post_id DESC LIMIT 1) 
	FROM topics WHERE topic_cat = ? ORDER BY topic_date DESC LIMIT ?""", (cat_id,n))

	rows = c.fetchall()
	return rows if rows else -1

def getPostsByTopID(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT posts.post_topic, posts.post_content, posts.post_date, posts.post_by, users.user_id, users.user_name, posts.post_id, users.user_avatar FROM posts LEFT JOIN users ON posts.post_by = users.user_id WHERE posts.post_topic = ?", (id,))
 
	rows = c.fetchall()
	return rows if rows else -1

def getLastPosts():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT posts.post_topic, posts.post_content, posts.post_date, posts.post_by, users.user_id, users.user_name, posts.post_id, (SELECT topic_subject FROM topics WHERE topic_id = posts.post_topic), users.user_avatar FROM posts LEFT JOIN users ON posts.post_by = users.user_id ORDER BY posts.post_date DESC LIMIT 10")

	rows = c.fetchall()
	return rows if rows else -1

def getUserId(user_name):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT user_id FROM users WHERE user_name = ?", (user_name,))
 
	rows = c.fetchall()
	return rows[0][0] if rows else -1

def getPostById(id):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT posts.post_topic, posts.post_content, posts.post_date, posts.post_by, users.user_id, users.user_name, posts.post_id FROM posts LEFT JOIN users ON posts.post_by = users.user_id WHERE posts.post_id = ?", (id,))
 
	rows = c.fetchall()
	return rows if rows else -1

def updateAvatar(id, user_avatar):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('UPDATE users SET user_avatar = ? WHERE user_id = ?;', (user_avatar, id))
	conn.commit()

def createTables():
    createTableCategories()
    createTableTopics()
    createTablePosts()

if __name__ == "__main__":
	createTableUsers()
	import getpass
	print ("Add user account: ")
	user_name = input("Please enter the username: ")
	user_email = input("Please enter the email: ")
	user_pass = getpass.getpass("Please enter the password: ")
	user_permissions = "*"
	registerUser(user_name, user_pass, user_email, user_permissions)
