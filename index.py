from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template, redirect, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS #pip install -U flask-cors
from correo import enviar_correo


app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'my_secret_key'

db = SQLAlchemy(app)

@dataclass
class Users(db.Model):
    id: int
    nombre: str
    apellido: str
    username: str
    correo: str
    password: str
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)
    apellido = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(60), nullable=False,unique=True)
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



@app.route('/users', methods=['GET', 'POST'])
def route_colors():
    if request.method == 'GET':
        color = Users.query.all()
        return jsonify(color)
    
    elif request.method == 'POST':
        color_data = request.get_json()
        color = Users(nombre=color_data['nombre'], apellido=color_data['apellido'],username=color_data['username'], correo=color_data['correo'], password = color_data['password'])
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
                'username':color.username,
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
            color.username = data['username']
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
        data = []
        for book in book:
            book_data = {
                "titulo": book.titulo,
                "descripcion": book.descripcion,
                "autor": book.autor,
                "precio": book.precio,
                "id"      : book.id,
                "id_category" : book.id_categoria }
            data.append(book_data)
        return jsonify(data)
    elif request.method == 'POST':
        book_data = request.get_json()
        user = Users.query.get(book_data['id_usuario'])
        
        autor = f"{user.nombre} {user.apellido}"

        book = Libros(
            id_usuario     = book_data['id_usuario'],
            id_categoria   = book_data['id_categoria'],
            titulo         = book_data['titulo'],
            autor          = autor,
            descripcion    = book_data['descripcion'],
            precio         = book_data['precio'],
            archivo_pdf    = book_data['archivo_pdf']
        )
        db.session.add(book)
        db.session.commit()
        return "SUCCESS"
    
@app.route('/books/<books_id>', methods=['GET'])
def route_books_id(books_id):
    if request.method == 'GET':
        book = Libros.query.filter_by(id=books_id).first()
        if book:
            result = {
                "titulo": book.titulo,
                "descripcion": book.descripcion,
                "autor": book.autor,
                "precio": book.precio,
                "id"      : book.id  }
            return jsonify(result)
    return "ERROR"

@app.route('/books/categorias/<books_id>', methods=['GET','PUT','DELETE'])
def route_books_category_id(books_id):
    if request.method == 'GET':
        book = Libros.query.filter_by(id_categoria=books_id).all()   
        data = []
        for book in book:
            book_data = {
                "titulo": book.titulo,
                "descripcion": book.descripcion,
                "autor": book.autor,
                "precio": book.precio,
                "id"      : book.id  }
            data.append(book_data)
        return jsonify(data)
    
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

@app.route('/categorias', methods=['GET','POST'])
def rout_categorias():
    if request.method == 'GET':
        categoria = Categorias.query.all()
        return jsonify(categoria)
    elif request.method == 'POST':
        data = request.get_json()
        categoria = Categorias(nombre=data['nombre'])
        db.session.add(categoria)
        db.session.commit()
        return "SUCCESS"

@app.route('/categorias/<id_categoria>', methods=['GET','DELETE','PUT'])
def route_categorias_id(id_categoria):
    if request.method == 'GET':
        book = Libros.query.filter_by(id=id_categoria).all()   
        data = []
        for book in book:
            book_data = {
                "id"          : book.id,
                "titulo"      : book.titulo,
                "descripcion" : book.descripcion,
                "autor"       : book.autor,
                "precio"      : book.precio}
            data.append(book_data)
        return jsonify(data)
    elif request.method == 'DELETE':
        book = Libros.query.filter_by(id=id_categoria).first()
        db.session.delete(book)
        db.session.commit()
        return "SUCCESS"



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(correo=data['correo']).first()
    if user and user.check_password(data['password']):
        session['id_usuario'] = user.id
        return jsonify({'id_usuario': user.id})
    else:
        flash('Invalid email or password', 'error')
        return "ERROR"


@app.route('/password/<password_correo>', methods=['GET'])
def password(password_correo):
    data = Users.query.filter_by(correo=password_correo).first()
    if data:
        # Crea el contenido del correo con la contraseña y el nombre de usuario
        contenido = f"Contraseña: {data.password}\nNombre de usuario: {data.username}"

        # Llama a la función enviar_correo con los datos correspondientes
        enviar_correo(password_correo, "Recuperación de cuenta", contenido)

        return jsonify(data.password)
    else:
        return "Correo no encontrado"



@app.route('/enviar_correo', methods=['POST'])
def enviar_correo_handler():
    data = request.get_json()
    print(data)
    
    correo = data.get('correo')
    password = data.get('password')
    username = data.get('username')

    # Crea el contenido del correo con la contraseña y el nombre de usuario
    contenido = f"Contraseña: {password}\nNombre de usuario: {username}"

    # Llama a la función enviar_correo con los datos correspondientes
    enviar_correo(correo, "Recuperacion de cueta", contenido)

    response = {
        'mensaje': 'Correo enviado correctamente',
        'correo': correo,
        'password': password,
        'username': username
    }

    return jsonify(response)




    
#import http.client
#name = http.client.HTTPConnection("127.0.0.1", 5000)

#name.request("GET","/players")
#response = name.getresponse()

#print("Response",response.read().decode())

#name.close()