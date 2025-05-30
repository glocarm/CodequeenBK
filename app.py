from flask import Flask, flash, url_for,render_template, request, redirect, send_from_directory, jsonify
from flask_mysqldb import MySQL
from datetime import datetime 
import os

# Creamos la aplicación
app = Flask(__name__) 
app.secret_key = '1234'

# Creamos la conexión con la base de datos:
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'colegio'

# Inicializamos la extensión MySQL
mysql = MySQL(app)

app.config['STATIC_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
app.config['IMG_FOLDER'] = os.path.join(app.config['STATIC_FOLDER'], 'img')

# Guardamos la ruta de la carpeta "uploads" en nuestra app
CARPETA= os.path.join('fotos')
app.config['CARPETA']=CARPETA

#--------------------------------------------------------------------
# Generamos el acceso a la carpeta fotos. 
# El método fotos que creamos nos dirige a la carpeta (variable CARPETA)
# y nos muestra la foto guardada en la variable nombreFoto.
@app.route('/fotos/<fotoalumno>')
def fotos(fotoalumno):
 return send_from_directory(app.config['CARPETA'], fotoalumno)

#--------------------------------------------------------------------
# Proporcionamos la ruta a la raíz del sitio
@app.route('/')
def inicio():
    return render_template('colegio/landing.html')

#--------------------------------------------------------------------
#VERIFICAR DATOS DEL INICIO DE SESION. 
@app.route('/iniciarsesion')
def consultar():
    conn = mysql.connection
    cursor = conn.cursor()
    sql = "SELECT * FROM colegio.empresa;"
    cursor.execute(sql)
    empresa = cursor.fetchone()
    cursor.close()   
    return render_template('colegio/iniciosesion.html', empresa=empresa,)  

#--------------------------------------------------------------------
#ruta para consultar si el usuario que inicia sesión existe en la base de datos e indico la clave correcta.
@app.route('/select', methods=['GET', 'POST'])
def select():
    conn = mysql.connection
    cursor = conn.cursor()
    _username = request.args.get('txtusername')
    _password = request.args.get('txtpassword')
    sql = "SELECT * FROM colegio.usuario WHERE username = %s AND password = %s"
    cursor.execute(sql, (_username, _password))
    conn.commit() 
    datos = cursor.fetchone() 
    print(datos)
    if datos:
        if datos[3] == 'Admin' and datos[4] == 'super':
            sql = "SELECT * FROM colegio.alumno;"
            cursor = conn.cursor() 
            cursor.execute(sql) 
            db_alumno = cursor.fetchall()
            sql = "SELECT * FROM colegio.empresa;"
            cursor.execute(sql)
            empresa = cursor.fetchall()
            cursor.close()   
            return redirect('/indexppal')
        else:
            return jsonify({'status': 'success', 'message': 'Usuario autenticado', 'data': datos})
    else:
        return jsonify({'status': 'fail', 'message': 'Usuario o clave incorrectos'})
      
#--------------------------------------------------------------------
# FUNCIONES PARA MOSTRAR LAS CARDS DE LAS AULAS EN EL INICIO  
@app.route('/indexppal') 
def indexppal():
    # Creamos una variable que va a contener la consulta SQL para obtener los alumnos:
    sql = "SELECT c.nombcurso, m.nombmateria FROM `colegio`.`materiacurso` a JOIN `colegio`.`materia` m JOIN `colegio`.`curso` c ON a.idcurso = c.idcurso and a.idmateria= m.idmateria ORDER BY c.nombcurso asc"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    dataula = cursor.fetchall()
    sql = "SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    # Devolvemos código HTML para ser renderizado
    return render_template('colegio/indexppal.html', dataula=dataula , empresa=empresa )

#--------------------------------------------------------------------
# REGISTRAR DATOS DE EMPRESA 
#--------------------------------------------------------------------
@app.route('/indexemp') 
def indexemp():
    # Creamos una variable que va a contener la consulta SQL para obtener los datos de Empresa:
    sql = "SELECT * FROM `colegio`.`empresa`"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('colegio/indexemp.html', empresa=empresa, )

#--------------------------------------------------------------------
# FUNCION PARA CREAR EMPRESA
@app.route('/createmp')
def createmp():
    sql = "SELECT * FROM `colegio`.`empresa`"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('colegio/createmp.html', empresa=empresa,) 
    
#--------------------------------------------------------------------
# FUNCION PARA GUARDAR DATA DE EMPRESA
#--------------------------------------------------------------------
@app.route('/storemp', methods=['POST'])
def storagemp():
    # Recibimos los valores del formulario y los pasamos a variables locales:
    _rifemp = request.form['txtrifemp']
    _nombemp = request.form['txtnombemp']
    _diremp = request.form['txtdiremp']
    _cedreplegal = request.form['txtcedreplegal']
    _nombreplegal = request.form['txtnombreplegal']
    _apellreplegal = request.form['txtapellreplegal']
    _logoemp = request.files['txtlogoemp']
    if _logoemp.filename != '':
        nuevologoemp = _logoemp.filename 
        _logoemp.save(f"uploads/{nuevologoemp}")
        datos = (_rifemp,  _nombemp, _diremp, _cedreplegal, _nombreplegal, _apellreplegal, nuevologoemp)
    else:
        datos = (_rifemp,  _nombemp, _diremp, _cedreplegal, _nombreplegal, _apellreplegal, None)
    sql = "INSERT INTO `colegio`.`empresa` (idemp, rifemp,  nombemp, diremp, cedreplegal, nombreplegal, apellreplegal, logoemp) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s);"
    conn = mysql.connection   
    cursor = conn.cursor()   
    try:
        cursor.execute(sql, datos) 
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()   
    return redirect('/indexemp')

#--------------------------------------------------------------------
# FUNCION PARA EDITAR DATA DE EMPRESA
#--------------------------------------------------------------------
@app.route('/editemp/<int:idemp>')
def editemp(idemp):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `colegio`.`empresa` WHERE idemp=%s", (idemp,))
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('colegio/editemp.html', empresa=empresa,)
#--------------------------------------------------------------------
# FUNCION PARA MODIFICAR DATA DE EMPRESA
#--------------------------------------------------------------------
@app.route('/updatemp', methods=['POST'])
def updatemp():
    _rifemp = request.form['txtrifemp']
    _nombemp = request.form['txtnombemp']
    _diremp = request.form['txtdiremp']
    _cedreplegal = request.form['txtcedreplegal']
    _nombreplegal = request.form['txtnombreplegal']
    _apellreplegal = request.form['txtapellreplegal']  
    _logoemp = request.files['txtlogoemp']
    _idemp = request.form['txtidemp'] 
    conn = mysql.connection
    cursor = conn.cursor()
    # Actualizamos los datos básicos de Empresa
    sql = "UPDATE `colegio`.`empresa` SET rifemp=%s, nombemp=%s, diremp=%s, cedreplegal=%s, nombreplegal=%s, apellreplegal=%s WHERE idemp=%s"
    params = (_rifemp, _nombemp, _diremp, _cedreplegal, _nombreplegal, _apellreplegal, _idemp)
    cursor.execute(sql, params)
     # Procesar la imagen
    if _logoemp and _logoemp.filename != '':
        # Guardar la imagen siempre con el nombre 'logoemp.png'
        filename = 'logoemp.png'
        ruta_destino = os.path.join(app.config['IMG_FOLDER'], filename)
        # Guardar la nueva imagen
        _logoemp.save(ruta_destino)

        # Si quieres eliminar la anterior, no es necesario porque siempre será la misma
        # pero si quieres asegurarte, puedes hacer esto:
        cursor.execute("SELECT logoemp FROM colegio.empresa WHERE idemp=%s", (_idemp,))
        fila = cursor.fetchone()
        if fila and fila[0]:
            ruta_logo_antigua = os.path.join(app.config['IMG_FOLDER'], fila[0])
            if os.path.exists(ruta_logo_antigua) and fila[0] != filename:
                os.remove(ruta_logo_antigua)
        # Actualizar la base de datos con el nombre fijo
        cursor.execute("UPDATE colegio.empresa SET logoemp=%s WHERE idemp=%s", (filename, _idemp))
    conn.commit()
    cursor.close()
    return redirect('/indexemp')
#--------------------------------------------------------------------
# MANEJO DE ALUMNOS - MOSTRAR LISTADO DE ALUMNOS
#--------------------------------------------------------------------
@app.route('/index') 
def index():
    # Creamos una variable que va a contener la consulta SQL para obtener los alumnos:
    sql = "SELECT a.*, r.nombrerep, r.apellidorep, c.nombcurso FROM `colegio`.`alumno` a JOIN `colegio`.`representante` r JOIN `colegio`.`curso` c ON a.idrepresentante = r.idrepresentante and a.idcurso= c.idcurso"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    db_alumno = cursor.fetchall()
    for alumno in db_alumno:
      print(alumno) 
    sql="SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    cursor.close()
    # Devolvemos código HTML para ser renderizado
    return render_template('colegio/index.html', alumno = db_alumno, empresa=empresa, )
#--------------------------------------------------------------------
# FUNCION PARA CREAR UN ALUMNO
#--------------------------------------------------------------------
@app.route('/create')
def create():
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT idrepresentante, nombrerep, apellidorep FROM `colegio`.`representante`")
    representantes = cursor.fetchall()
    cursor.execute("SELECT idcurso, nombcurso FROM `colegio`.`curso`")
    cursos = cursor.fetchall()
    sql="SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('colegio/create.html', representantes=representantes, cursos=cursos ,empresa=empresa, )

#--------------------------------------------------------------------
# FUNCION PARA GUARDAR UN ALUMNO Y LAS MATERIAS A CURSAR
#--------------------------------------------------------------------
@app.route('/store', methods=['GET','POST']) 
def storage(): 
    conn = mysql.connection
    cursor = conn.cursor() 
    _tipousu='' # Recibimos los valores del formulario y los pasamos a variables locales: 
    _tipousuario=request.form['txttipousuario'] 
    _nombalumno = request.form['txtnombalumno'] 
    _apellidoalum = request.form['txtapellidoalum'] 
    _dnialumno = request.form['txtdnialumno'] 
    _emailalumno = request.form['txtemailalumno'] 
    _idrepresentante = request.form['txtidrepresentante']
    _idcurso = request.form['txtidcurso'] 
    _password = request.form['txtpassword'] 
    _fotoalumno = request.files['txtfotoalumno']
    if _tipousu=='1':
        _tipousuario='DIRECTIVO'
    if _tipousu=='2':
        _tipousuario='DOCENTE'
    if _tipousu=='3':
        _tipousuario='COORDINADOR'
    if _tipousu=='4':
        _tipousuario='AUXILIAR'
    if _tipousu=='5':
        _tipousuario='ALUMNO'
    _username=_emailalumno
    # Guardamos en now los datos de fecha y hora
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S") 
    if _fotoalumno.filename != '':
        nuevoNombreFoto = tiempo + _fotoalumno.filename 
        _fotoalumno.save(f"static/fotos/{nuevoNombreFoto}")
        datos = (_nombalumno, _apellidoalum, _dnialumno, _emailalumno, _idrepresentante, _idcurso, nuevoNombreFoto, _tipousuario )
    else:
        datos = ( _nombalumno, _apellidoalum, _dnialumno, _emailalumno, _idrepresentante, _idcurso, None, _tipousuario )
    sql = "INSERT INTO `colegio`.`alumno` (idalumno, nombalumno, apellidoalum, dnialumno, emailalumno, idrepresentante, idcurso, fotoalumno, tipousuario) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(sql, datos)
    # Obtener el idalumno recién insertado 
    ultidalumno = cursor.lastrowid
    #conn.commit()
    datausuario=(_tipousuario,_nombalumno, _apellidoalum, _username, _password )
    sql = "INSERT INTO `colegio`.`usuario` (idusuario, tipousuario, nombre, apellido, username, password) VALUES (NULL, %s, %s, %s, %s, %s);"
    cursor.execute(sql, datausuario) 
    conn.commit()
    # Obtener los idcursomat asociados al idcurso
    cursor.execute("SELECT idcursomat FROM materiacurso WHERE idcurso = %s", (_idcurso,))
    curmatalumno = cursor.fetchall()
    print("este",curmatalumno)
    # Comprobar si se han encontrado cursos
    if curmatalumno:
        for curmatalumno_row in curmatalumno:
            materia = curmatalumno_row[0]
            cursor.execute("INSERT INTO materialumno (idcursomat, idalumno) VALUES (%s, %s)", ( materia, ultidalumno))
    else:
        print("No se encontraron cursos asociados al idcurso proporcionado.")       
    conn.commit()
    cursor.close()   
    return redirect('/index')  
#--------------------------------------------------------------------
#  EDITAR  ALUMNO
#--------------------------------------------------------------------
@app.route('/edit/<int:idalumno>')
def edit(idalumno):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT a.* , r.idrepresentante, r.nombrerep, r.apellidorep, c.idcurso , c.nombcurso FROM `colegio`.`alumno` a JOIN `colegio`.`representante` r JOIN `colegio`.`curso` c ON a.idrepresentante = r.idrepresentante and a.idcurso=c.idcurso and a.idalumno=%s", (idalumno,))
    alumnos = cursor.fetchall()
    sql="SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    sql="SELECT * FROM `colegio`.`representante`"
    cursor.execute(sql) 
    representante = cursor.fetchall()
    sql="SELECT * FROM `colegio`.`curso`"
    cursor.execute(sql) 
    curso = cursor.fetchall()
    cursor.close()
    return render_template('colegio/edit.html', alumnos=alumnos, empresa=empresa, representante=representante, curso=curso,)

#--------------------------------------------------------------------
#  MODIFICAR LOS DATOS DEL ALUMNO
#--------------------------------------------------------------------
@app.route('/update', methods=['POST'])
def update():
    _nombalumno = request.form['txtnombalumno']
    _apellidoalum = request.form['txtapellidoalum']
    _dnialumno = request.form['txtdnialumno']
    _emailalumno = request.form['txtemailalumno']
    _idrepresentante = request.form['txtidrepresentante']  
    _idcursonew = request.form['txtidcursonew']
    _fotoalumno = request.files['txtfotoalumno']
    _idalumno = request.form['txtidalumno'] 
    conn = mysql.connection
    cursor = conn.cursor()
    
    try:
        nuevo_curso_id = int(_idcursonew)
    except ValueError:
        # Manejar error si no es un entero válido
        nuevo_curso_id = None
    # Obtener el curso actual del alumno antes de la actualización
    cursor.execute("SELECT idcurso FROM colegio.alumno WHERE idalumno=%s", (_idalumno,))
    fila_actual = cursor.fetchone()
    curso_actual = fila_actual[0] if fila_actual else None
    # Actualizamos los datos básicos del alumno
    sql = "UPDATE colegio.alumno SET nombalumno=%s, apellidoalum=%s, dnialumno=%s, emailalumno=%s, idrepresentante=%s, idcurso=%s WHERE idalumno=%s"
    params = (_nombalumno, _apellidoalum, _dnialumno, _emailalumno, _idrepresentante, _idcursonew, _idalumno)
    cursor.execute(sql, params)
    # Si se proporciona una nueva foto, actualizamos la foto
    if _fotoalumno.filename != '':
        # Guardamos la foto con un nombre único basado en el tiempo
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        nuevoNombreFoto = tiempo + "_" + _fotoalumno.filename
        _fotoalumno.save(f"static/fotos/{nuevoNombreFoto}")
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
    # Si el curso cambió, actualizar la tabla materialumno
    # Si el curso cambió, actualizar la tabla materialumno
    if curso_actual != nuevo_curso_id:
        # Eliminar registros antiguos
        cursor.execute("DELETE FROM colegio.materialumno WHERE idalumno=%s", (_idalumno,))
        # Obtener las materias del **nuevo** curso
        cursor.execute("SELECT idcursomat FROM colegio.materiacurso WHERE idcurso=%s", (nuevo_curso_id,))
        cursomats = cursor.fetchall()
        if cursomats:
            for cursomats_row in cursomats:
                materia_id = cursomats_row[0]
                cursor.execute("INSERT INTO colegio.materialumno (idcursomat, idalumno) VALUES (%s, %s)", (materia_id, _idalumno))
        else:
            print("No se encontraron materias asociadas al nuevo idcurso proporcionado.")
    conn.commit()
    cursor.close()
    return redirect('/index')
      
#--------------------------------------------------------------------
# FUNCION PARA ELIMINAR UN ALUMNO
#--------------------------------------------------------------------
@app.route('/destroy/<int:idalumno>')
def destroy(idalumno):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `colegio`.`alumno` WHERE idalumno=%s", (idalumno,))
    conn.commit()
    cursor.close()
    return redirect('/index')
    
#--------------------------------------------------------------------
#FUNCION PARA LISTAR LAS  MATERIAS DEL CURSO (ASIGNADAS O NO ) - ALUMNO Y ACTUALIZAR 
#--------------------------------------------------------------------
@app.route('/listarmatalumno/<int:idalumno>,<int:idcurso>', methods=['GET', 'POST'])
def listarmatalumno(idalumno,idcurso):
    conn = mysql.connection
    cursor = conn.cursor()
    # Seleccionamos el id y nombre del curso
    cursor.execute("SELECT a.*, c.nombcurso FROM alumno a, curso c WHERE c.idcurso=a.idcurso AND a.idalumno=%s;", (idalumno,))
    cursoalumno = cursor.fetchone()
    # Obtener las materias no asignadas
    cursor.execute("SELECT * FROM materia WHERE idmateria NOT IN (SELECT mc.idmateria FROM materiacurso mc JOIN materialumno ma ON mc.idcursomat = ma.idcursomat WHERE ma.idalumno = %s);", (idalumno,))
    materias_no_asignadas = cursor.fetchall()
    # Seleccionamos el id y nombre de las materias asignadas al alumno
    cursor.execute("select m.idmateria, m.nombmateria from materia m, materiacurso mc where mc.idcursomat IN (SELECT idcursomat FROM materialumno WHERE idalumno=%s) AND m.idmateria= mc.idmateria;", (idalumno,))
    materias_asignadas = cursor.fetchall()
    sql="SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    conn.commit()
    if materias_asignadas or materias_no_asignadas:
        return render_template('colegio/listarmatalumno.html', cursoalumno = cursoalumno,  materias_asignadas = materias_asignadas,  materias_no_asignadas = materias_no_asignadas , empresa=empresa, )  
    else: 
        return redirect('/index')    
        
#--------------------------------------------------------------------    
#   FUNCION PARA ASIGNAR MATERIAS A UN ALUMNO
#--------------------------------------------------------------------    
@app.route('/materialumno/<int:idalumno>,<int:idcurso>', methods=['GET', 'POST'])
def materialumno(idalumno,idcurso):
    conn = mysql.connection
    if request.method == 'POST':
        conn = mysql.connection  # Obtener la conexión a la base de datos
        cursor = conn.cursor()
        cursor.execute("SELECT idcursomat FROM materiacurso WHERE idcurso=%s",(idcurso,))
        cursomatalum = cursor.fetchall()
        cursor.close()
        for cursomatalum in cursomatalum:
            cursor.execute("INSERT INTO materialumno ( idcursomat, idalumno) VALUES ( %s,%s)", ( {{cursomatalum[0]}}, idalumno))
        conn.commit()  
        # Redirigir a la página de indexcurso después de guardar
        return redirect('/index')  # Redirigir a la ruta deseada
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.idcursomat, a.idcurso, b.nombcurso, a.idmateria, c.nombmateria 
        FROM `materiacurso` as a 
        JOIN `curso` as b ON a.idcurso=b.idcurso 
        JOIN `materia` as c ON a.idmateria=c.idmateria 
        LEFT JOIN `cursomatprof` as d ON a.idcursomat=d.idcursomat AND d.idprofesor IS NOT NULL
        WHERE d.idcursomat IS NULL AND a.estatus='NO' 
        ORDER BY a.idcursomat ASC;
    """)
    cursor.execute("SELECT a.idcursomat, a.idcurso, b.nombcurso, a.idmateria, c.nombmateria FROM `materiacurso` as a join `curso` as b join `materia` as c WHERE a.idcurso=b.idcurso and a.idmateria=c.idmateria and a.estatus='NO' order by a.idcursomat asc;")
    materia = cursor.fetchall()
    cursor.execute("SELECT * FROM `colegio`.`alumno` WHERE idalumno=%s", (idalumno,))
    alumno = cursor.fetchall()
    cursor.close()
    # Obtener las materias no asignadas
    cursor.execute("SELECT * FROM materia WHERE idmateria NOT IN (SELECT mc.idmateria FROM materiacurso mc JOIN materialumno ma ON mc.idcursomat = ma.idcursomat WHERE ma.idalumno = %s);", (idalumno,))
    materias_no_asignadas = cursor.fetchall()
    cursor.close()
    return render_template('colegio/listarmatalumno.html', alumno=alumno, materia=materia, materias_no_asignadas=materias_no_asignadas)

#--------------------------------------------------------------------    
#   FUNCION PARA ASIGNAR MATERIAS ANTERIORMENTE ELIMINADAS A UN ALUMNO
#--------------------------------------------------------------------    
@app.route('/matelimalumno/<int:idalumno>,<int:idcurso>,<int:idmateria>', methods=['GET', 'POST'])
def matelimalumno(idalumno,idcurso,idmateria):
    conn = mysql.connection
    if request.method == 'POST':
        conn = mysql.connection  # Obtener la conexión a la base de datos
        cursor = conn.cursor()
        cursor.execute("SELECT idcursomat FROM materiacurso WHERE idcurso=%s",(idcurso,))
        cursomatalum = cursor.fetchall()
        cursor.close()
        for cursomatalum in cursomatalum:
            cursor.execute("INSERT INTO materialumno ( idcursomat, idalumno) VALUES ( %s,%s)", ( {{cursomatalum[0]}}, idalumno))
        conn.commit()  
        return redirect('/index')  
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.idcursomat, a.idcurso, b.nombcurso, a.idmateria, c.nombmateria 
        FROM `materiacurso` as a 
        JOIN `curso` as b ON a.idcurso=b.idcurso 
        JOIN `materia` as c ON a.idmateria=c.idmateria 
        LEFT JOIN `cursomatprof` as d ON a.idcursomat=d.idcursomat AND d.idprofesor IS NOT NULL
        WHERE d.idcursomat IS NULL AND a.estatus='NO' 
        ORDER BY a.idcursomat ASC;
    """)
    cursor.execute("SELECT a.idcursomat, a.idcurso, b.nombcurso, a.idmateria, c.nombmateria FROM `materiacurso` as a join `curso` as b join `materia` as c WHERE a.idcurso=b.idcurso and a.idmateria=c.idmateria and a.estatus='NO' order by a.idcursomat asc;")
    materia = cursor.fetchall()
    cursor.execute("SELECT * FROM `colegio`.`alumno` WHERE idalumno=%s", (idalumno,))
    alumno = cursor.fetchall()
    cursor.close()
    return render_template('colegio/listarmatalumno.html', alumno=alumno, materia=materia, )

