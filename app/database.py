from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import hashlib

def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        db.session.commit()
        # Check for admin user (should always be first)
        if getUserByID(1) == -1:
            create_admin_user()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.now())
    permissions = db.Column(db.String(255))
    avatar = db.Column(db.String(255))

class Categories(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

class Topics(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.now())
    category_id = db.Column(db.Integer) # foreign key to Category
    author_id = db.Column(db.Integer) # foreign key to User

class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now())
    topic_id = db.Column(db.Integer) # foreign key to Topic
    author_id = db.Column(db.Integer) # foreign key to User


def registerUser(user_name, user_pass, user_email, user_permissions = ''):
    user_pass = user_pass.encode('utf-8')
    user_pass=hashlib.sha512(user_pass).hexdigest()
    user_avatar = 'static/images/default-avatar.jpg'
    new_user = Users(name=user_name, password=user_pass, email=user_email, permissions=user_permissions, avatar=user_avatar, date=datetime.now())
    db.session.add(new_user)
    db.session.commit()
    return new_user

def signIn(user_name, user_pass):
    user_pass = user_pass.encode('utf-8')
    user = Users.query.filter_by(name=user_name, password=hashlib.sha512(user_pass).hexdigest()).first()

    return user if user else 0

def getPermissions(name):
    user = Users.query.filter_by(name=name).first()

    if not user: return -1

    return user.permissions if user.permissions else -1

def getPermissionsByID(id):
    user = Users.query.filter_by(id=id).first()

    if not user: return -1

    return user.permissions if user.permissions else -1

def updatePermissions(id, permissions):
    Users.query.filter_by(id=id).update(dict(permissions=permissions))
    db.session.commit()

# get amount of users that need to be activated
def getActionRequired():
    count = Users.query.filter_by(permissions='').count()

    return count if count else -1

def userInDB(name):
    user = Users.query.filter_by(name=name).first()

    return 1 if user else -1

def getUsers():
    users = Users.query.all()

    return users if users else -1

def getUserByID(id):
    user = Users.query.filter_by(id=id).first()

    return user if user else -1

def getIDFromName(name):
    user = Users.query.filter_by(name=name).first()

    return user.id if user else -1

def getNameFromID(id):
    user = Users.query.filter_by(id=id).first()

    return user.name if user else -1

# def linkTopicsToCategories():
#     conn = sqlite3.connect(dbfile)
#     c = conn.cursor()
#     c.execute('''ALTER TABLE topics ADD FOREIGN KEY(topic_cat) 
# REFERENCES categories(cat_id) ON DELETE CASCADE ON UPDATE CASCADE;''')
#     conn.commit()
    
# def linkTopicsToUsers():
#     conn = sqlite3.connect(dbfile)
#     c = conn.cursor()
#     c.execute('''ALTER TABLE topics ADD FOREIGN KEY(topic_by) 
# REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE;''')
#     conn.commit()
    
# def linkPostsToTopics():
#     conn = sqlite3.connect(dbfile)
#     c = conn.cursor()
#     c.execute('''ALTER TABLE posts ADD FOREIGN KEY(post_topic) 
# REFERENCES topics(topic_id) ON DELETE CASCADE ON UPDATE CASCADE;''')
#     conn.commit()
    
# def linkPostsToUsers():
#     conn = sqlite3.connect(dbfile)
#     c = conn.cursor()
#     c.execute('''ALTER TABLE posts ADD FOREIGN KEY(post_by) 
# REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE;''')
#     conn.commit()

def createCategorie(cat_name, cat_description):
    new_category = Categories(name=cat_name, description=cat_description)
    db.session.add(new_category)
    db.session.commit()

def getCategories():
    categories = Categories.query.all()

    return categories if categories else -1

def getCategoryByName(name):
    category = Categories.query.filter_by(name=name).first()

    return 1 if category else 0

def createTopic(topic_subject, topic_cat, user_id):
    new_topic = Topics(subject=topic_subject, category_id=topic_cat, author_id=user_id, date=datetime.now())
    db.session.add(new_topic)
    db.session.commit()

def addPost(post_content, topic_id, user_id):
    new_post = Posts(content=post_content, topic_id=topic_id, author_id=user_id, date=datetime.now())
    db.session.add(new_post)
    db.session.commit()

    return new_post.id

def gettopicID(topic_subject, topic_cat, user_id):
    topic = Topics.query.filter_by(subject=topic_subject, category_id=topic_cat, author_id=user_id).first()

    return topic.id if topic else -1

def getCategorieByID(id):
    category = Categories.query.filter_by(id=id).first()

    return category if category else -1

def getTopicByCatID(id):
    topic = Topics.query.filter_by(category_id=id)

    return topic if topic else -1

def getTopicByID(id):
    topic = Topics.query.filter_by(id=id).first()

    return topic if topic else -1

def deletePostByID(id):
    post = Posts.query.filter_by(id=id).first()
    count_posts_in_topic = Posts.query.filter_by(topic_id=post.topic_id).count()

    if post and count_posts_in_topic > 1:
        db.session.delete(post)
        db.session.commit()

