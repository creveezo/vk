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
    if request.method == 'POST':

        title = request.form['title']
        values = {'title': title}
        if not title:
            return render_template('search_init.html', error="no_title",
                                   values=values)
        try:
            public_json = fin(title)[0]
            public_dict = fin(title)[1]
            general = basic_info(title)
        except ValueError:
            return render_template('search_init.html', error="wrong_name",
                                   values=values)
        if public_json == -2:
            return render_template('search_init.html', error="access_denied",
                                   values=values)

        return render_template('infographics.html', values={}, public_json=public_json,
                               general=general, public_dict=public_dict)

    return render_template('search_init.html', values={})


@app.route("/")
def main():
    return render_template('search_init.html', active_page='home')


if __name__ == '__main__':
    app.run(debug=True)