#--------------------------------------------------------------------    
# FUNCION PARA ASIGNAR MATERIAS ANTERIORMENTE ELIMINADAS A UN ALUMNO
#--------------------------------------------------------------------    
@app.route('/destroymatalum/<int:idalumno>,<int:idcurso>,<int:idmateria>', methods=['GET', 'POST'])
def destroymatalum(idalumno, idcurso, idmateria):
    print(idalumno, idcurso, idmateria)
    conn = mysql.connection
    cursor = conn.cursor()

    # Verifica si la materia está asignada antes de eliminar
    cursor.execute("""
        SELECT ma.idcursomat FROM materialumno ma
        WHERE ma.idalumno=%s AND ma.idcursomat IN (
            SELECT mc.idcursomat FROM materiacurso mc
            WHERE mc.idcurso=%s AND mc.idmateria=%s
        );
    """, (idalumno, idcurso, idmateria))
    asignada = cursor.fetchone()

    if asignada:
        # Realiza la eliminación
        cursor.execute("""
            DELETE FROM materialumno WHERE idalumno=%s AND idcursomat IN (
                SELECT mc.idcursomat FROM materiacurso mc
                WHERE mc.idcurso=%s AND mc.idmateria=%s
            );
        """, (idalumno, idcurso, idmateria))
        conn.commit()  # Asegúrate de guardar los cambios
        print("Materia eliminada correctamente.")
    else:
        print("La materia no estaba asignada al alumno o ya fue eliminada.")

    # Ahora, actualiza las listas para reflejar cambios
    cursor.execute("SELECT a.*, c.nombcurso FROM alumno a, curso c WHERE c.idcurso=a.idcurso AND a.idalumno=%s;", (idalumno,))
    cursoalumno = cursor.fetchone()

    cursor.execute("""
        SELECT m.idmateria, m.nombmateria FROM materialumno ma
        JOIN materiacurso mc ON ma.idcursomat = mc.idcursomat
        JOIN materia m ON mc.idmateria = m.idmateria
        WHERE ma.idalumno=%s;
    """, (idalumno,))
    materias_asignadas = cursor.fetchall()

    cursor.execute("""
        SELECT ma.idmateria, ma.nombmateria FROM materia ma
        WHERE ma.idmateria NOT IN (
            SELECT mc.idmateria FROM materiacurso mc
            JOIN materialumno ma2 ON mc.idcursomat = ma2.idcursomat
            WHERE ma2.idalumno=%s
        );
    """, (idalumno,))
    materias_no_asignadas = cursor.fetchall()

    cursor.execute("SELECT * FROM `colegio`.`empresa`")
    empresa = cursor.fetchone()

    return render_template(
        'colegio/listarmatalumno.html',
        cursoalumno=cursoalumno,
        materias_asignadas=materias_asignadas,
        materias_no_asignadas=materias_no_asignadas,
        empresa=empresa
    )

