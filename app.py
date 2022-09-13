#!/usr/bin/env python
from flask import Flask, session, redirect, url_for, render_template, request, flash
from flask_session import Session
from datetime import datetime, timedelta
import hashlib

import sys
from waitress import serve

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(days=365)
Session(app)

import services.main_db as m_db
import services.forum_database as f_db

import services.permissions as perm
import services.navigation as nav
import services.forum as f

# create tables
print ('[LOG] Create Tables')
m_db.createTableUsers()
m_db.createTableNews()
f_db.createTables()

# Return values:
# 0 - Error
# 1 - Success
# 2 - Login redirect
# 3 - Denied redirect
def checkAccess(requiredPermission = '+', redir = True):
    if session.get('access') == 'true' and session.get('name'):
        userPermissions = m_db.getPermissions(session['name'])
        if  not (type (userPermissions) == int) and (requiredPermission in userPermissions or ('*' in userPermissions)):
            return 1
        else: return 3
    if session.get('access') == True and session['access'] == 'true':
        if redir:
            return 3
        else: return 0
    if redir:
        return 2
    else:
        return 0

def getNav():
    userNav = []
    permissions = perm.getPermissionList()
    sites = nav.getSites()

    if session.get('access') == 'true' and session.get('name'):
        userPermissions = m_db.getPermissions(session['name'])
        if (type (userPermissions) == int):
            return []
        for key in permissions:
            if key in userPermissions or '*' in userPermissions:
                if permissions[key] in sites:
                    userNav.append(permissions[key])

    return userNav

def getAvatar(email):
    return 'https://www.gravatar.com/avatar/' + hashlib.md5(email.lower().encode('utf-8')).hexdigest()

def getDefaultVars():
    vars = {}
    vars['year'] = datetime.today().year
    vars['title'] = 'Home'
    vars['active'] = 'Home'
    vars['nav'] = getNav()
    if session.get('name'):
        vars['user'] = session['name'] 
        vars['permissions'] = m_db.getPermissions(vars['user'])
        vars['userid'] = m_db.getIDFromName(vars['user'])
        tmpUser = m_db.getUserByID(vars['userid'])
        vars['avatar'] = getAvatar(tmpUser[3])
        vars['action_required'] = 0
        if not type (vars['permissions']) == int and ('a' in vars['permissions'] or '*' in vars['permissions']):
            vars['action_required'] = m_db.getActionRequired()
            if vars['action_required'] > 9:
                vars['action_required'] = 9

    return vars

@app.route('/home')
def home():
	return redirect('/')

@app.route('/')
def index():
    result = checkAccess()
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    vars = getDefaultVars()
    vars['title'] = 'Home'
    vars['active'] = 'home'

	#forum
    res_posts = f_db.getLastPosts()
    if res_posts == -1 or res_posts == 0:
        res_posts = None
    vars['res_posts'] = res_posts

    return render_template('pages/home.html', vars=vars)

@app.route('/login', methods = ['GET', 'POST','DELETE', 'PATCH'])
def login():
    result = checkAccess()
    if result == 1: return redirect('/')

    errors = list()
    vars = {}
    vars['year'] = datetime.today().year

    if request.method == 'GET':
        vars['error'] = False

        return render_template('pages/login.html', vars=vars)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password and m_db.signIn(username, password):
            session['access'] = 'true'
            session['name'] = username
            session['id'] = m_db.getIDFromName(username)
            return redirect('/')
        else:
            vars['error'] = True
            errors.append('Login failed.')

        vars['errors'] = errors
        return render_template('pages/login.html', vars=vars)

@app.route('/register', methods = ['GET', 'POST','DELETE', 'PATCH'])
def register():
    errors = list()
    vars = getDefaultVars()
    vars['title'] = 'Request Access'
    vars['active'] = ''
    vars['errors'] = errors

    if request.method == 'GET':
        return render_template('pages/login.html', vars=vars)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        email = request.form.get('email')

        if not (username or password or repeat_password or email or len(username) < 1):
            errors.append('Please fill in every field.')
        if len(username) > 20:
            errors.append('Your username may not exceed 20 characters.')
        if not password == repeat_password:
            errors.append('Passwords do not match.')
        if m_db.userInDB(username)[0]:
            errors.append('User already exists.')

        vars['errors'] = errors

        if not errors:
            m_db.registerUser(username, password, email)
            session['access'] = 'true'
            session['name'] = username

        if errors:
            print ('[LOG] ' + str(username) + ' requested Access but an error occured')
            return render_template('pages/login.html', vars=vars)
        
        print ('[LOG] ' + str(username) + ' requests Access')
        return redirect('/')

@app.route('/denied')
def denied():
	vars = getDefaultVars()
	vars['title'] = '403'
	vars['active'] = ''

	userPermissions = m_db.getPermissions(session['name'])
	vars['activate'] = False
	if  (type (userPermissions) == int):
		vars['activate'] = True
	
	return render_template('pages/access-denied.html', vars=vars)

