from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import uuid

app = Flask(__name__)

JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")
BIN_ID = os.getenv("JSONBIN_BIN_ID")  

HEADERS = {
    'Content-Type': 'application/json',
    'X-Master-Key': JSONBIN_API_KEY
}

def cargar_recetas():
    """Carga las recetas desde jsonbin.io usando el BIN_ID"""
    if not BIN_ID:
        return []

    url = f'https://api.jsonbin.io/v3/bins/{BIN_ID}/latest'
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        return res.json()['record']
    else:
        return []

def guardar_recetas(recetas):
    """Guarda la lista completa de recetas en jsonbin.io"""
    global BIN_ID

    url_base = 'https://api.jsonbin.io/v3/bins'

    if not BIN_ID:
        # Crear nuevo bin
        res = requests.post(url_base, headers=HEADERS, json=recetas)
        if res.status_code in (200, 201):
            BIN_ID = res.json()['metadata']['id']
            print(f"Nuevo BIN_ID creado: {BIN_ID}")
            # IMPORTANTE: debes actualizar esta variable de entorno JSONBIN_BIN_ID en tu entorno o en Render manualmente
            return True
        else:
            return False
    else:
        # Actualizar bin existente (PUT)
        url = f'{url_base}/{BIN_ID}'
        res = requests.put(url, headers=HEADERS, json=recetas)
        return res.status_code == 200

@app.route('/')
def index():
    recetas = cargar_recetas()
    busqueda = request.args.get('busqueda', '').lower()

    if busqueda:
        recetas = [r for r in recetas if busqueda in r['titulo'].lower()]

    return render_template('index.html', recetas=recetas)

@app.route('/receta/<receta_id>')
def ver_receta(receta_id):
    recetas = cargar_recetas()
    receta = next((r for r in recetas if r['id'] == receta_id), None)
    if receta is None:
        return "Receta no encontrada", 404
    return render_template('ver_receta.html', receta=receta)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        ingredientes = request.form['ingredientes']
        pasos = request.form['pasos']

        receta = {
            'id': str(uuid.uuid4()),
            'titulo': titulo,
            'ingredientes': ingredientes.split('\n'),
            'pasos': pasos.split('\n')
        }

        recetas = cargar_recetas()
        recetas.append(receta)
        if guardar_recetas(recetas):
            return redirect(url_for('index'))
        else:
            return "Error al guardar receta en jsonbin", 500

    return render_template('agregar.html')

@app.route('/borrar/<receta_id>', methods=['GET'])
def borrar(receta_id):
    recetas = cargar_recetas()
    recetas = [r for r in recetas if r['id'] != receta_id]
    if guardar_recetas(recetas):
        return redirect(url_for('index'))
    else:
        return "Error al borrar receta en jsonbin", 500


if __name__ == '__main__':
    app.run(debug=True)