#--------------------------------------------------------------------    
# FUNCION PARA ASIGNAR MATERIAS ANTERIORMENTE ELIMINADAS A UN ALUMNO
#--------------------------------------------------------------------    
@app.route('/reasignarmatalum/<int:idalumno>,<int:idcurso>,<int:idmateria>', methods=['GET', 'POST'])
def reasignarmatalum(idalumno, idcurso, idmateria):
    print(idalumno, idcurso, idmateria)
    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("""
       SELECT idcursomat FROM materiacurso 
            WHERE idcurso=%s AND idmateria=%s
        ;
    """, (idcurso, idmateria))
    id_cursomat = cursor.fetchone()
    print(id_cursomat[0])
    if id_cursomat:
        id_cursomat_id = id_cursomat[0]
        # Verificar si la materia ya está asignada al alumno
        cursor.execute("""
            SELECT * FROM materialumno WHERE idcursomat=%s AND idalumno=%s
        """, (id_cursomat_id, idalumno))
        ya_asignada = cursor.fetchone()
        if not ya_asignada:
            # Realizar la inserción
            try:
                cursor.execute("""
                    INSERT INTO materialumno (idcursomat, idalumno) VALUES (%s, %s)
                """, (id_cursomat_id, idalumno))
                conn.commit()
                print("Materia reasignada correctamente.")
            except Exception as e:
                print("Error al insertar:", e)
        
        else:
            print("La materia ya estaba asignada al alumno o no fue eliminada.")
    else:
            print("No se encontró la materia en el curso con esos datos, o ya fue eliminada.")
            
    # Ahora, actualiza las listas para reflejar cambios
    cursor.execute("SELECT a.*, c.nombcurso FROM alumno a, curso c WHERE c.idcurso=a.idcurso AND a.idalumno=%s;", (idalumno,))
    cursoalumno = cursor.fetchone()

    cursor.execute("""
        SELECT m.idmateria, m.nombmateria FROM materialumno ma
        JOIN materiacurso mc ON ma.idcursomat = mc.idcursomat
        JOIN materia m ON mc.idmateria = m.idmateria
        WHERE ma.idalumno=%s;
    """, (idalumno,))
    materias_asignadas = cursor.fetchall()

    cursor.execute("""
        SELECT ma.idmateria, ma.nombmateria FROM materia ma
        WHERE ma.idmateria NOT IN (
            SELECT mc.idmateria FROM materiacurso mc
            JOIN materialumno ma2 ON mc.idcursomat = ma2.idcursomat
            WHERE ma2.idalumno=%s
        );
    """, (idalumno,))
    materias_no_asignadas = cursor.fetchall()

    cursor.execute("SELECT * FROM `colegio`.`empresa`")
    empresa = cursor.fetchone()

    return render_template(
        'colegio/listarmatalumno.html',
        cursoalumno=cursoalumno,
        materias_asignadas=materias_asignadas,
        materias_no_asignadas=materias_no_asignadas,
        empresa=empresa
    )


