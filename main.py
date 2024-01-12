from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "\x82\xdc\x15\xc6\x179m\xbf}SxM7}\xb0o\xa2\x87\xfd\t;3\xf6\xc4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Book '{self.title}'>"


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<Member '{self.name}'>"


class Lend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)

    member = db.relationship('Member', backref=db.backref('lends', lazy=True))
    book = db.relationship('Book', backref=db.backref('lends', lazy=True))


# Create the database tables
def create_tables():
    db.create_all()


create_tables()


# Routes
@app.route('/')
def index():
    books = Book.query.all()
    members = Member.query.all()
    return render_template("index.html", books=books, members=members)


@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    quantity = request.form.get('quantity')
    new_book = Book(title=title, author=author, quantity=quantity)
    db.session.add(new_book)
    db.session.commit()
    flash('Book added successfully!')
    return redirect(url_for('index'))


@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form.get('name')
    email = request.form.get('email')
    new_member = Member(name=name, email=email)
    db.session.add(new_member)
    db.session.commit()
    flash('Member added successfully!')
    return redirect(url_for('index'))


@app.route('/lend_book', methods=['POST'])
def lend_book():
    member_id = request.form.get('member_id')
    book_id = request.form.get('book_id')
    due_date = request.form.get('due_date')
    lend = Lend(member_id=member_id, book_id=book_id, due_date=due_date)
    db.session.add(lend)
    db.session.commit()
    flash('Book lent successfully!')
    return redirect(url_for('index'))


@app.route('/return_book/<int:lend_id>', methods=['POST'])
def return_book(lend_id):
    lend = Lend.query.get_or_404(lend_id)
    db.session.delete(lend)
    db.session.commit()
    flash('Book returned successfully!')
    return redirect(url_for('index'))


# To edit and delete, you'll set up similar routes with appropriate forms and database operations.
# Routes for editing a book
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.quantity = request.form['quantity']
        db.session.commit()
        flash('Book updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)


# Route for deleting a book
@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!')
    return redirect(url_for('index'))


# Route for editing a member
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.email = request.form['email']
        db.session.commit()
        flash('Member updated successfully!')
        return redirect(url_for('index'))
    return render_template('edit_member.html', member=member)


# Route for deleting a member
@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    # Additional logic to ensure a member without lent books is deleted
    if member.lends:
        flash('Member cannot be deleted while they have lent books!')
        return redirect(url_for('index'))
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted successfully!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
