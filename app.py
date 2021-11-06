# -*- coding: utf-8 -*-

import json
import time
import hashlib

from pymongo import MongoClient
from flask import Flask, render_template, request, session

app = Flask(__name__)
db = MongoClient('localhost', 27017).Karimi.Bez

def add_music(name, link):
    """ try to add song in the db """
    try:
        data = {'_id': name, 'title': name, 'link': link, 'reviews': []}
        db.insert_one(data)
    except Exception:
        pass

@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s)

@app.route('/', methods=['GET', 'POST'])
@app.route('/<song_name>', methods=['GET', 'POST'])
def index(song_name=None):
    """ return page for provided song name """
    if song_name:
        song = db.find_one({'title': song_name})
    else:
        song = db.find_one()

    # check form submit
    alert_message = None
    try:
        if 'login' in request.form:
            username = request.form['username']
            password = hashlib.md5(request.form['password'].encode()).hexdigest()
            user = db.find_one({'user': username, 'pass': password})
            if user:
                session['user'] = username
                alert_message = 'Welcome ' + username
            else:
                if db.find_one({'user': username}):
                    alert_message = 'Incorrect Password!'
                else:
                    alert_message = 'User doesn\'t exist!'
        elif 'signup' in request.form:
            username = request.form['username']
            password = hashlib.md5(request.form['password'].encode()).hexdigest()
            if db.find_one({'user': username}):
                alert_message = 'User already exist!'
            else:
                db.insert_one({'user': username, 'pass': password})
                alert_message = 'Account Created. Now you can login!'
        elif 'logout' in request.form:
            session.pop('user', None)
            alert_message = 'Logged out!'
        elif 'review' in request.form:
            if song and ('user' in session):
                data = {'cid': len(song['reviews']),
                        'user': session['user'],
                        'timestamp': int(time.time()),
                        'description': request.form['review'],
                        'comments': []}
                song['reviews'].append(data)
                db.update({'_id': song['_id']}, {'$push': {'reviews': data}})
                alert_message = 'Comment Posted!'
            else:
                alert_message = 'Invalid Request!'
        elif 'comment' in request.form:
            cid = int(request.form.get('parent', 0))
            if song and ('user' in session) and (cid < len(song['reviews'])) and (cid >= 0):
                data = {'user': session['user'], 'timestamp': int(time.time()), 'description': request.form['comment']}
                song['reviews'][cid]['comments'].append(data)
                db.update({'_id': song['_id'], 'reviews.cid': cid}, {'$push': {'reviews.$.comments': data}})
                alert_message = 'Comment Posted!'
            else:
                alert_message = 'Invalid Request!'
    except Exception as e:
        alert_message = str(e)
        print(e)

    return render_template('index.html', current=song, sess=session, message=alert_message)

if __name__ == '__main__':

    # add songs to the database
    add_music('Let Her Go', 'http://www.youtube.com/embed/RBumgq5yVrA')
    add_music('We Don\'t Talk Anymore', 'http://www.youtube.com/embed/3AtDnEC4zak')

    # run server
    app.secret_key = 'some_secret_key'
    app.run(host='0.0.0.0', port=8000, debug=True)