#--------------------------------------------------------------------    
# FUNCION PARA MOSTRAR DATOS DE LOS CURSOS
#--------------------------------------------------------------------  
@app.route('/indexcurso') 
def indexcurso():
    # Creamos una variable que va a contener la consulta SQL para obtener los cursos:
    sql = "SELECT * FROM `colegio`.`curso`"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    db_curso = cursor.fetchall()
    for curso in db_curso:
       print(curso) 
    cursor.close()
    # Devolvemos código HTML para ser renderizado
    return render_template('colegio/indexcursos.html', curso = db_curso,  )
 
# FUNCION PARA CREAR UN CURSO
@app.route('/createcurso')
def createcurso():
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT idrepresentante, nombrerep, apellidorep FROM `colegio`.`representante`")
    representantes = cursor.fetchall()
    cursor.execute("SELECT idcurso, nombcurso FROM `colegio`.`curso`")
    cursos = cursor.fetchall()
    return render_template('colegio/indexcurso.html', representantes=representantes, cursos=cursos)

@app.route('/storecurso', methods=['POST'])
def storagecurso():
    # Recibimos los valores del formulario y los pasamos a variables locales:
    _nombcurso = request.form['txtnombcurso']     
    datos = ( _nombcurso, )
    # Armamos la sentencia SQL que va a almacenar estos datos en la DB:
    sql = "INSERT INTO colegio.curso ( idcurso, nombcurso) VALUES ( NULL, %s );"
    conn = mysql.connection  # Nos conectamos a la base de datos 
    cursor = conn.cursor()   # En cursor vamos a realizar las operaciones
    cursor.execute(sql, datos)  # Ejecutamos la sentencia SQL en el cursor
    conn.commit()  # Hacemos el commit
    cursor.close()
    return redirect('/indexcurso')
