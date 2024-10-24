from flask import Flask, get_flashed_messages, jsonify, render_template, redirect, url_for, request, flash
from conexionBD import conectar_bd 
from py2neo import Graph, Node 
import os
import csv

ALLOWED_EXTENSIONS = {'txt','csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'


graph = conectar_bd()

#la página principal
@app.route('/')
def menu_principal():
    return render_template('menu_principal.html')


#CARGA DE DATOS
@app.route('/carga_datos')
def carga_datos():
    return render_template('carga_datos.html')

#CRUS
@app.route('/CRUD')
def CRUD():
    return render_template('CRUD.html')

#resultados
@app.route('/resultados')
def resultados():
    return render_template('resultados.html')


#Cargas archivo GEMINI_API_COMPETITION
@app.route('/carga_datos', methods=['POST'])
def cargar_Gemini_API():
    if 'Gemini' not in request.files:
        flash('No se ha seleccionado ningún archivo', 'danger')
        return redirect(url_for('carga_datos'))

    archivo = request.files['Gemini']

    if archivo.filename == '' or not archivo.filename.endswith('.csv'):
        flash('Archivo no válido. Por favor sube un archivo CSV.', 'danger')
        return redirect(url_for('carga_datos'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
    archivo.save(file_path)

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Titulo = row.get('Title')
                SubTitulo = row['Sub_Title']
                YouTubeLink = row['YouTube_Link']
                WhatItDoes = row['What_it_Does']
                BuiltWith = row['Built_With']
                By = row['By']     

                geminis = Node("Geminis", Title=Titulo, Sub_Title=SubTitulo,YouTube_Link= YouTubeLink, What_it_Does=WhatItDoes,
                               Built_With=BuiltWith)
                graph.create(geminis)

        flash('Geminis cargados exitosamente en la base de datos.', 'success')
    except Exception as e:
        flash(f'Error al procesar el archivo: {e}', 'danger')

    return redirect(url_for('carga_datos'))


@app.route('/agregar_nodo', methods=['POST'])
def agregar_nodo():
    title = request.form['title']
    Sub_Title = request.form['Sub_Title']
    YouTube_Link = request.form['YouTube_Link']
    What_it_Does = request.form['What_it_Does']
    Built_With = request.form['Built_With']
    By = request.form['By']
    Location = request.form['Location']
    Project_Link = request.form['Project_Link']

    try:
        query = """
        CREATE (g:Gemini {
            title: $title, 
            Sub_Title: $Sub_Title, 
            YouTube_Link: $YouTube_Link, 
            What_it_Does: $What_it_Does,
            Built_With: $Built_With,
            By: $By,
            Location: $Location,
            Project_Link: $Project_Link
        })
        """
        graph.run(query,title=title, Sub_Title=Sub_Title,YouTube_Link=YouTube_Link, What_it_Does=What_it_Does,
                  Built_With=Built_With, By=By, Location=Location, Project_Link= Project_Link)
        flash(f'Gemini {title} ha sido agregado exitosamente.', 'success')

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


