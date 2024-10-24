from flask import Flask, get_flashed_messages, jsonify, render_template, redirect, url_for, request, flash
from conexionBD import conectar_bd 
from py2neo import Graph, Node 
import os
import csv

ALLOWED_EXTENSIONS = {'txt','csv', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

graph = conectar_bd()

#la página principal
@app.route('/')
def menu_principal():
    return render_template('menu_principal.html')


#CARGA DE DATOS
@app.route('/carga_datos')
def carga_datos():
    return render_template('carga_datos.html')

#Borrar base de datos     LISTO
@app.route('/borrar_base_datos', methods=['POST'])
def borrar_base_datos():
    try:
        query = """
        MATCH (n) DETACH DELETE n
        """
        graph.run(query)
        flash('La BASE DE DATOS ha sido eliminada exitosamente.', 'success') #aqui no me esta funcionando el mensaje

    except Exception as e:
        flash(f'Error al agregar evento: {e}', 'danger')

    return redirect(url_for('carga_datos'))



#Cargas archivo GEMINI_API_COMPETITION
@app.route('/cargar_Gemini_API', methods=['POST'])
def cargar_Gemini_API():
    if 'Gemini' not in request.files:
        flash('No se ha seleccionado ningún archivo', 'danger')
        return redirect(url_for('carga_datos'))

    archivo = request.files['Gemini']
#   print(archivo)

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
        archivo.save(file_path)
        print(f'Archivo guardado correctamente en {file_path}') 
    except Exception as e:
        print(f'Error al guardar el archivo: {e}')
        flash(f'Error al guardar el archivo: {e}', 'danger')
        return redirect(url_for('carga_datos'))

    try:
        print("Entro al try")
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            print("Entro al with")
            
            reader = csv.DictReader(csvfile)
            print(reader)
            #creo el nodito de Tecnologias
            for row in reader:
                Title = row.get('Title', '')
                What_it_Does = row.get('What it Does', '')  # Nombre correcto de la columna según tu ejemplo
                Built_With = row.get('Built With', '')      # Asegúrate de que estos nombres coinciden con el archivo CSV
            
                #print(f"Procesando What_it_Does: {What_it_Does}, Built_With: {Built_With}")
            
                tecnologias = Node("Tecnologias",Title=Title, What_it_Does=What_it_Does, Built_With=Built_With)
                graph.create(tecnologias)
                
            #creo el nodito de Aplicaciones            
            for row in reader:
                Title = row.get('Title', '')  # Usar 'get' en lugar de indexación directa para evitar errores
                Built_With = row.get('Built With', '')
                By = row.get('By', '')
                print(f"Procesando Aplicaciones - Title: {Title}, Built_With: {Built_With}, By: {By}")
                aplicaciones = Node("Aplicaciones", Title=Title, Built_With=Built_With, By=By)
                graph.create(aplicaciones)

            #creo el nodito de Creadores
            for row in reader:
                Title = row.get('Title', '')
                By = row.get('By', '')
                print(f"Procesando Creadores - Title: {Title}, By: {By}")
                creadores = Node("Creadores", Title=Title, By=By)
                graph.create(creadores) 
        

            
        flash('Nodos cargados exitosamente en la base de datos.', 'success')
    except Exception as e:
        print("Creo que entro aqui al except")
        flash(f'Error al procesar el archivo: {e}', 'danger')

    return redirect(url_for('carga_datos'))



@app.route('/agregar_nodo_aplicaciones', methods=['POST'])
def agregar_nodo_aplicaciones():
    title = request.form['title']
    What_it_Does = request.form['What_it_Does']
    Built_With = request.form['Built_With']
    try:
        query = """
        CREATE (g:Gemini {
            title: $title, 
            What_it_Does: $What_it_Does,
            Built_With: $Built_With,
        })
        """
        graph.run(query,title=title,What_it_Does=What_it_Does,
                  Built_With=Built_With)
        flash(f'Gemini {title} ha sido agregado exitosamente.', 'success') #aqui no me esta funcionando el mensaje

    except Exception as e:
        flash(f'Error al agregar evento: {e}', 'danger')

    return redirect(url_for('CRUD'))

@app.route('/editar_nodo', methods=['POST'])
def editar_nodo():
    pass


@app.route('/leer_nodo', methods=['POST'])
def leer_nodo():
    pass

@app.route('/borrar_nodo', methods=['POST'])
def borrar_nodo():
    pass



if __name__ == '__main__':
    app.run(debug=True, port=8080)


