from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'my_secret_key'

db = SQLAlchemy(app)

@dataclass
class Users(db.Model):
    id: int
    nombre: str
    apellido: str
    correo: str
    password: str

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)
    apellido = db.Column(db.String(60), nullable=False)
    correo = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<User {self.id}>'
    
    def check_password(self, password):
        return self.password == password

@dataclass
class Categorias(db.Model):
    id: int
    nombre: str

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)
    
    def __repr__(self):
        return f'<Categoria {self.id}>'

@dataclass
class Libros(db.Model):
    id: int
    id_usuario: int
    id_categoria: int
    titulo: str
    autor: str
    descripcion: str
    precio: float
    archivo_pdf: str

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    archivo_pdf = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Libro {self.id}>'

with app.app_context():
    db.create_all()


@app.route('/')
def menu():
    return render_template('signup.html')

@app.route('/menu.js')
def menu_js():
    return render_template('menu.js')

@app.route('/signup_menu')
def signup_menu():
    return render_template('signup.html')
@app.route('/signup.js')
def signup_js():
    return render_template('signup.js')

@app.route('/login.js')
def login_js():
    return render_template('login.js')
@app.route('/login_menu')
def login_menu():
    return render_template('login.html')

@app.route('/users', methods=['GET', 'POST'])
def route_colors():
    if request.method == 'GET':
        color = Users.query.all()
        return jsonify(color)
    
    elif request.method == 'POST':
        color_data = request.get_json()
        color = Users(nombre=color_data['nombre'], apellido=color_data['apellido'], correo=color_data['correo'], password = color_data['password'])
        db.session.add(color)
        db.session.commit()
        return "SUCCESS"

@app.route('/users/<users_id>', methods=['GET', 'PUT', 'DELETE'])
def route_users_id(users_id):
    if request.method == 'GET':
        color = Users.query.filter_by(id=users_id).first()
        if color:
            result = {
                'id': color.id,
                'nombre': color.nombre,
                'apellido': color.apellido,
                'correo': color.correo,
                'password':color.password
            }
            return jsonify(result)
        else:
            return "ERROR"
    
    elif request.method == 'DELETE':
        color = Users.query.filter_by(id=users_id).first()
        if color:
            db.session.delete(color)
            db.session.commit()
            return "SUCCESS"
        else:
            return "ERROR"
    
    elif request.method == 'PUT':
        data = request.get_json()
        color = Users.query.filter_by(id=users_id).first()
        if color:
            color.nombre = data['nombre']
            color.apellido = data['apellido']
            color.correo = data['correo']
            color.password = data['password']
            db.session.commit()
            return "SUCCESS"
        else:
            return "ERROR"
        
@app.route('/books', methods=['GET', 'POST'])
def route_books():
    if request.method == 'GET':
        book = Libros.query.all()
        return jsonify(book)
    elif request.method == 'POST':
        book_data = request.get_json()
        user = Users.query.get(book_data['id_usuario'])
        autor = f"{user.nombre} {user.apellido}"
        book = Libros(
            id_usuario=book_data['id_usuario'],
            id_categoria=book_data['id_categoria'],
            titulo=book_data['titulo'],
            autor=autor,
            descripcion=book_data['descripcion'],
            precio=book_data['precio'],
            archivo_pdf=book_data['archivo_pdf']
        )
        db.session.add(book)
        db.session.commit()
        return "SUCCESS"
@app.route('/books/<books_id>', methods=['GET','PUT','DELETE'])
def route_books_id(books_id):
    if request.method == 'GET':
        book = Libros.query.get(books_id)
        return jsonify(book)
    elif request.method == 'DELETE':
        book = Libros.query.filter_by(id=books_id).first()
        db.session.delete(book)
        db.session.commit()
        return "SUCCESS"
    elif request.method == 'PUT':
        data = request.get_json()
        book = Libros.query.filter_by(id=books_id).first()
        
        if book:
            book.id_usuario = data.get('id_usuario')
            book.id_categoria = data.get('id_categoria')
            book.titulo = data.get('titulo')
            book.descripcion = data.get('descripcion')
            book.precio = data.get('precio')
            book.archivo_pdf = data.get('archivo_pdf')
            
            user = Users.query.get(data['id_usuario'])
            
            if user:
                book.autor = f"{user.nombre} {user.apellido}"
            
            db.session.commit()
            return "SUCCESS"
        else:
            return "ERROR"



@app.route('/pagina')
def pagina():
    return render_template('pagina.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    player = Users.query.filter_by(correo=data["correo"]).first()
    if player and player.check_password(data["password"]):
        return redirect('/pagina')
    else:
        flash('Invalid email or password', 'error')
        return render_template('login.html')