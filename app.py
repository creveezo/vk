import os
from preprocessing import fin
from preprocessing import basic_info
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'GET':
        title = request.args.get('title')
        values = {'title': title}
        if title or title != '':
            return public(id=title)

    return render_template('search_init.html', values={})


@app.route('/analysis/<id>')
def public(id):
    if not id or id == '':
        return render_template('search_init.html')
    values = {'title': id}
    try:
        public_json = fin(id)[0]
        public_dict = fin(id)[1]
        general = basic_info(id)
    except ValueError:
        return render_template('search_init.html', error="wrong_name",
                               values=values)

    if public_json == -2:
        return render_template('search_init.html', error="access_denied",
                               values=values)
    return render_template('infographics.html', values={}, public_json=public_json,
                           general=general, public_dict=public_dict)


@app.route("/")
def main():
    return render_template('search_init.html', active_page='home')


if __name__ == '__main__':
    app.run(debug=True)
