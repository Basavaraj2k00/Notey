from flask import Flask, render_template, redirect, url_for, flash, abort, request

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
load_dotenv()
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.sql import func
from forms import LoginForm, RegisterForm
from datetime import datetime
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///todo.db")
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)




login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    content = db.Column(db.String(10000))
    date = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    notes = db.relationship('Note')


db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    # notes = Note.query.order_by(Note.date.desc()).all()

    if request.method == "POST":
        date = datetime.now().strftime('%d-%B-%Y %H:%M')
        new_data = Note(
            title=request.form['title'].title(),
            content=request.form['content'],
            date=date,
            user_id=current_user.id
        )
        # print(len(request.form['content']))
        db.session.add(new_data)
        db.session.commit()

    notes = db.session.query(Note).all()

    return render_template('notes.html', notes=notes, user=current_user)


@app.errorhandler(401)
def resource_not_found(e):
    return render_template('401.html', error=e), 401


@app.errorhandler(404)
def resource_not_found(e):
    return render_template('404.html', error=e), 404


@app.route("/notes/delete")
def delete():
    note_id = request.args.get('id')

    # DELETE A RECORD BY ID
    note_to_delete = Note.query.get(note_id)
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for('notes'))


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!", category="warning")
            return redirect(url_for('login'))

        else:

            new_user = User(
                email=form.email.data,
                password=generate_password_hash(
                    form.password.data, method='pbkdf2:sha256', salt_length=8),
                name=form.name.data.title()
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)

            flash("Successfully Registerd ", category="info")
            return redirect(url_for("notes"))
    return render_template("register.html", form=form, user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.", category="error")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', category="error")
            return redirect(url_for('login'))
        else:
            login_user(user, remember=True)

            return redirect(url_for("notes"))

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# @app.route('/register',methods=['GET','POST'])
# def register():
#     form = RegisterForm()
#     form.validate_on_submit
#     return render_template('register.html',form=form)

# @app.route('/login',methods=['GET','POST'])
# def login():
#     form = LoginForm()
#     return render_template('login.html',form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # app.run(host='127.0.0.1', port=8000, debug=True)
