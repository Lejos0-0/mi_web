from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura'  # Cambia esto por una clave aleatoria fuerte

# Configuración de la base de datos
DATABASE = '/home/Eremarmolejos/mi_web/database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Crear tabla de sesiones (opcional)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()

# Inicializar la base de datos al iniciar
init_db()

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        
        # Validación básica
        if not username or not password:
            flash('Username y password son requeridos')
            return redirect(url_for('register'))
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                flash('El usuario ya existe')
                return redirect(url_for('register'))
            
            # Hash del password
            hashed_password = generate_password_hash(password)
            
            # Insertar nuevo usuario
            cursor.execute(
                'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                (username, hashed_password, email)
            )
            conn.commit()
            flash('Registro exitoso! Por favor inicia sesión')
            return redirect(url_for('login'))
            
        except sqlite3.Error as e:
            flash(f'Error de base de datos: {str(e)}')
            return redirect(url_for('register'))
            
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar usuario en la base de datos
            cursor.execute(
                'SELECT id, username, password FROM users WHERE username = ?', 
                (username,)
            )
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Inicio de sesión exitoso!')
                return redirect(url_for('home'))
            else:
                flash('Usuario o contraseña incorrectos')
                
        except sqlite3.Error as e:
            flash(f'Error de base de datos: {str(e)}')
            
        finally:
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True