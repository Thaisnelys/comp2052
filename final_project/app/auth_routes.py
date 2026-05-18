from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms import LoginForm, RegisterForm
from app.models import db, User, Role
from flask_login import login_user, logout_user

# Blueprint de autenticación: gestiona login, registro y logout
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Inicia sesión de un usuario existente si las credenciales son válidas.
    """
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))

        flash('Invalid credentials')

    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    """
    Cierra la sesión del usuario.
    """
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registra un nuevo usuario y lo asocia por defecto al rol 'Usuario'.
    """    
    form = RegisterForm()
    
    if form.validate_on_submit():

        # Buscar el rol 'Usuario'
        role = Role.query.filter_by(name='Usuario').first()

        # Crear el usuario con el rol asignado
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=role
        )
        user.set_password(form.password.data)

        # Guardar en la base de datos
        db.session.add(user)
        db.session.commit()

        flash('User registered successfully.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

