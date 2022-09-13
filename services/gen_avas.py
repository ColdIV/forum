import sqlite3
import re
import hashlib
import time
from datetime import date
import datetime

dbfile = 'database/main.sqlt'

def getUsers():
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute("SELECT * FROM users")
	
	rows = c.fetchall()
	return rows if rows else -1

def updateAvatar(id, user_avatar):
	conn = sqlite3.connect(dbfile)
	c = conn.cursor()
	c.execute('UPDATE users SET user_avatar = ? WHERE user_id = ?;', (user_avatar, id))
	conn.commit()

if __name__ == "__main__":
    users = getUsers()
    
    for user in users:
        print (user)
        user_email = user[3]
        user_avatar = 'https://www.gravatar.com/avatar/' + hashlib.md5(user_email.lower().encode('utf-8')).hexdigest()
        updateAvatar(user[0], user_avatar)
        print (user)