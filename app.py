from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from logging import FileHandler

app = Flask(__name__)  # Corrected here
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # Corrected here
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if not title or not desc:
            flash('Title and description cannot be empty!', 'danger')
            return redirect('/')
        try:
            todo = Todo(title=title, desc=desc)
            db.session.add(todo)
            db.session.commit()
            flash('Todo item added successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error adding todo item: {e}")
            flash('An error occurred while adding the todo item.', 'danger')
        return redirect('/')
        
    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        if not title or not desc:
            flash('Title and description cannot be empty!', 'danger')
            return redirect(f'/update/{sno}')
        try:
            todo.title = title
            todo.desc = desc
            db.session.commit()
            flash('Todo item updated successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error updating todo item: {e}")
            flash('An error occurred while updating the todo item.', 'danger')
        return redirect('/')
        
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first_or_404()
    try:
        db.session.delete(todo)
        db.session.commit()
        flash('Todo item deleted successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error deleting todo item: {e}")
        flash('An error occurred while deleting the todo item.', 'danger')
    return redirect('/')

if __name__ == "__main__":  # Corrected here
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    # Set up logging to a file
    file_handler = FileHandler('error.log')
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)
    app.run(debug=True)
