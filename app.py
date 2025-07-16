from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import uuid

app = Flask(__name__)

# Variables de entorno
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")           # X-Master-Key
JSONBIN_ACCESS_KEY = os.getenv("JSONBIN_ACCESS_KEY")     # X-Access-Key (para modificar bin)
BIN_ID = os.getenv("JSONBIN_BIN_ID")                     # ID del bin de recetas

HEADERS_BASE = {
    'Content-Type': 'application/json',
    'X-Master-Key': JSONBIN_API_KEY
}

def cargar_recetas():
    """Carga las recetas desde jsonbin.io usando el BIN_ID"""
    if not BIN_ID:
        return []

    url = f'https://api.jsonbin.io/v3/b/{BIN_ID}/latest'
    res = requests.get(url, headers=HEADERS_BASE)
    print(url)
    if res.status_code == 200:
        return res.json()['record']
    else:
        print(f"Error al cargar recetas: {res.status_code}")
        return []

def guardar_recetas(recetas):
    """Guarda la lista completa de recetas en jsonbin.io"""
    global BIN_ID

    url_base = 'https://api.jsonbin.io/v3/b'

    if not BIN_ID:
        # Crear nuevo bin (solo necesita master key)
        res = requests.post(url_base, headers=HEADERS_BASE, json=recetas)
        if res.status_code in (200, 201):
            BIN_ID = res.json()['metadata']['id']
            print(f"Nuevo BIN_ID creado: {BIN_ID}")
            return True
        else:
            print(f"Error al crear bin: {res.status_code} - {res.text}")
            return False
    else:
        # Actualizar bin existente (necesita access key)
        headers = HEADERS_BASE.copy()
        if JSONBIN_ACCESS_KEY:
            headers['X-Access-Key'] = JSONBIN_ACCESS_KEY

        url = f'{url_base}/{BIN_ID}'
        res = requests.put(url, headers=headers, json=recetas)
        if res.status_code == 200:
            return True
        else:
            print(f"Error al actualizar bin: {res.status_code} - {res.text}")
            return False

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
