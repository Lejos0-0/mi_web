import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Necesario para sessions

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Crear tabla users si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Llamar a init_db al iniciar la aplicación
init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return "El usuario ya existe"
        finally:
            conn.close()
    
    return render_template('register.html')

# Resto de tu aplicación...
