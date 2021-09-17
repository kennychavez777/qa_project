#Set-ExecutionPolicy Unrestricted -Scope Process
#venv\Scripts\activate
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
import json

# Mysql connection
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'qa_project'
mysql = MySQL(app)

# Settings
app.secret_key = 'secretkey'
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/index')
def get_index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tb_usuarios WHERE correo=%s and password=%s', (email, password))
        user = cur.fetchall()
        session['user_id'] = user[0][0]
        session['user_name'] = user[0][1]
        cur.close()
        if user:
            return redirect(url_for('get_flows'))
        else:
            return 'No entro'

@app.route('/flows')
def get_flows():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_flujo')
    data = cursor.fetchall()
    cursor.close()
    return render_template('flows.html', flows = data)

@app.route('/my-incidences')
def get_my_incidences():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tbp.nombre as 'process_name', tbti.nombre as 'type', tbh.descripcion as 'description', tbu.nombre as 'user_name', tbh.fecha, tbh.gravedad FROM tb_historial tbh INNER JOIN tb_tipo_incidencia tbti ON tbh.id_tipo_incidencia = tbti.id_tipo_incidencia INNER JOIN tb_usuarios tbu ON tbh.id_usuario_creador = tbu.id_usuario INNER JOIN tb_procesos tbp ON tbh.id_proceso = tbp.id_proceso WHERE tbh.id_usuario_afectado = %s", [session['user_id']])
    created_incidences = cursor.fetchall()
    print(created_incidences)
    return render_template('created-incidences.html', incidences=created_incidences)

@app.route('/flow-detail/<id>', methods=['GET'])
def get_flow_detail(id):
    data = {}
    if id:
        cursor = mysql.connection.cursor()
        # Get flow data
        cursor.execute('SELECT * FROM tb_flujo WHERE id_flujo=%s', (id))
        flow = cursor.fetchall()
        
        # Get process data
        cursor.execute('SELECT * FROM tb_procesos WHERE id_flujo=%s', (id))
        processes = cursor.fetchall()
        
        # Get type
        cursor.execute('SELECT * FROM tb_tipo_incidencia')
        types = cursor.fetchall()
        
        cursor.close()

        data['flow'] = flow[0]
        data['processes'] = processes
        data['types'] = types
        
        return render_template('flow-detail.html', data = data)

@app.route('/get-usuarios', methods=['POST'])
def get_usuarios():
    id = request.get_json()['id']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_usuarios WHERE id_area = (SELECT id_area FROM `tb_procesos` WHERE id_proceso = %s)', [id])
    users = cursor.fetchall()
    cursor.close()
    return json.dumps(users)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return render_template('login.html')

@app.route('/save-history', methods=['POST'])
def save_history():
    if request.method == 'POST':
        id_proceso = request.form['id_proceso']
        id_usuario_afectado = request.form['id_usuario_afectado']
        id_tipo_incidencia = request.form['id_tipo_incidencia']
        descripcion = request.form['descripcion']
        gravedad = request.form['gravedad']
        id_usuario_creador = session['user_id']
        
        now = datetime.now()
        # dd/mm/YY H:M:S
        # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO tb_historial (id_tipo_incidencia, descripcion, id_proceso, fecha, id_usuario_creador, id_usuario_afectado, justificacion, estado, gravedad) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
        (id_tipo_incidencia, descripcion, id_proceso, dt_string, id_usuario_creador, id_usuario_afectado, None, 'creado', gravedad))
        mysql.connection.commit()

        return redirect(url_for('get_flows'))

@app.route('/created-incidences')
def get_created_incidences():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tbp.nombre as 'process_name', tbti.nombre as 'type', tbh.descripcion as 'description', tbu.nombre as 'user_name', tbh.fecha, tbh.gravedad FROM tb_historial tbh INNER JOIN tb_tipo_incidencia tbti ON tbh.id_tipo_incidencia = tbti.id_tipo_incidencia INNER JOIN tb_usuarios tbu ON tbh.id_usuario_afectado = tbu.id_usuario INNER JOIN tb_procesos tbp ON tbh.id_proceso = tbp.id_proceso WHERE id_usuario_creador = %s", [session['user_id']])
    created_incidences = cursor.fetchall()
    print(created_incidences)
    return render_template('created-incidences.html', incidences=created_incidences)

if __name__ == '__main__':
    app.run(port=3000, debug=True)