#--------------------------------------------------------------------
# Ruta para actualizar los datos de un Profesor
@app.route('/updatecurso', methods=['POST'])
def updatecurso():
    _nombcurso = request.form['txtnombcurso']
    _idcurso = request.form['txtidcurso']
    conn = mysql.connection
    cursor = conn.cursor()

    # Actualizamos los datos básicos del alumno
    sql = "UPDATE colegio.curso SET nombcurso=%s WHERE idcurso=%s"
    params = (_nombcurso, _idcurso)
    cursor.execute(sql, params) 
    conn.commit()
    cursor.close()
    return redirect('/indexcurso')

#--------------------------------------------------------------------
# FUNCION PARA EDITAR UN CURSO
@app.route('/editcurso/<int:idcurso>')
def editcurso(idcurso):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `colegio`.`curso` WHERE  idcurso=%s", (idcurso,))
    curso = cursor.fetchall()
    cursor.close()
    return render_template('colegio/editcurso.html', curso=curso,)  

#--------------------------------------------------------------------
# Función para eliminar un registro de Profesor
@app.route('/destroycurso/<int:idcurso>')
def destroycurso(idcurso):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `colegio`.`curso` WHERE idcurso=%s", (idcurso,))
    conn.commit()
    cursor.close()
    return redirect('/indexcurso')

                  # AQUI VA LO DE MATERIAS
   
@app.route('/indexmateria') 
def indexmateria():
    # Creamos una variable que va a contener la consulta SQL para obtener los cursos:
    sql = "SELECT * FROM `colegio`.`materia`"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    db_materia = cursor.fetchall()
    for materia in db_materia:
       print(materia) 
    cursor.close()
    # Devolvemos código HTML para ser renderizado
    return render_template('colegio/indexmaterias.html', materia = db_materia,  )
 

@app.route('/createmateria')
def createmateria():
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    return render_template('colegio/indexmateria.html')

