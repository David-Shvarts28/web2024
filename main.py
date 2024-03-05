from flask import Flask, url_for, request, render_template, session, redirect
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms import StringField, TextAreaField
from werkzeug.utils import secure_filename

from data import db_session
from fill_db import fill_users, get_user
from data.users import User
from data.news import News

DB_NAME = 'site'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

settings = {"user_name": input()
            }


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
                           css_url=f"{url_for('static', filename='css/style.css')}",
                           title="Главная страница", user_name=settings.get('user_name', 'Аноним'))



@app.route('/users_page')
def return_sample_page():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('users_page.html', title='Список пользователей', users=users)


@app.route('/test_carousel', methods=['POST', 'GET'])
def return_carousel():
    if 'pics' not in settings:
        settings['pics'] = [(f"{url_for('static', filename='img/1.jpeg')}", "first"),
                            (f"{url_for('static', filename='img/2.jpeg')}", "second"),
                            (f"{url_for('static', filename='img/3.jpeg')}", "third")
                            ]
    if request.method == 'POST':
        f = request.files['file']
        settings["avatar_file"] = f.filename
        f.save(f'static/img/{f.filename}')
        settings['pics'].append((f"{url_for('static', filename=f'img/{f.filename}')}", "first"))
    return render_template('test_carousel.html', title='Карусель', pics=settings['pics'])


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


@app.route('/news', methods=['GET', 'POST'])
def add_news():
    form = NewsForm()
    current_user = get_user(DB_NAME)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_news.html', title='Добавление новости',
                           form=form)


def main():
    db_session.global_init(f"db/{DB_NAME}.db")
    fill_users(DB_NAME)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
# http://127.0.0.1:8080/