from flask import Flask, session, redirect, url_for, render_template, request, flash

import app.database as db

from markupsafe import escape, Markup
import bbcode
parser = bbcode.Parser(url_template='<a href="{href}" target="_blank">{text}</a>')

def forum(session, vars):
    errors = list()
    res = db.getCategories()
    if res == -1:
        errors.append("The categories could not be displayed, please try again later.")
    elif res == 0:
        errors.append("No categories defined yet.")

    topics = list()
    if not errors:
        for i,r in enumerate(res):
            topics = list()
            topics.append(db.getLastTopicsOfCat(r.id))
            res[i] = (r.id, r.name, r.description,topics)
    
    vars['errors'] = errors
    vars['access'] = session['access'] or None
    vars['res'] = res
    vars['topics'] = topics or None
    
    return render_template('pages/forum_index.html', vars=vars)

def create_cat(session, vars):
    errors = list()

    vars['errors'] = errors
    vars['access'] = session['access'] or None

    return render_template('pages/forum_create_cat_pre.html', vars=vars)

def create_catPOST(session, vars):
    errors = list()

    cat_name = request.form.get('cat_name')
    cat_description = request.form.get('cat_description')

    if not session['access'] == 'true':
        errors.append("You must be logged in to create a category.")
    if not cat_name:
        errors.append("The categorie name field must not be empty.")
    if not cat_description:
        errors.append("The categorie description field must not be empty.")

    if not errors:
        res = db.getCategoryByName(cat_name)
        if res == 1:
            errors.append("Couldn't create category.")
        else:
            print ("[LOG] " + vars["user"] + " created category " + str(cat_name))
            db.createCategorie(cat_name, cat_description)

    vars['errors'] = errors
    vars['access'] = session['access'] or None

    return render_template('pages/forum_create_cat_post.html', vars=vars)

def create_topic(session, vars):
    errors = list()
    res = db.getCategories()
    if res == -1:
        errors.append("The categories could not be displayed, please try again later.")
    elif res == 0:
        errors.append("No categories defined yet.")

    vars['errors'] = errors
    vars['access'] = session['access'] or None
    vars['res'] = res

    return render_template('pages/forum_create_topic_pre.html', vars=vars)

def create_topicPOST(session, vars):
    errors = list()

    topic_subject = request.form.get('topic_subject')
    topic_cat = request.form.get('topic_cat')
    user_id = db.getIDFromName(vars["user"])
    post_content = request.form.get('post_content')

    if not topic_subject or len(topic_subject) < 3:
        errors.append("The topic subject must be at least 3 characters long.")
    if len(topic_subject) > 50:
        errors.append("The topic subject may not be longer than 50 characters.")
    if not topic_cat:
        errors.append("The topic category field must not be empty.")
    if not post_content or len(post_content) < 3:
        errors.append("The topic message must be at least 3 characters long.")
    if len(post_content) > 2000:
        errors.append("The topic message may not be longer than 2000 characters.")
    if not session['access'] == 'true':
        errors.append("You must be logged in.")
    if db.getTopicInCatBySubject(topic_cat, topic_subject) != -1:
        errors.append("The topic already exists in this category.")

    if not errors:
        print ("[LOG] " + vars["user"] + " created topic " + str(topic_subject))
        db.createTopic(topic_subject, topic_cat, user_id)

        if not post_content:
            errors.append("The message field must not be empty.")
        else:
            topic_id = db.gettopicID(topic_subject, topic_cat, user_id)
            if topic_id == -1:
                errors.append("Couldn't connect to the database.")
        if not errors:
            db.addPost(post_content, topic_id, user_id)
            redirect('/topic?id=' + str(topic_id))
        
        vars['topic_id'] = topic_id or None

    vars['errors'] = errors
    vars['access'] = session['access'] or None

    return render_template('pages/forum_create_topic_post.html', vars=vars)

def category(session, vars):
    errors = list()

    cat_id = request.args.get('id','')
    res_cat = 0
    if cat_id and int(cat_id) > 0:
        res_cat = db.getCategorieByID(cat_id)

    if res_cat == -1:
        errors.append("The category could not be displayed, please try again later.")
    elif res_cat == 0:
        errors.append("This category does not exist.")
    
    res_top = None
    if not errors:
        res_top = db.getTopicByCatID(cat_id)

        if res_top == -1:
            errors.append("The topics could not be displayed, please try again later.")
        elif res_top == 0:
            errors.append("There are no topics in this category yet.")

    vars['errors'] = errors
    vars['access'] = session['access'] or None
    vars['res_cat'] = res_cat
    vars['res_top'] = res_top
    
    return render_template('pages/forum_category.html', vars=vars)
    
def topic(session, vars):
    errors = list()
    
    top_id = request.args.get('id','')
    if top_id and int(top_id) > 0:
        top_id = int(top_id)
        res_top = db.getTopicByID(top_id)

        if res_top == -1:
            errors.append("The topic could not be displayed, please try again later.")
        elif res_top == 0:
            errors.append("This topic does not exist.")
    else:
        errors.append("This topic does not exist.")

    if not errors:
        res_posts = db.getPostsByTopID(top_id)

        if res_posts == -1:
            errors.append("The posts could not be displayed, please try again later.")
        elif res_posts == 0 or not res_posts:
            errors.append("There are no posts in this topic yet.")

        if not errors:
            vars['res_top'] = res_top or None
            vars['res_posts'] = res_posts or None

    vars['errors'] = errors
    vars['access'] = session['access'] or None
    vars['user_id'] = db.getIDFromName(vars["user"])
    vars['reply_content'] = None

    return render_template('pages/forum_topic.html', vars=vars)

def topicPOST(session, vars):
    errors = list()

    vars['res_posts'] = None

    if not session['access']:
        errors.append("You must be signed in to post a reply.")
    
    top_id = request.args.get('id','')
    top_id = int(top_id)
    res_top = db.getTopicByID(top_id)
    reply_content = ''
    user_id = -1

    if res_top == -1:
        errors.append("The topic could not be displayed, please try again later.")
    elif res_top == 0:
        errors.append("This topic does not exist.")
    
    if not errors:
        res_posts = db.getPostsByTopID(top_id)

        if res_posts == -1:
            errors.append("The posts could not be displayed, please try again later.")
        elif res_posts == 0:
            errors.append("There are no posts in this topic yet.")
        vars['res_posts'] = res_posts or None
        reply_content = request.form.get('reply_content')
        user_id = db.getIDFromName(vars["user"])

        if not reply_content or len(reply_content) < 3:
            errors.append("The post must be at least 3 characters long.")
        if not reply_content or len(reply_content) > 2000:
            errors.append("The post may not be longer than 2000 characters.")
        if not user_id:
            errors.append("You must be signed in to post a reply.")
        
        # parse bbcodes
        content = Markup(parser.format(reply_content))

        post_id = db.addPost(content, top_id, user_id)
        print ("[LOG] " + vars["user"] + " created post #" + str(post_id))
        
        redirect('/topic?id=' + str(top_id) + '#post' + str(post_id))

    vars['errors'] = errors
    vars['access'] = session['access'] or None
    vars['res_top'] = res_top or None
    vars['reply_content'] = content or ' '
    vars['post_id'] = post_id
    vars['user_id'] = user_id

    return render_template('pages/forum_topic.html', vars=vars)

def deletePost(session, postId):
    print ("[LOG] Deleted post #" + str(postId))
    db.deletePostByID(postId)

def deleteTopic(session, topicId):
    print ("[LOG] Deleted topic #" + str(topicId))
    db.deleteTopicByID(topicId)
