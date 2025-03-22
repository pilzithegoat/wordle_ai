from flask import Flask, render_template, request, redirect, url_for
from database import Session, Word
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('WEB_SECRET')

@app.route('/')
def index():
    session = Session()
    words = session.query(Word).all()
    daily_word = session.query(Word).filter_by(is_daily=True).first()
    session.close()
    return render_template('index.html', words=words, daily_word=daily_word)

@app.route('/add_word', methods=['POST'])
def add_word():
    word = request.form['word'].lower()
    if len(word) != 5:
        return redirect(url_for('index'))
    
    session = Session()
    if not session.query(Word).get(word):
        new_word = Word(word=word)
        session.add(new_word)
        session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/set_daily', methods=['POST'])
def set_daily():
    word = request.form['word'].lower()
    session = Session()
    
    # Reset current daily
    session.query(Word).update({Word.is_daily: False})
    
    # Set new daily
    target = session.query(Word).get(word)
    if target:
        target.is_daily = True
    session.commit()
    session.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
