#!/usr/bin/env python
from flask import Flask, session, redirect, url_for, render_template, request, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
import hashlib

from app import app, lm

import app.database as db
import app.permissions as perm
import app.navigation as nav
import app.forum as f


print ('[LOG] Create Tables')
db.init_db(app)

@lm.user_loader
def load_user(user_id):
    return db.getUserByID(user_id)

# Return values:
# 0 - Error
# 1 - Success
# 2 - Login redirect
# 3 - Denied redirect
def checkAccess(requiredPermission = '+', redir = True):
    if current_user.is_authenticated:
        userPermissions = db.getPermissions(current_user.name)
        if  not (type (userPermissions) == int) and (requiredPermission in userPermissions or ('*' in userPermissions)):
            return 1
        else: return 3
    if current_user.is_authenticated:
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

    if current_user.is_authenticated:
        userPermissions = db.getPermissions(current_user.name)
        if (type (userPermissions) == int):
            return []
        for key in permissions:
            if key in userPermissions or '*' in userPermissions:
                if permissions[key] in sites:
                    userNav.append(permissions[key])

    return userNav

def getDefaultVars():
    vars = {}
    vars['year'] = datetime.today().year
    vars['title'] = 'Home'
    vars['active'] = 'Home'
    vars['nav'] = getNav()
    if current_user.is_authenticated:
        vars['user'] = current_user.name 
        vars['permissions'] = db.getPermissions(vars['user'])
        vars['userid'] = db.getIDFromName(vars['user'])
        tmpUser = db.getUserByID(vars['userid'])
        if tmpUser == -1:
            vars['avatar'] = 'static/images/default-avatar.jpg'
        else:
            vars['avatar'] = tmpUser.avatar
        vars['action_required'] = 0
        if not type (vars['permissions']) == int and ('a' in vars['permissions'] or '*' in vars['permissions']):
            vars['action_required'] = db.getActionRequired()
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
    res_posts = db.getLastPosts()
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

        if username and password:
            tmpUser = db.signIn(username, password)
            if tmpUser:
                login_user(tmpUser)
                return redirect('/')
        
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
        if db.userInDB(username) == 1:
            errors.append('User already exists.')

        vars['errors'] = errors

        if not errors:
            tmpUser = db.registerUser(username, password, email)
            login_user(tmpUser)

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

	userPermissions = db.getPermissions(current_user.name)
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
        
    vars['users'] = db.getUsers()

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

        vars['selectedUser'] = db.getUserByID(id)

        vars['errors'] = errors
        vars['active'] = 'admin'
        vars['permissions'] = permissions
        return render_template('pages/admin_edit_permissions.html', vars=vars)
    
    if request.method == 'POST':
        permissions = request.form.get('permissions')

        db.updatePermissions(id, permissions)
        print ('[LOG] Permissions for User with ID ' + str(id) + ' have been updated')
        
        return redirect('/admin')

@app.route('/logout')
def logout():
	logout_user()
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
    return f.forum(current_user, vars)

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
        return f.create_cat(current_user, vars)
    if request.method == 'POST':
	    return f.create_catPOST(current_user, vars)

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
        return f.create_topic(current_user, vars)
    if request.method == 'POST':
	    return f.create_topicPOST(current_user, vars)

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
    return f.category(current_user, vars)

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
        return f.topic(current_user, vars)
    if request.method == 'POST':
	    return f.topicPOST(current_user, vars)

@app.route('/delete/post/<topicId>/<postId>')
def deletePost(topicId, postId):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    post = db.getPostById(postId)

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
        
    f.deletePost(current_user, postId)
    return redirect('/topic?id=' + str(topicId))

@app.route('/delete/topic/<topicId>')
def deleteTopic(topicId):
    result = checkAccess('a')
    if result == 2: return redirect('/login')
    elif result == 3: 
        vars = getDefaultVars()
        return render_template('pages/access-denied.html', vars=vars)

    topic = db.getTopicByID(topicId)

    vars = getDefaultVars()
    vars['topic'] = topic
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

    f.deleteTopic(current_user, topicId)
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
