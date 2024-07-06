from flask import Flask, render_template, request,redirect, send_from_directory
from flask_mysqldb import MySQL
from datetime import datetime 
import os

# Creamos la aplicación
app = Flask(__name__) 

# Creamos la conexión con la base de datos:
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'colegio'

# Inicializamos la extensión MySQL
mysql = MySQL(app)

# Guardamos la ruta de la carpeta "uploads" en nuestra app
CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA
#--------------------------------------------------------------------
# Generamos el acceso a la carpeta uploads. 
# El método uploads que creamos nos dirige a la carpeta (variable CARPETA)
# y nos muestra la foto guardada en la variable nombreFoto.
@app.route('/uploads/<fotoalumno>')
def uploads(fotoalumno):
 return send_from_directory(app.config['CARPETA'], fotoalumno)
#--------------------------------------------------------------------
# Proporcionamos la ruta a la raíz del sitio

@app.route('/')
def inicio():
    return render_template('colegio/landing.html')

#***********************************************************************************
#VERIFICAR DATOS DEL INICIO DE SESION. 
@app.route('/iniciarsesion')
def consultar():
    return render_template('colegio/iniciosesion.html')  

#ruta para consultar si el usuario que inicia sesión existe en la base de datos e indico la clave correcta.
@app.route('/select', methods=['GET','POST'])
def select():
    conn=mysql.connection
    cursor=conn.cursor()
    nombusuario = request.args.get('nombusuario')
    sql = "SELECT * FROM colegio.usuario WHERE nombusuario = %s" 
    cursor.execute(sql, (nombusuario,))
    datos = cursor.fetchone() 
    conn.commit() 
    if datos[0] == 'Admin' and datos[1] == 'super':
        sql = "SELECT * FROM colegio.alumno;"
        cursor = conn.cursor() 
        cursor.execute(sql) 
        db_alumno = cursor.fetchall()
        #for alumno in db_alumno:
         #   print(alumno)
        cursor.close()   
        return render_template('colegio/index.html', alumno = db_alumno,  )
  
#FUNCION PARA MOSTRAR LA DATA DE ALUMNOS 
@app.route('/index') 
def index():
    # Creamos una variable que va a contener la consulta SQL para obtener los alumnos:
    sql = "SELECT a.*, r.nombrerep, r.apellidorep, c.nombcurso FROM `colegio`.`alumno` a JOIN `colegio`.`representante` r JOIN `colegio`.`curso` c ON a.idrepresentante = r.idrepresentante and a.idcurso= c.idcurso"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    db_alumno = cursor.fetchall()
    #for alumno in db_alumno:
     #   print(alumno) 
    cursor.close()
    # Devolvemos código HTML para ser renderizado
    return render_template('colegio/index.html', alumno = db_alumno,  )
   

#--------------------------------------------------------------------
# Función para eliminar un registro de Alumno
@app.route('/destroy/<int:idalumno>')
def destroy(idalumno):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `colegio`.`alumno` WHERE idalumno=%s", (idalumno,))
    conn.commit()
    cursor.close()
    return redirect('/index')

#--------------------------------------------------------------------
# Ruta para actualizar los datos de un Alumno
@app.route('/update', methods=['POST'])
def update():
    _nombalumno = request.form['txtnombalumno']
    _apellidoalum = request.form['txtapellidoalum']
    _dnialumno = request.form['txtdnialumno']
    _emailalumno = request.form['txtemailalumno']
    _idrepresentante = request.form['txtidrepresentante']  
    _idcurso = request.form['txtidcurso']
    _fotoalumno = request.files['txtfotoalumno']
    _idalumno = request.form['txtidalumno']
   
    conn = mysql.connection
    cursor = conn.cursor()

    # Actualizamos los datos básicos del alumno
    sql = "UPDATE colegio.alumno SET nombalumno=%s, apellidoalum=%s, dnialumno=%s, emailalumno=%s, idrepresentante=%s, idcurso=%s WHERE idalumno=%s"
    params = (_nombalumno, _apellidoalum, _dnialumno, _emailalumno, _idrepresentante, _idcurso, _idalumno)
    cursor.execute(sql, params)

    # Si se proporciona una nueva foto, actualizamos la foto
    if _fotoalumno.filename != '':
        # Guardamos la foto con un nombre único basado en el tiempo
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + "_" + _fotoalumno.filename
        _fotoalumno.save(os.path.join(app.config['CARPETA'], nuevoNombreFoto))
       
        # Consultamos la foto anterior para borrarla del servidor
        cursor.execute("SELECT fotoalumno FROM colegio.alumno WHERE idalumno=%s", (_idalumno,))
        fila = cursor.fetchone()
        if fila and fila[0] is not None:
            nombreFotoAnterior = fila[0]
            rutaFotoAnterior = os.path.join(app.config['CARPETA'], nombreFotoAnterior)
            if os.path.exists(rutaFotoAnterior):
                os.remove(rutaFotoAnterior)
       
        # Actualizamos la base de datos con el nuevo nombre de la foto
        cursor.execute("UPDATE colegio.alumno SET fotoalumno=%s WHERE idalumno=%s", (nuevoNombreFoto, _idalumno))

    conn.commit()
    cursor.close()
    return redirect('/index')

