from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = 'data/recetas.json'

# Cargar recetas del archivo JSON
def cargar_recetas():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Guardar recetas en el archivo JSON
def guardar_recetas(recetas):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(recetas, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    recetas = cargar_recetas()
    busqueda = request.args.get('busqueda', '').lower()

    if busqueda:
        recetas = [r for r in recetas if busqueda in r['titulo'].lower()]

    return render_template('index.html', recetas=recetas)


@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        ingredientes = request.form['ingredientes']
        pasos = request.form['pasos']

        receta = {
            'id': str(len(cargar_recetas()) + 1),
            'titulo': titulo,
            'ingredientes': ingredientes.split('\n'),
            'pasos': pasos.split('\n')
        }

        recetas = cargar_recetas()
        recetas.append(receta)
        guardar_recetas(recetas)
        return redirect(url_for('index'))
    return render_template('agregar.html')

@app.route('/borrar/<receta_id>')
def borrar(receta_id):
    recetas = cargar_recetas()
    recetas = [r for r in recetas if r['id'] != receta_id]
    guardar_recetas(recetas)
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)
