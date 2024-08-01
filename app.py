from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = "1"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)

    db.create_all()
    return render_template('register.html')
@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    taskskol=Task.query.filter_by(user_id=current_user.id).count()
    return render_template('index.html', tasks=tasks, taskskol=taskskol)

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    if title:
        new_task = Task(title=title, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!')
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)

    if task and task.user_id == current_user.id:
        task.title = request.form.get('title')
        db.session.commit()
        flash('Task updated successfully!')
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    title = request.form.get('title')
    print(title)
    if task and task.user_id == current_user.id:
        task.completed = True
        db.session.commit()
        flash('Task marked as completed!')
    if title:
        task.completed = True
        db.session.commit()
        flash('Task marked as completed!')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!')
    return redirect(url_for('index'))

@app.route('/delete_all', methods=['POST'])
@login_required
def delete_all_tasks():
    Task.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('All tasks deleted successfully!')
    return redirect(url_for('index'))

@app.route('/filter/<status>')
@login_required
def filter_tasks(status):
    if status == 'completed':
        tasks = Task.query.filter_by(completed=True, user_id=current_user.id).all()
        taskskol=Task.query.filter_by(completed=True, user_id=current_user.id).count()
    elif status == 'open':
        tasks = Task.query.filter_by(completed=False, user_id=current_user.id).all()
        taskskol = Task.query.filter_by(completed=False, user_id=current_user.id).count()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        taskskol = Task.query.filter_by(user_id=current_user.id).count()

    return render_template('index.html', tasks=tasks, taskskol=taskskol)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
##
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))

        flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


app.run(debug=True)

print("GG")