#--------------------------------------------------------------------
# FUNCION PARA EDITAR UN ALUMNO
@app.route('/edit/<int:idalumno>')
def edit(idalumno):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT a.*,r.nombrerep, r.apellidorep, c.idcurso , c.nombcurso FROM `colegio`.`alumno` a JOIN `colegio`.`representante` r JOIN `colegio`.`curso` c ON a.idrepresentante = r.idrepresentante and a.idcurso=c.idcurso and a.idalumno=%s", (idalumno,))
    alumnos = cursor.fetchall()
    cursor.close()
    return render_template('colegio/edit.html', alumnos=alumnos,)

# FUNCION PARA CREAR UN ALUMNO
@app.route('/create')
def create():
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT idrepresentante, nombrerep, apellidorep FROM `colegio`.`representante`")
    representantes = cursor.fetchall()
    cursor.execute("SELECT idcurso, nombcurso FROM `colegio`.`curso`")
    cursos = cursor.fetchall()
    return render_template('colegio/create.html', representantes=representantes, cursos=cursos)

@app.route('/store', methods=['POST'])
def storage():
    # Recibimos los valores del formulario y los pasamos a variables locales:
    _nombalumno = request.form['txtnombalumno']
    _apellidoalum = request.form['txtapellidoalum']
    _dnialumno = request.form['txtdnialumno']
    _emailalumno = request.form['txtemailalumno']
    _idrepresentante = request.form['txtidrepresentante']  
    _idcurso= request.form['txtidcurso']
    _fotoalumno = request.files['txtfotoalumno']
    # Guardamos en now los datos de fecha y hora
    now = datetime.now()
    
    # Y en tiempo almacenamos una cadena con esos datos
    tiempo = now.strftime("%Y%H%M%S") 
    
    # Si el nombre de la foto ha sido proporcionado en el form...
    if _fotoalumno.filename != '':
        # ...le cambiamos el nombre.
        nuevoNombreFoto = tiempo + _fotoalumno.filename 
        # Guardamos la foto en el sistema de archivos
        _fotoalumno.save(f"uploads/{nuevoNombreFoto}")

        # Y armamos una tupla con esos valores:
        datos = (  _nombalumno, _apellidoalum, _dnialumno, _emailalumno,  _idrepresentante, _idcurso,  nuevoNombreFoto)
    else:
        datos = ( _nombalumno, _apellidoalum, _dnialumno, _emailalumno, _idrepresentante,_idcurso, None )
    
    # Armamos la sentencia SQL que va a almacenar estos datos en la DB:
    sql = "INSERT INTO colegio.alumno ( idalumno, nombalumno,apellidoalum, dnialumno, emailalumno, idrepresentante, idcurso, fotoalumno ) VALUES ( NULL, %s, %s, %s, %s,  %s, %s, %s );"
    
    conn = mysql.connection  # Nos conectamos a la base de datos 
    cursor = conn.cursor()   # En cursor vamos a realizar las operaciones
    cursor.execute(sql, datos)  # Ejecutamos la sentencia SQL en el cursor
    conn.commit()  # Hacemos el commit
   
   
    cursor.close()
    return redirect('/index')
   


#--------------------------------------------------------------------
# Estas líneas de código las requiere python para que 
# se pueda empezar a trabajar con la aplicación
if __name__ == '__main__':
    # Corremos la aplicación en modo debug
    app.run(debug=True)
#--------------------------------------------------------------------