def deleteAllPostsOfTopic(id):
    Posts.query.filter_by(topic_id=id).delete()
    db.session.commit()

def deleteTopicByID(id):
    deleteAllPostsOfTopic(id)
    Topics.query.filter_by(id=id).delete()
    db.session.commit()

def getTopicInCatBySubject(category_id, topic_subject):
    topic = Topics.query.filter_by(category_id=category_id, subject=topic_subject).first()

    return 1 if topic else -1

def getLastTopOfCat(cat_id):
    topic = Topics.query.filter_by(category_id = cat_id).order_by(Topics.date.desc()).limit(1)
    return (topic.id, topic.subject, topic.date) if topic else (-1, u'-', u'-')

def getLastTopicsOfCat(cat_id, n = 5):
    topics = Topics.query.filter_by(category_id=cat_id).order_by(Topics.date.desc()).limit(n)
    rows = []
    for topic in topics:
        post = Posts.query.filter_by(topic_id=topic.id).order_by(Posts.id).limit(1).first()
        if not post:
            continue
        user = Users.query.filter_by(id=post.author_id).first()
        if not user:
            continue
        rows.append((topic.category_id, topic.id, topic.subject, topic.date, post.id, user.name, post.date))

    return rows if topics else -1

    # rows = db.session.query(Topics, Posts, Users).filter(
    #     Topics.id == Posts.topic_id
    # ).filter(
    #     Users.id == Posts.author_id
    # ).filter(
    #     Topics.category_id == cat_id
    # ).order_by(Topics.date.desc()).limit(n)

    # result = [(t.category_id, t.id, t.subject, t.date, p.id, u.name, p.date) for t, p, u in rows]

    # return result if rows else -1

    # c.execute("""SELECT topic_cat, topic_id, topic_subject, topic_date, 
    # (SELECT post_id FROM posts WHERE post_topic = topic_id ORDER BY post_id DESC LIMIT 1), 
    # (SELECT user_name FROM users WHERE user_id = (SELECT post_by FROM posts WHERE post_topic = topic_id ORDER BY post_id DESC LIMIT 1)), 
    # (SELECT post_date FROM posts WHERE post_topic = topic_id ORDER BY post_id DESC LIMIT 1) 
    # FROM topics WHERE topic_cat = ? ORDER BY topic_date DESC LIMIT ?""", (cat_id,n))

def getPostsByTopID(id):
    rows = db.session.query(Posts, Users).filter(
        Posts.author_id == Users.id
    ).filter(
        Posts.topic_id == id
    )

    result = [(p.topic_id, p.content, p.date, p.author_id, u.id, u.name, p.id, u.avatar) for p, u in rows]

    return result if rows else -1

    # c.execute("SELECT posts.post_topic, posts.post_content, posts.post_date, posts.post_by, users.user_id, users.user_name, posts.post_id, users.user_avatar FROM posts LEFT JOIN users ON posts.post_by = users.user_id WHERE posts.post_topic = ?", (id,))

def getLastPosts(n = 10):
    rows = db.session.query(Posts, Topics, Users).filter(
        Topics.id == Posts.topic_id
    ).filter(
        Posts.author_id == Users.id
    ).order_by(Posts.date.desc()).limit(n)

    result = [(p.topic_id, p.content, p.date, p.author_id, u.id, u.name, p.id, t.subject, u.avatar) for p, t, u in rows]

    return result if rows else -1

    # c.execute("SELECT posts.post_topic, posts.post_content, posts.post_date, posts.post_by,
    # users.user_id, users.user_name, posts.post_id,
    # (SELECT topic_subject FROM topics WHERE topic_id = posts.post_topic),
    # users.user_avatar
    # FROM posts LEFT JOIN users ON posts.post_by = users.user_id ORDER BY posts.post_date DESC LIMIT 10")

def getUserId(user_name):
    user = Users.query.filter_by(name = user_name)

    return user.id if user else -1

def getPostById(id):
    rows = db.session.query(Posts, Users).filter(
        Posts.author_id == Users.id
    ).filter(
        Posts.id == id
    )

    result = [(p.topic_id, p.content, p.date, p.author_id, u.id, u.name, p.id) for p, u in rows]

    return result if rows else -1

    # c.execute("SELECT posts.post_topic, posts.post_content, posts.post_date, posts.post_by, users.user_id, users.user_name, posts.post_id
    # FROM posts LEFT JOIN users ON posts.post_by = users.user_id WHERE posts.post_id = ?", (id,))

def updateAvatar(id, user_avatar):
    Users.query.filter_by(id=id).update(dict(avatar=user_avatar))
    db.session.commit()

def create_admin_user():
    import getpass
    print ("Add user account: ")
    user_name = input("Please enter the username: ")
    user_email = input("Please enter the email: ")
    user_pass = getpass.getpass("Please enter the password: ")
    user_permissions = "*"
    registerUser(user_name, user_pass, user_email, user_permissions)