@app.route('/storemateria', methods=['POST'])
def storagemateria():
    # Recibimos los valores del formulario y los pasamos a variables locales:
    _nombmateria = request.form['txtnombmateria']     
    datos = ( _nombmateria, )
    # Armamos la sentencia SQL que va a almacenar estos datos en la DB:
    sql = "INSERT INTO colegio.materia ( idmateria, nombmateria) VALUES ( NULL, %s );"
    conn = mysql.connection  # Nos conectamos a la base de datos 
    cursor = conn.cursor()   # En cursor vamos a realizar las operaciones
    cursor.execute(sql, datos)  # Ejecutamos la sentencia SQL en el cursor
    conn.commit()  # Hacemos el commit
    cursor.close()
    return redirect('/indexmateria')
#--------------------------------------------------------------------
# Ruta para actualizar los datos de un Profesor
@app.route('/updatemateria', methods=['POST'])
def updatemateria():
    _nombmateria = request.form['txtnombmateria']
    _idmateria = request.form['txtidmateria']
    conn = mysql.connection
    cursor = conn.cursor()

    # Actualizamos los datos básicos del alumno
    sql = "UPDATE colegio.materia SET nombmateria=%s WHERE idmateria=%s"
    params = (_nombmateria, _idmateria)
    cursor.execute(sql, params) 
    conn.commit()
    cursor.close()
    return redirect('/indexmateria')

#--------------------------------------------------------------------
#FUNCION PARA EDITAR UN MATERIA
@app.route('/editmateria/<int:idmateria>')
def editmateria(idmateria):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `colegio`.`materia` WHERE  idmateria=%s", (idmateria,))
    materia= cursor.fetchall()
    cursor.close()
    return render_template('colegio/editmateria.html', materia=materia,)  

#--------------------------------------------------------------------
# Función para eliminar un registro de Profesor
@app.route('/destroymateria/<int:idmateria>')
def destroymateria(idmateria):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `colegio`.`materia` WHERE idmateria=%s", (idmateria,))
    conn.commit()
    cursor.close()
    return redirect('/indexmateria')  

           #MATERIAS ASOCIADAS A CURSO

#FUNCION PARA RELACIONAR MATERIAS A UN CURSO
@app.route('/materiacurso/<int:idcurso>', methods=['GET', 'POST'])
def materiacurso(idcurso):
    conn = mysql.connection
    if request.method == 'POST':
        materias_seleccionadas = request.form.getlist('materias')  # Asegúrate de que el nombre coincida
        conn = mysql.connection  # Obtener la conexión a la base de datos
        cursor = conn.cursor()
        # Guardamos en la tabla materiacurso
        for materia_id in materias_seleccionadas:
            cursor.execute("INSERT INTO materiacurso (idcurso, idmateria, estatus) VALUES (%s, %s,%s)", (idcurso, materia_id, "NO"))
        conn.commit()  # No olvides hacer commit para guardar cambios
        cursor.close()
        
        # Redirigir a la página de indexcurso después de guardar
        return redirect('/indexcurso')  # Redirigir a la ruta deseada

    # Obtén las materias y el curso para mostrarlos después de guardar
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `colegio`.`materia`")
    materia = cursor.fetchall()
    cursor.execute("SELECT * FROM `colegio`.`curso` WHERE idcurso=%s", (idcurso,))
    curso = cursor.fetchall()
    cursor.close()
    return render_template('colegio/materiascurso.html', materia=materia, curso=curso)
                      
# MANEJO DE PROFESORES 
#FUNCION PARA MOSTRAR LA DATA DE PROFESORES
@app.route('/indexprof') 
def indexprof():
    # Creamos una variable que va a contener la consulta SQL para obtener los profesores:
    sql = "SELECT * FROM `colegio`.`profesor`"
    conn = mysql.connection   
    cursor = conn.cursor() 
    cursor.execute(sql) 
    db_profesor = cursor.fetchall()
    for profesor in db_profesor:
       print(profesor) 
    sql="SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    cursor.close()
    # Devolvemos código HTML para ser renderizado
    return render_template('colegio/indexprof.html', profesor = db_profesor, empresa=empresa,  )

#--------------------------------------------------------------------
# Función para eliminar un registro de Profesor
@app.route('/destroyprof/<int:idprofesor>')
def destroyprof(idprofesor):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `colegio`.`cursomatprof` WHERE idprofesor=%s", (idprofesor,))
    dataprof = cursor.fetchall()
    if dataprof:
        flash("No se puede eliminar el profesor porque tiene cursos asociados", "error")
    else:
        cursor.execute("DELETE FROM `colegio`.`profesor` WHERE idprofesor=%s", (idprofesor,))
        flash("Datos del Profesor Eliminados correctamente", "error")
        conn.commit()  
    cursor.close()
    return redirect(url_for('indexprof'))

# FUNCION PARA CREAR UN PROFESOR
@app.route('/createprof')
def createprof():
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT idrepresentante, nombrerep, apellidorep FROM `colegio`.`representante`")
    representantes = cursor.fetchall()
    cursor.execute("SELECT idcurso, nombcurso FROM `colegio`.`curso`")
    cursos = cursor.fetchall()
    return render_template('colegio/indexprofesor.html', representantes=representantes, cursos=cursos)

@app.route('/storeprof', methods=['POST'])
def storageprof():
    # Recibimos los valores del formulario y los pasamos a variables locales:
    _nombprof = request.form['txtnombprof']
    _apellidoprof = request.form['txtapellidoprof']
    _dniprof = request.form['txtdniprof']
    _telefonoprof = request.form['txttelefonoprof']
    _direccionprof = request.form['txtdireccionprof']  
    _areaprof= request.form['txtareaprof']
    _emailprof = request.form['txtemailprof']
   
    datos = ( _nombprof, _apellidoprof, _dniprof, _telefonoprof,_direccionprof, _areaprof, _emailprof )
    
    # Armamos la sentencia SQL que va a almacenar estos datos en la DB:
    sql = "INSERT INTO colegio.profesor ( idprofesor, nombprof, apellidoprof, dniprof, telefonoprof,direccionprof, areaprof, emailprof ) VALUES ( NULL, %s, %s, %s, %s,  %s, %s, %s );"
    
    conn = mysql.connection  # Nos conectamos a la base de datos 
    cursor = conn.cursor()   # En cursor vamos a realizar las operaciones
    cursor.execute(sql, datos)  # Ejecutamos la sentencia SQL en el cursor
    conn.commit()  # Hacemos el commit
    cursor.close()
    return redirect('/indexprof')
 
