from app import app, db
from flask import render_template, url_for, request, flash, redirect
from flask_login import current_user, login_user, logout_user
from forms import RegistrationForm, LoginForm, EditProfileForm, HotelsForm, HotelsEntryForm, ContractForm
from user import User
from werkzeug.security import check_password_hash


@app.route('/')
def index():
    routes = db.getRoutes()

    return render_template('index.html', routes=routes, title='Доступные туры')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        res = db.getUserByLogin(request.form['username'])

        if res is None or not check_password_hash(res[2], request.form['password']):
            flash('Неверное имя пользователя или пароль', 'error')
            return redirect(url_for('login'))

        id, login, password = res
        user = User(id, login, password)
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
        if not db.addUser(request):
            flash('Неудачная попытка регистрации !'
                  ' Пользователь с таким email/login уже зарегистрирован',
                  'danger')
            return redirect(url_for('register'))
        flash('Пользователь успешно зарегистрирован', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Регистрация', form=reg_form)


@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    user_client = db.getCurrUserClient()
    return render_template('profile.html', title='Мой профиль', user_client=user_client)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    edit_profile_form = EditProfileForm()
    client = db.getCurrUserClient()

    if request.method == 'GET':
        if client:
            edit_profile_form.phone_number.data = client[2]
            edit_profile_form.full_name.data = client[3]
            edit_profile_form.address.data = client[4]
            edit_profile_form.birth_date.data = client[5]

    if edit_profile_form.validate_on_submit():
        if client:
            db.updateClient(request)
        else:
            db.addClient(request)

        flash('Информация успешно обновлена', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', title='Редактировать профиль', form=edit_profile_form)


@app.route('/trips')
def trips():
    client_trips = db.getCurrClientTrips()

    return render_template('trips.html', title='Мои путевки', trips=client_trips)


@app.route('/contracts', methods=['GET', 'POST'])
def contracts():
    contract_form = ContractForm()
    res_contracts = db.getСurrClientContracts()

    if contract_form.validate_on_submit():
        if not db.addClientContract(request):
            flash('Для заключения контракта вам необходимо заполнить профиль', 'danger')

        return redirect(url_for('contracts'))

    return render_template('contracts.html',
                           title='Мои договоры', form=contract_form, contracts=res_contracts)


@app.route('/contract/<int:contract_id>')
def view_contract(contract_id):
    contract = db.getContractByID(contract_id)
    print(contract)

    return render_template('trips.html', contract=contract)


@app.route('/route/<int:route_id>')
def view_route(route_id):
    route = db.getRouteByID(route_id)
    stations = db.getStationsByRouteID(route_id)

    print(stations)

    return render_template('route.html', titile='Просмотр тура', route=route, stations=stations)


@app.route('/route/<int:route_id>/station/<int:station_id>', methods=['GET', 'POST'])
def view_station(route_id, station_id):
    if not current_user.is_authenticated:
        flash('Для конфигурирования путевки необходимо авторизоваться', 'danger')
        return redirect(url_for('login'))

    client = db.getCurrUserClient()
    if not client:
        flash('Для конфигурирования путевки необходимо заполнить профиль', 'danger')
        return redirect(url_for('profile'))

    return render_template('station.html', titile='Договоры')