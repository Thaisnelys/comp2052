from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.forms import ItemForm, ChangePasswordForm
from app.models import db, Item, User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Current password is incorrect.')
            return render_template('cambiar_password.html', form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password updated successfully.')
        return redirect(url_for('main.dashboard'))

    return render_template('cambiar_password.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role.name == 'Usuario':
        items = Item.query.filter_by(usuario_id=current_user.id).limit(5).all()
    else:
        items = Item.query.limit(5).all()

    return render_template('dashboard.html', items=items)

# =========================
# ITEMS
# =========================

@main.route('/items')
@login_required
def listar_items():
    if current_user.role.name == 'Usuario':
        items = Item.query.filter_by(usuario_id=current_user.id).all()
    else:
        items = Item.query.all()

    return render_template('items.html', items=items)

@main.route('/items/new', methods=['GET', 'POST'])
@login_required
def crear_item():
    form = ItemForm()

    if form.validate_on_submit():
        item = Item(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            cantidad=form.cantidad.data,
            usuario_id=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash("Item created.")
        return redirect(url_for('main.listar_items'))

    return render_template('item_form.html', form=form)

@main.route('/items/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def editar_item(id):
    item = Item.query.get_or_404(id)

    if current_user.role.name != 'Admin' and item.usuario_id != current_user.id:
        flash('You cannot edit this item.')
        return redirect(url_for('main.listar_items'))

    form = ItemForm(obj=item)

    if form.validate_on_submit():
        item.nombre = form.nombre.data
        item.descripcion = form.descripcion.data
        item.cantidad = form.cantidad.data
        db.session.commit()
        flash("Item updated.")
        return redirect(url_for('main.listar_items'))

    return render_template('item_form.html', form=form, editar=True)

@main.route('/items/<int:id>/delete', methods=['POST'])
@login_required
def eliminar_item(id):
    item = Item.query.get_or_404(id)

    if current_user.role.name != 'Admin' and item.usuario_id != current_user.id:
        flash('You cannot delete this item.')
        return redirect(url_for('main.listar_items'))

    db.session.delete(item)
    db.session.commit()
    flash("Item deleted.")
    return redirect(url_for('main.listar_items'))

# =========================
# USUARIOS
# =========================

@main.route('/usuarios')
@login_required
def listar_usuarios():
    if current_user.role.name != 'Admin':
        flash("You cannot view this page.")
        return redirect(url_for('main.dashboard'))

    usuarios = User.query.join(User.role).all()
    return render_template('usuarios.html', usuarios=usuarios)
