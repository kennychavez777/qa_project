#Set-ExecutionPolicy Unrestricted -Scope Process
#venv\Scripts\activate
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
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

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        cursor = mysql.connection.cursor() 
        cursor.execute('INSERT INTO contacts (nombre, phone, email) VALUES (%s, %s, %s)', (fullname, phone, email))
        mysql.connection.commit()
        
        return redirect(url_for('index'))

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
        print(session)
        cur.close()
        if user:
            return redirect(url_for('get_flows'))
        else:
            return 'No entro'

@app.route('/edit')
def edit_contact():
    return 'edit'

@app.route('/delete')
def delete_contact():
    return 'delete'

@app.route('/dashboard')
def get_dashboard():
    return render_template('dashboard.html')

@app.route('/flows')
def get_flows():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM tb_flujo')
    data = cursor.fetchall()
    cursor.close()
    return render_template('flows.html', flows = data)

@app.route('/my-incidences')
def get_my_incidences():
    return render_template('my-incidences.html')

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

# @app.route('/save-history', methods=['POST'])
# def save_history():
#     if request.method == 'POST':
#         fullname = request.form['fullname']
#         phone = request.form['phone']
#         email = request.form['email']

if __name__ == '__main__':
    app.run(port=3000, debug=True)