#--------------------------------------------------------------------
# Ruta para actualizar los datos de un Profesor
@app.route('/updateprof', methods=['POST'])
def updateprof():
    _nombprof = request.form['txtnombprof']
    _apellidoprof = request.form['txtapellidoprof']
    _dniprof = request.form['txtdniprof']
    _telefonoprof= request.form['txttelefonoprof']
    _emailprof = request.form['txtemailprof']
    _direccionprof = request.form['txtdireccionprof']  
    _areaprof = request.form['txtareaprof']
    _idprofesor = request.form['txtidprofesor']
    conn = mysql.connection
    cursor = conn.cursor()
    # Actualizamos los datos básicos del alumno
    sql = "UPDATE `colegio`.`profesor` SET nombprof=%s, apellidoprof=%s, dniprof=%s, telefonoprof=%s, emailprof=%s, direccionprof=%s, areaprof=%s WHERE idprofesor=%s"
    params = (_nombprof, _apellidoprof, _dniprof, _telefonoprof, _emailprof, _direccionprof, _areaprof, _idprofesor)
    cursor.execute(sql, params) 
    conn.commit()
    cursor.close()
    return redirect('/indexprof')

#--------------------------------------------------------------------
# FUNCION PARA EDITAR UN PROFESOR
@app.route('/editprof/<int:idprofesor>')
def editprof(idprofesor):
    conn = mysql.connection  # Obtener la conexión a la base de datos
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `colegio`.`profesor` WHERE  idprofesor=%s", (idprofesor,))
    profesor = cursor.fetchone()
    print(profesor)
    cursor.execute("SELECT * FROM `colegio`.`empresa`")
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('colegio/editprof.html', profesor=profesor, empresa=empresa, )  

