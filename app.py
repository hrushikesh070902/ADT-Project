# app.py

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from extensions import db
from auth import authenticate

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret123"

    # Replace with your actual database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/medistockdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    # import models after db is initialized
    from models import (
        User, Item, Vendor, ItemVendor,
        SupplyRequest, Notification, Reorder
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email    = request.form['email']
            password = request.form['password']
            role     = request.form['role']

            if User.query.filter_by(email=email).first():
                flash('That email is already registered.', 'error')
                return redirect(url_for('register'))

            user = User(email=email, password=password, role=role)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email    = request.form['email']
            password = request.form['password']
            user     = authenticate(email, password)

            if user:
                login_user(user)
                return redirect(url_for('dashboard'))

            flash('Invalid credentials', 'error')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You've been logged out.", 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        role = current_user.role
        if role == 'Nurse':
            return redirect(url_for('nurse_dashboard'))
        if role == 'Doctor':
            return redirect(url_for('request_supplies'))
        if role == 'Manager':
            return redirect(url_for('manager_dashboard'))
        # Admin or other roles land here
        return render_template('dashboard.html', user=current_user)

    # ─── Admin: Add New Item ───────────────────────────────────────────
    @app.route('/add_item', methods=['GET', 'POST'])
    @login_required
    def add_item():
        if current_user.role != 'Admin':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            name        = request.form['name'].strip()
            stock_str   = request.form['stock'].strip()
            reorder_str = request.form['reorder_level'].strip()

            if not name:
                flash('Item name is required.', 'error')
                return redirect(url_for('add_item'))

            try:
                stock = int(stock_str)
                reorder_level = int(reorder_str)
            except ValueError:
                flash('Stock and reorder level must be integers.', 'error')
                return redirect(url_for('add_item'))

            if Item.query.filter_by(name=name).first():
                flash(f'An item named "{name}" already exists.', 'error')
                return redirect(url_for('add_item'))

            new_item = Item(name=name, stock=stock, reorder_level=reorder_level)
            db.session.add(new_item)
            db.session.commit()

            flash(f'Item "{name}" added successfully.', 'success')
            return redirect(url_for('dashboard'))

        return render_template('add_item.html', user=current_user)

    # ─── Admin: Manage Items ────────────────────────────────────────────
    @app.route('/manage_items')
    @login_required
    def manage_items():
        if current_user.role != 'Admin':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        items = Item.query.all()
        return render_template('manage_items.html', user=current_user, items=items)

    @app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
    @login_required
    def edit_item(item_id):
        if current_user.role != 'Admin':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        item = Item.query.get_or_404(item_id)
        if request.method == 'POST':
            name        = request.form['name'].strip()
            stock_str   = request.form['stock'].strip()
            reorder_str = request.form['reorder_level'].strip()

            if not name:
                flash('Name cannot be blank.', 'error')
                return redirect(url_for('edit_item', item_id=item_id))

            try:
                stock = int(stock_str)
                reorder_level = int(reorder_str)
            except ValueError:
                flash('Stock and reorder level must be integers.', 'error')
                return redirect(url_for('edit_item', item_id=item_id))

            item.name          = name
            item.stock         = stock
            item.reorder_level = reorder_level
            db.session.commit()

            flash(f'Item "{item.name}" updated.', 'success')
            return redirect(url_for('manage_items'))

        return render_template('edit_item.html', user=current_user, item=item)

    # ─── Admin: Manage Users ────────────────────────────────────────────
    @app.route('/manage_users')
    @login_required
    def manage_users():
        if current_user.role != 'Admin':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        users = User.query.all()
        return render_template('manage_users.html', user=current_user, users=users)

    @app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        if current_user.role != 'Admin':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        user_obj = User.query.get_or_404(user_id)
        if request.method == 'POST':
            email = request.form['email'].strip()
            role  = request.form['role']
            if not email:
                flash('Email cannot be blank.', 'error')
                return redirect(url_for('edit_user', user_id=user_id))
            user_obj.email = email
            user_obj.role  = role
            db.session.commit()
            flash('User updated.', 'success')
            return redirect(url_for('manage_users'))
        return render_template('edit_user.html', user=current_user, user_obj=user_obj)

    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if current_user.role != 'Admin':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        user_obj = User.query.get_or_404(user_id)
        db.session.delete(user_obj)
        db.session.commit()
        flash('User deleted.', 'info')
        return redirect(url_for('manage_users'))

    # ─── Common routes ─────────────────────────────────────────────────
    @app.route('/check_supplies')
    @login_required
    def check_supplies():
        inventory = Item.query.all()
        return render_template('check_supplies.html', user=current_user, inventory=inventory)

    @app.route('/use_item', methods=['POST'])
    @login_required
    def use_item():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False}), 400
        try:
            item_id  = int(data['item_id'])
            quantity = int(data['quantity'])
        except (KeyError, ValueError):
            return jsonify({'success': False}), 400
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'success': False}), 404
        item.stock = max(0, item.stock - quantity)
        db.session.commit()
        return jsonify({'success': True, 'new_stock': item.stock})

    @app.route('/nurse_dashboard')
    @login_required
    def nurse_dashboard():
        if current_user.role != 'Nurse':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        inventory     = Item.query.all()
        notifications = Notification.query.filter_by(user_id=current_user.user_id).all()
        return render_template(
            'nurse_dashboard.html',
            user=current_user,
            inventory=inventory,
            notifications=notifications
        )

    @app.route('/request_equipment')
    @login_required
    def request_equipment():
        return render_template('request_equipment.html', user=current_user)

    @app.route('/request_supplies')
    @login_required
    def request_supplies():
        items = Item.query.all()
        return render_template('request_supplies.html', user=current_user, items=items)

    @app.route('/submit_supply_request', methods=['POST'])
    @login_required
    def submit_supply_request():
        try:
            item_id  = int(request.form['item_id'])
            quantity = int(request.form['quantity'])
            reason   = request.form['reason'].strip()
        except (KeyError, ValueError):
            flash('Invalid request data.', 'error')
            return redirect(url_for('request_supplies'))
        req = SupplyRequest(
            user_id=current_user.user_id,
            item_id=item_id,
            quantity=quantity,
            reason=reason
        )
        db.session.add(req)
        db.session.commit()
        flash('Request submitted successfully!', 'success')
        return redirect(url_for('request_supplies'))

    @app.route('/manager_dashboard')
    @login_required
    def manager_dashboard():
        if current_user.role != 'Manager':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        pending = SupplyRequest.query.filter_by(status='Waiting for Approval').all()
        return render_template('manager_dashboard.html', user=current_user, requests=pending)

    @app.route('/handle_request_action', methods=['POST'])
    @login_required
    def handle_request_action():
        if current_user.role != 'Manager':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        try:
            req_id = int(request.form['request_id'])
            action = request.form['action']
        except (KeyError, ValueError):
            return redirect(url_for('manager_dashboard'))
        req = SupplyRequest.query.get(req_id)
        if req:
            req.status = 'Approved' if action == 'approved' else 'Not Approved'
            db.session.commit()
            item = Item.query.get(req.item_id)
            note = Notification(
                user_id=req.user_id,
                message=f"Your request for {item.name} was {req.status}."
            )
            db.session.add(note)
            db.session.commit()
            flash(f"Request {req.status}.", 'success')
        return redirect(url_for('manager_dashboard'))

    @app.route('/manager_history')
    @login_required
    def manager_history():
        if current_user.role != 'Manager':
            flash('Unauthorized', 'error')
            return redirect(url_for('dashboard'))
        history = SupplyRequest.query.filter(SupplyRequest.status != 'Waiting for Approval').all()
        return render_template('manager_history.html', user=current_user, requests=history)

    @app.route('/notifications')
    @login_required
    def notifications_page():
        notes = Notification.query.filter_by(user_id=current_user.user_id).all()
        return render_template('notifications.html', user=current_user, notifications=notes)

    @app.route('/clear_notifications', methods=['POST'])
    @login_required
    def clear_notifications():
        Notification.query.filter_by(user_id=current_user.user_id).delete()
        db.session.commit()
        flash('All notifications cleared.', 'info')
        return redirect(url_for('notifications_page'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