@app.route('/admin')
def admin():
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)
           
    permissions = perm.getPermissionList()
    errors = list()
    vars = getDefaultVars()

    vars['headline'] = 'Admin'
    vars['title'] = 'Admin'
        
    vars['users'] = m_db.getUsers()

    vars['errors'] = errors
    vars['active'] = 'admin'
    vars['permissions'] = permissions

    print ('[LOG] ' + vars['user'] + ' looked at the Admin page')
    return render_template('pages/admin.html', vars=vars)

@app.route('/admin/edit/permissions/<id>', methods = ['GET', 'POST','DELETE', 'PATCH'])
def adminEditPermissions(id):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    if request.method == 'GET':
        permissions = perm.getPermissionList()
        errors = list()
        vars = getDefaultVars()

        vars['headline'] = 'Admin'
        vars['title'] = 'Admin'

        vars['selectedUser'] = m_db.getUserByID(id)

        vars['errors'] = errors
        vars['active'] = 'admin'
        vars['permissions'] = permissions
        return render_template('pages/admin_edit_permissions.html', vars=vars)
    
    if request.method == 'POST':
        permissions = request.form.get('permissions')

        m_db.updatePermissions(id, permissions)
        print ('[LOG] Permissions for User with ID ' + str(id) + ' have been updated')
        
        return redirect('/admin')

@app.route('/logout')
def logout():
	session['access'] = 'false'
	session['name'] = ''
	session['id'] = ''
	return redirect('/login')

# Forum
@app.route('/forum')
def forum():
    result = checkAccess('f')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    vars = getDefaultVars()
    vars['active'] = 'forum'
    vars['title'] = 'Forum'
    return f.forum(session, vars)

@app.route('/create_cat', methods = ['GET', 'POST','DELETE', 'PATCH'])
def create_cat():
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    vars = getDefaultVars()
    vars['active'] = 'forum'
    vars['title'] = 'Forum'

    if request.method == 'GET':
        return f.create_cat(session, vars)
    if request.method == 'POST':
	    return f.create_catPOST(session, vars)

@app.route('/create_topic', methods = ['GET', 'POST','DELETE', 'PATCH'])
def create_topic():
    result = checkAccess('f')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    vars = getDefaultVars()
    vars['active'] = 'forum'
    vars['title'] = 'Forum'

    if request.method == 'GET':
        return f.create_topic(session, vars)
    if request.method == 'POST':
	    return f.create_topicPOST(session, vars)

@app.route('/category', methods = ['GET', 'POST','DELETE', 'PATCH'])
def category():
    result = checkAccess('f')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    vars = getDefaultVars()
    vars['active'] = 'forum'
    vars['title'] = 'Forum'
    return f.category(session, vars)

@app.route('/topic', methods = ['GET', 'POST','DELETE', 'PATCH'])
def topic():
    result = checkAccess('f')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    vars = getDefaultVars()
    vars['active'] = 'forum'
    vars['title'] = 'Forum'

    if request.method == 'GET':
        return f.topic(session, vars)
    if request.method == 'POST':
	    return f.topicPOST(session, vars)

@app.route('/delete/post/<topicId>/<postId>')
def deletePost(topicId, postId):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    post = f_db.getPostById(postId)

    vars = getDefaultVars()
    vars['post'] = post[0]
    vars['active'] = 'forum'
    vars['title'] = 'Forum'
        
    return render_template('pages/forum_delete_post.html', vars=vars)

@app.route('/delete/post/<topicId>/<postId>/confirm')
def deletePostConfirm(topicId, postId):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)
        
    f.deletePost(session, postId)
    return redirect('/topic?id=' + str(topicId))

@app.route('/delete/topic/<topicId>')
def deleteTopic(topicId):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    topic = f_db.getTopicByID(topicId)

    vars = getDefaultVars()
    vars['topic'] = topic[0]
    vars['active'] = 'forum'
    vars['title'] = 'Forum'

    return render_template('pages/forum_delete_topic.html', vars=vars)

@app.route('/delete/topic/<topicId>/confirm')
def deleteTopicConfirm(topicId):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    f.deleteTopic(session, topicId)
    return redirect('/forum')
	
# Errors
@app.route('/error/<err>')
def showError(err):
    result = checkAccess('+')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    # errors start with perrmission symbol followed by a unique code
    errors = {}
    errors['p000'] = 'ID has to be an positive integer.'

    vars = getDefaultVars()
    vars['title'] = 'Error'
    vars['code'] = err
    vars['content'] = errors[err] if err in errors else None
    vars['active'] = ''

    return render_template('pages/error.html', vars=vars)

@app.errorhandler(404)
def error404(error):
    result = checkAccess('+')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)
        
    vars = getDefaultVars()
    vars['title'] = 'Error'
    vars['code'] = '404'
    vars['content'] = 'I have no time for a fancy 404 page. You are lost though.'
    vars['active'] = ''

    return render_template('pages/error.html', vars=vars), 404

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'dev':
        print ('[LOG] Run development server')
        app.run(debug=True)
    else:
        print ('[LOG] Run production server')
        serve(app, host='0.0.0.0', port=8080)
