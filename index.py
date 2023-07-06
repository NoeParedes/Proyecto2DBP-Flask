from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template, redirect, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS #pip install -U flask-cors
from correo import enviar_correo
from date import today_date
from sqlalchemy import or_

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

@dataclass
class Compras(db.Model):
    id      : int
    user_id : int
    autor   : str
    title   : str
    price   : float
    day     : str
    hour    : str

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    autor   = db.Column(db.String(100), nullable=False)
    title   = db.Column(db.String(100), nullable=False)
    price   = db.Column(db.Float, nullable=False)
    day     = db.Column(db.String(20), nullable=False)
    hour    = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Compras {self.id}>'

with app.app_context():
    db.create_all()


@app.route('/users', methods=['GET', 'POST'])
def route_users():
    if request.method == 'GET':
        users = Users.query.all()
        return jsonify(users)
    elif request.method == 'POST':
        color_data = request.get_json()
        color = Users(nombre=color_data['nombre'],
                      apellido=color_data['apellido'],
                      username=color_data['username'],
                      correo=color_data['correo'],
                      password = color_data['password'])
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
                "titulo"      : book.titulo,
                "descripcion" : book.descripcion,
                "autor"       : book.autor,
                "precio"      : book.precio,
                "id"          : book.id,
                "id_category" : book.id_categoria,
                "id_usuario"  : book.id_usuario,
                "archivo_pdf" : book.archivo_pdf }
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
    
@app.route('/books/<books_id>', methods=['GET','PUT'])
def route_books_id(books_id):
    if request.method == 'GET':
        book = Libros.query.filter_by(id=books_id).first()
        book_data = {
            "titulo"      : book.titulo,
            "descripcion" : book.descripcion,
            "autor"       : book.autor,
            "precio"      : book.precio,
            "id"          : book.id,
            "id_category" : book.id_categoria,
            "id_usuario"  : book.id_usuario,
            "archivo_pdf" : book.archivo_pdf }
        return jsonify(book_data)
    elif request.method == 'PUT':
        data = request.get_json()
        book = Libros.query.get_or_404(books_id)
        if book:
            book.id_usuario   = data['id_usuario']
            book.id_categoria = data['id_category']
            book.titulo       = data['titulo']
            book.descripcion  = data['descripcion']
            book.precio       = data['precio']
            book.archivo_pdf  = data['archivo_pdf']
            book.autor        = data['autor']
            db.session.commit()
            return "SUCCESS"
        return "SUCCESS"

@app.route('/books/usuario/<id>', methods=['GET'])
def route_books_user_id(id):
    if request.method == 'GET':
        book = Libros.query.filter_by(id_usuario=id).all()   
        data = []
        for book in book:
            book_data = {
                "titulo"      : book.titulo,
                "descripcion" : book.descripcion,
                "autor"       : book.autor,
                "precio"      : book.precio,
                "id"          : book.id,
                "archivo_pdf" : book.archivo_pdf}
            data.append(book_data)
        return jsonify(data)
    return "ERROR"

@app.route('/books/categorias/<books_id>', methods=['GET','PUT','DELETE'])
def route_books_category_id(books_id):
    if request.method == 'GET':
        book = Libros.query.filter_by(id_categoria=books_id).all()   
        data = []
        for book in book:
            book_data = {
                "titulo"      : book.titulo,
                "descripcion" : book.descripcion,
                "autor"       : book.autor,
                "precio"      : book.precio,
                "id"          : book.id,
                "id_category" : book.id_categoria,
                "id_usuario"  : book.id_usuario,
                "archivo_pdf" : book.archivo_pdf }
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
            book['id_usuario'] = data.get('id_usuario')
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

@app.route('/compras', methods=['GET','POST','DELETE'])
def route_compra():
    if request.method == 'GET':
        compras = Compras.query.all()
        response = []
        for compra in compras:
            data = {
                'id'     : compra.id,
                'user_id': compra.user_id,
                'autor'  : compra.autor,
                'title'  : compra.title,
                'price'  : compra.price,
                'day'    : compra.day,
                'hour'   : compra.hour}
            response.append(data)
        return jsonify(response)
    elif request.method == 'POST':
        data = request.get_json()
        now  = today_date()
        compra = Compras(
            user_id = data['user_id'],
            autor   = data['autor'],
            title   = data['title'],
            price   = data['price'],
            day     = now['day'],
            hour    = now['hour'])
        db.session.add(compra)
        db.session.commit()
        return "SUCCESS"
    elif request.method == 'DELETE':
        db.session.query(Compras).delete()
        db.session.commit()
        return "SUCCESS"

@app.route('/compras/usuario/<id>', methods=['GET'])
def route_compra_by_user(id):
    if request.method == 'GET':
        compras = Compras.query.filter_by(user_id=id).all()   
        result = []
        for compra in compras:
            data = {
                "id"      : compra.id,
                "user_id" : compra.user_id,
                "autor"   : compra.autor,
                "title"   : compra.title,
                "price"   : compra.price,
                "day"     : compra.day,
                "hour"    : compra.hour }
            result.append(data)
        return jsonify(result)

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


@app.route('/users/login', methods=['POST'])
def check_valid_user():
    data = request.get_json()
    user = Users.query.filter(or_(Users.correo==data['correo'], Users.username==data['correo'])).first()
    if user:
        if user.check_password(data['password']):
            return jsonify(user)
        return jsonify({'ERROR': "Incorrect password"})
    return jsonify({'ERROR': "Unregistered user"})

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

if __name__ == '__main__':
    app.run()