#FUNCION PARA ASIGNAR MATERIAS A UN PROFESOR
@app.route('/matcursosprof/<int:idprofesor>', methods=['GET', 'POST'])
def matcursosprof(idprofesor):
    conn = mysql.connection
    if request.method == 'POST':
        materiacursoselecc = request.form.getlist('materia')  # Asegúrate de que el nombre coincida
        conn = mysql.connection  # Obtener la conexión a la base de datos
        cursor = conn.cursor()
        # Guardamos en la tabla materiacurso
        for idcursomat in materiacursoselecc:
            cursor.execute("INSERT INTO cursomatprof ( idcursomat, idprofesor) VALUES ( %s,%s)", (  idcursomat, idprofesor,))
        conn.commit()  # No olvides hacer commit para guardar cambios
       
        # Actualizar el estatus en la tabla materiacurso
        for idcursomat in materiacursoselecc:
            cursor.execute("UPDATE materiacurso SET estatus='SI' WHERE idcursomat=%s", (idcursomat,))
        
        conn.commit()  # No olvides hacer commit para guardar cambios
        cursor.close()
        
        # Redirigir a la página de indexcurso después de guardar
        return redirect('/indexprof')  # Redirigir a la ruta deseada
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.idcursomat, a.idcurso, b.nombcurso, a.idmateria, c.nombmateria 
        FROM `materiacurso` as a 
        JOIN `curso` as b ON a.idcurso=b.idcurso 
        JOIN `materia` as c ON a.idmateria=c.idmateria 
        LEFT JOIN `cursomatprof` as d ON a.idcursomat=d.idcursomat AND d.idprofesor IS NOT NULL
        WHERE d.idcursomat IS NULL AND a.estatus='NO' 
        ORDER BY a.idcursomat ASC;
    """)
    
    # cursor.execute("SELECT a.idcursomat, a.idcurso, b.nombcurso, a.idmateria, c.nombmateria FROM `materiacurso` as a join `curso` as b join `materia` as c WHERE a.idcurso=b.idcurso and a.idmateria=c.idmateria and a.estatus='NO' order by a.idcursomat asc;")
    materia = cursor.fetchall()
    cursor.execute("SELECT * FROM `colegio`.`profesor` WHERE idprofesor=%s", (idprofesor,))
    profesor = cursor.fetchone()
    cursor.execute("SELECT * FROM `colegio`.`empresa`")
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('colegio/matcursosprof.html', profesor=profesor, materia=materia, empresa=empresa, )
  

#FUNCION PARA LISTAR LAS  MATERIAS ASIGNADAS A UN PROFESOR 
@app.route('/listarmatcurprof/<int:idprofesor>', methods=['GET', 'POST'])
def listarmatcurprof(idprofesor):
    conn = mysql.connection
    cursor = conn.cursor()
    # Guardamos en la tabla materiacurso  
    cursor.execute("SELECT a.idprofesor, a.nombprof , a.apellidoprof , e.idcursomat, b.idcurso, b.nombcurso , c.idmateria, c.nombmateria FROM profesor a JOIN cursomatprof e ON e.idprofesor = a.idprofesor JOIN materiacurso d ON e.idcursomat = d.idcursomat JOIN materia c ON c.idmateria = d.idmateria JOIN curso b ON b.idcurso = d.idcurso WHERE a.idprofesor = %s;", (idprofesor,))
    cursomatprof = cursor.fetchall()
    cursor.execute("SELECT mc.idcursomat, mc.idcurso, c.nombcurso, mc.idmateria, m.nombmateria from materiacurso mc, materia m, curso c where c.idcurso=mc.idcurso AND mc.idmateria=m.idmateria AND mc.idcursomat NOT IN (SELECT idcursomat FROM `cursomatprof` where idprofesor = %s);", (idprofesor,))
    cursomatnoasignadas = cursor.fetchall()
    cursor.execute("SELECT * FROM empresa")
    empresa = cursor.fetchone()
    cursor.close()
    if cursomatprof:
        return render_template('colegio/listmatcurprof.html', cursomatprof=cursomatprof, cursomatnoasignadas = cursomatnoasignadas, empresa=empresa,)
    else:
        return redirect('/indexprof')  # Redirigir a la ruta deseada
        

#--------------------------------------------------------------------    
# FUNCION PARA ASIGNAR MATERIAS ANTERIORMENTE ELIMINADAS A UN ALUMNO
#--------------------------------------------------------------------    
@app.route('/reasignarmatprof/<int:idprofesor>,<int:idcurso>,<int:idmateria>', methods=['GET', 'POST'])
def reasignarmatprof(idprofesor, idcurso, idmateria):
    print(idprofesor, idcurso, idmateria)
    conn = mysql.connection
    cursor = conn.cursor()

    cursor.execute("""
       SELECT idcursomat FROM materiacurso 
            WHERE idcurso=%s AND idmateria=%s
        ;
    """, (idcurso, idmateria))
    id_cursomat = cursor.fetchone()
    
    if id_cursomat:
        id_cursomat_id = id_cursomat[0]
        # Verificar si la materia ya está asignada al profesor
        cursor.execute("""
            SELECT * FROM cursomatprof WHERE idcursomat=%s AND idprofesor=%s
        """, (id_cursomat_id, idprofesor))
        ya_asignada = cursor.fetchone()
        if not ya_asignada:
            # Realizar la inserción
            try:
                cursor.execute("""
                    INSERT INTO cursomatprof (idcursomat, idprofesor) VALUES (%s, %s)
                """, (id_cursomat_id, idprofesor))
                conn.commit()
                
            except Exception as e:
                print("Error al insertar:", e)
        
        else:
            print("La materia ya estaba asignada al profesor o no fue eliminada.")
    else:
            print("No se encontró la materia en el curso con esos datos, o ya fue eliminada.")
    cursor.execute("SELECT a.idprofesor, a.nombprof , a.apellidoprof , e.idcursomat, b.idcurso, b.nombcurso , c.idmateria, c.nombmateria FROM profesor a JOIN cursomatprof e ON e.idprofesor = a.idprofesor JOIN materiacurso d ON e.idcursomat = d.idcursomat JOIN materia c ON c.idmateria = d.idmateria JOIN curso b ON b.idcurso = d.idcurso WHERE a.idprofesor = %s;", (idprofesor,))
    cursomatprof = cursor.fetchall()
    cursor.execute("SELECT mc.idcursomat, mc.idcurso, c.nombcurso, mc.idmateria, m.nombmateria from materiacurso mc, materia m, curso c where c.idcurso=mc.idcurso AND mc.idmateria=m.idmateria AND mc.idcursomat NOT IN (SELECT idcursomat FROM `cursomatprof` where idprofesor = %s);", (idprofesor,))
    cursomatnoasignadas = cursor.fetchall()
    cursor.execute("SELECT * FROM empresa")
    empresa = cursor.fetchone()
    cursor.close()
    if cursomatprof:
        return render_template('colegio/listmatcurprof.html', cursomatprof=cursomatprof, cursomatnoasignadas = cursomatnoasignadas, empresa=empresa,)
    else:
        return redirect('/indexprof')  # Redirigir a la ruta deseada           
    


#--------------------------------------------------------------------    
# FUNCION PARA ELIMINAR MATERIAS A UN PROFESOR
#--------------------------------------------------------------------    
@app.route('/destroymatprof/<int:idprofesor>,<int:idcurso>,<int:idmateria>', methods=['GET', 'POST'])
def destroymatprof(idprofesor, idcurso, idmateria):
    print(idprofesor, idcurso, idmateria)
    conn = mysql.connection
    cursor = conn.cursor()
    # Verifica si la materia está asignada antes de eliminar
    cursor.execute("""
        SELECT cmp.idcursomat FROM cursomatprof cmp
        WHERE cmp.idprofesor=%s AND cmp.idcursomat IN (
            SELECT mc.idcursomat FROM materiacurso mc
            WHERE mc.idcurso=%s AND mc.idmateria=%s
        );
    """, (idprofesor, idcurso, idmateria))
    asignada = cursor.fetchone()

    if asignada:
        # Realiza la eliminación
        cursor.execute("""
            DELETE FROM cursomatprof WHERE idprofesor=%s AND idcursomat IN (
                SELECT mc.idcursomat FROM materiacurso mc
                WHERE mc.idcurso=%s AND mc.idmateria=%s
            );
        """, (idprofesor, idcurso, idmateria))
        conn.commit()  # Asegúrate de guardar los cambios
        print("Materia eliminada correctamente.")
    else:
        print("La materia no estaba asignada al profesor o ya fue eliminada.")

    cursor.execute("SELECT * FROM `colegio`.`empresa`")
    empresa = cursor.fetchone()
    cursor.execute("SELECT a.idprofesor, a.nombprof , a.apellidoprof , e.idcursomat, b.idcurso, b.nombcurso , c.idmateria, c.nombmateria FROM profesor a JOIN cursomatprof e ON e.idprofesor = a.idprofesor JOIN materiacurso d ON e.idcursomat = d.idcursomat JOIN materia c ON c.idmateria = d.idmateria JOIN curso b ON b.idcurso = d.idcurso WHERE a.idprofesor = %s;", (idprofesor,))
    cursomatprof = cursor.fetchall()
    cursor.execute("SELECT mc.idcursomat, c.idcurso, c.nombcurso, m.idmateria, m.nombmateria from materiacurso mc, materia m, curso c where c.idcurso=mc.idcurso AND mc.idmateria=m.idmateria AND mc.idcursomat NOT IN (SELECT idcursomat FROM `cursomatprof` where idprofesor = %s);", (idprofesor,))
    cursomatnoasignadas = cursor.fetchall()
    cursor.execute("SELECT * FROM empresa")
    empresa = cursor.fetchone()
    cursor.close()
    if cursomatprof:
        return render_template('colegio/listmatcurprof.html', cursomatprof=cursomatprof, cursomatnoasignadas = cursomatnoasignadas, empresa=empresa,)
    else:
        return redirect('/indexprof')  # Redirigir a la ruta deseada
     
 
     

@app.route('/construccion')
def construccion():
    conn = mysql.connection 
    cursor = conn.cursor()
    sql="SELECT * FROM `colegio`.`empresa`"
    cursor.execute(sql) 
    empresa = cursor.fetchone()
    return render_template('colegio/construccion.html', empresa=empresa, )

@app.route('/asignarmateria/<int:idalumno>,<int:idcurso>,<int:idmateria>', methods=['POST'])
def asignarmateria(idalumno, idcurso, idmateria):
    conn = mysql.connection
    cursor = conn.cursor()
    
    # Obtener el idcursomat asociado al idcurso e idmateria
    cursor.execute("SELECT idcursomat FROM materiacurso WHERE idcurso = %s AND idmateria = %s", (idcurso, idmateria))
    cursomat = cursor.fetchone()
    
    if cursomat:
        # Insertar en materialumno
        cursor.execute("INSERT INTO materialumno (idcursomat, idalumno) VALUES (%s, %s)", (cursomat[0], idalumno))
        conn.commit()
        
    cursor.close()
    return redirect(url_for('listarmatalumno', idalumno=idalumno, idcurso=idcurso))

#--------------------------------------------------------------------
# Estas líneas de código las requiere python para que 
# se pueda empezar a trabajar con la aplicación
if __name__ == '__main__':
    # Corremos la aplicación en modo debug
    app.run(debug=True)
#--------------------------------------------------------------------
