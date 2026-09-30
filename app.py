import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DB_FILE = 'tetris_scores.db'

def init_db():
    if not os.path.exists(DB_FILE):
        print("Creando base de datos inicial con Pandas...")
        initial_data = {
            'id': [1, 2],
            'nombre': ['Jugador 1', 'Jugador 2'],
            'max_puntuacion': [0, 0]
        }
        df = pd.DataFrame(initial_data)
        conn = sqlite3.connect(DB_FILE)
        df.to_sql('perfiles', conn, if_exists='replace', index=False)
        conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/perfiles', methods=['GET'])
def get_perfiles():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM perfiles", conn)
    conn.close()
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/perfil/renombrar', methods=['POST'])
def renombrar_perfil():
    data = request.json
    player_id = int(data.get('id'))
    nuevo_nombre = str(data.get('nombre')).strip()

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM perfiles", conn)
    df.loc[df['id'] == player_id, 'nombre'] = nuevo_nombre
    df.to_sql('perfiles', conn, if_exists='replace', index=False)
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/puntuacion', methods=['POST'])
def guardar_puntuacion():
    data = request.json
    player_id = int(data.get('id'))
    score = int(data.get('score'))

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM perfiles", conn)
    current_max = df.loc[df['id'] == player_id, 'max_puntuacion'].values[0]
    
    nuevo_record = False
    if score > current_max:
        df.loc[df['id'] == player_id, 'max_puntuacion'] = score
        df.to_sql('perfiles', conn, if_exists='replace', index=False)
        nuevo_record = True
        
    conn.close()
    return jsonify({"status": "success", "nuevo_record": nuevo_record})

if __name__ == '__main__':
    app.run(debug=True, port=5000)