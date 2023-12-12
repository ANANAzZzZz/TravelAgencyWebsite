from app import app, db
import psycopg
from flask import render_template, url_for, request, flash, redirect
from flask_login import current_user, login_user, logout_user
from forms import RegistrationForm, LoginForm, ContractForm
from user import User
from werkzeug.security import check_password_hash


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        res = db.getUserByLogin(request.form['username'])

        if res is None or not check_password_hash(res[2], request.form['password']):
            flash('Неверное имя пользователя или пароль', 'error')
            return redirect(url_for('login'))

        ID, login, password = res
        user = User(ID, login, password)
        login_user(user, remember=login_form.remember_me.data)
        flash(f'Вы успешно авторизованы, {current_user.login}', 'success')

        return redirect(url_for('profile'))
    return render_template('login.html', title='Авторизация', form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        msg = db.addUser(request)

        flash(msg, 'primary')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Регистрация', form=reg_form)


@app.route('/profile')
def profile():
    user_client = db.getUserClient()
    return render_template('profile.html', title='Мой профиль', user_client=user_client)


@app.route('/conclude_contract', methods=['GET', 'POST'])
def conclude_contract():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    contract_form = ContractForm()

    if contract_form.validate_on_submit():
            db.addClient(request)
            flash('Контркат успешно заключен', 'success')

    return render_template('contract.html', title='Заключить контркат', form=contract_form)


@app.route('/hotels')
def hotels():
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
        hotel_names = cur.execute(f'SELECT name FROM hotel').fetchall()

    return render_template('hotels.html', title="Отели", hotel_names=hotel_names)
