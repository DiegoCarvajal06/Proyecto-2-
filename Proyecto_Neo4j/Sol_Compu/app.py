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

def crear_restricciones():
    try:
        # Restricción de unicidad para Aplicaciones (campo Title)
        graph.run("CREATE CONSTRAINT aplicaciones_title_unique IF NOT EXISTS ON (a:Aplicaciones) ASSERT a.Title IS UNIQUE;")
        
        # Restricción de unicidad para Tecnologías (campo Built_With)
        graph.run("CREATE CONSTRAINT tecnologias_whatitdoes_unique IF NOT EXISTS ON (t:Tecnologias) ASSERT t.Built_With IS UNIQUE;")
        
        # Restricción de unicidad para Creadores (campo By)
        graph.run("CREATE CONSTRAINT creadores_by_unique IF NOT EXISTS ON (c:Creadores) ASSERT c.By IS UNIQUE;")
        
        print("Restricciones creadas correctamente.")
    except Exception as e:
        print(f"Error al crear restricciones: {e}")

#crear_restricciones()

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
                #Title = row.get('Title', '')
                #What_it_Does = row.get('What it Does', '')  # Nombre correcto de la columna según tu ejemplo
                Built_With = row.get('Built With', '')      # Asegúrate de que estos nombres coinciden con el archivo CSV
                #By = row.get('By', '')
                #print(f"Procesando What_it_Does: {What_it_Does}, Built_With: {Built_With}")
                if not graph.evaluate(f"MATCH (t:Tecnologias {{Built_With: '{Built_With}'}}) RETURN t"):
                    try:
                        tecnologias = Node("Tecnologias", Built_With=Built_With)
                        graph.create(tecnologias)
                    except Exception as e:
                        flash(f'Error al crear nodo de Tecnologías: {e}', 'danger')
                else:
                    print(f"El nodo con Built_With '{Built_With}' ya existe. No se creará un duplicado.")

        #vuelvo abrir el archivo       
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            print("Procesando Aplicaciones")
            reader = csv.DictReader(csvfile)      
            #creo el nodito de Aplicaciones            
            for row in reader:
                Title = row.get('Title', '')  # descripcion
                Built_With = row.get('Built With', '')
                By = row.get('By', '')
                print(f"Procesando Aplicaciones - Title: {Title}, Built_With: {Built_With}, By: {By}")

                if not graph.evaluate(f"MATCH (a:Aplicaciones {{Title: '{Title}'}}) RETURN a"):
                    try:
                        aplicaciones = Node("Aplicaciones", Title=Title, Built_With=Built_With, By=By)
                        graph.create(aplicaciones)
                    except Exception as e:
                        flash(f'Error al crear nodo de Aplicaciones: {e}', 'danger')
                else:
                    print(f"El nodo de Aplicaciones con Title '{Title}' ya existe. No se creará un duplicado.")


        #vuelvo abror el archivo para procesarlo.                 
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            print("Procesando Creadores")
            reader = csv.DictReader(csvfile)
            #creo el nodito de Creadores
            for row in reader:
                Title = row.get('Title', '')
                By = row.get('By', '')

                print(f"Procesando Creadores - Title: {Title}, By: {By}")
                if not graph.evaluate(f"MATCH (c:Creadores {{By: '{By}'}}) RETURN c"):
                    try:
                        creadores = Node("Creadores", Title=Title, By=By)
                        graph.create(creadores)
                    except Exception as e:
                        flash(f'Error al crear nodo de Creadores: {e}', 'danger')
                else:
                    print(f"El nodo con By '{By}' ya existe. No se creará un duplicado.")
            
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


