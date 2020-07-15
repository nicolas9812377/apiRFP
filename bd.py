import psycopg2
from config import config
from datetime import datetime

def conectar():
    """ Conexión al servidor de pases de datos PostgreSQL """
    conexion = None
    try:
        # Lectura de los parámetros de conexion
        params = config()
        # Conexion al servidor de PostgreSQL
        print('Conectando a la base de datos PostgreSQL...')
        conexion = psycopg2.connect(**params)    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        cerrar()
    return conexion
        
    

def consulta(conexion,id_persona):
    # creación del cursor
    cur = conexion.cursor()
       
    # Ejecución de una consulta con la version de PostgreSQL
    cur.execute('select persona.id_persona,nombres_persona,apellidos_persona,cedula_persona from fotos, persona where fotos.id_persona = persona.id_persona  and persona.id_persona = '+id_persona+'group by persona.id_persona,nombres_persona,apellidos_persona,cedula_persona')
    
    # Recorremos los resultados y los mostramos
    personas = []
    fotos = []
    for id_persona in cur.fetchall() :
        cur.execute('SELECT foto from fotos where id_persona = '+str(id_persona[0]))
        foto = cur.fetchone()
        personas.append(id_persona[1].strip()+" "+id_persona[2].strip())
        personas.append(id_persona[3])
        fotos.append(foto[0])    
        
    # Cierre de la comunicación con PostgreSQL
    cur.close()
    return personas,fotos



def validar(conexion,cedula):
    # creación del cursor
    cur = conexion.cursor()
    
    #obtener fecha y año actual
    date = datetime.now()
    anio = date.year
    mesn = date.month
    mes=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    # Ejecución de una consulta con la version de PostgreSQL
    cur.execute("select * from cobros,persona where cobros.id_persona = persona.id_persona and persona.cedula_persona = '"+str(cedula)+"' and mes_pago = '"+mes[mesn-1]+"' and anio_pago = '"+str(anio)+"' and estado = '"+'Pagado'+"'")

    alicuota = cur.fetchall()
    if(len(alicuota) == 0):
        return False
    if(len(alicuota) == 1):
        return True 
    # Cierre de la comunicación con PostgreSQL
    cur.close()
    return False

#Registro Entrada-Salida
def registro(conexion,cedula,acceso):
    # creación del cursor
    cur = conexion.cursor()

    cur.execute("select habitante_vivienda.num_vivienda,habitante_vivienda.id_tipo_vivienda,habitante_vivienda.id_persona,habitante_vivienda.id_tipo_persona,habitante_vivienda.id_estado_acceso from habitante_vivienda,persona where persona.id_persona = habitante_vivienda.id_persona and persona.cedula_persona = '" + str(cedula)+"'")
    # Ejecución de una consulta con la version de PostgreSQL
    habitante = cur.fetchall()
    date = datetime.now()
    try:
        cur.execute("INSERT INTO detalle_acceso(num_vivienda, id_tipo_vivienda, id_persona, id_tipo_persona, id_estado_acceso, fecha_ingreso_salida, hora_ingreso_salida,detalle_acceso) VALUES ('"+habitante[0]+"',"+habitante[1]+","+habitante[2]+","+habitante[3]+","+habitante[4]+",'"+str(date.date())+"','"+str(date.time())+"','"+ acceso+"')")
        # Cierre de la comunicación con PostgreSQL
        cur.close()
        return True

    except Exception as err:
        print(err)
        # Cierre de la comunicación con PostgreSQL
        cur.close()
        return False
    


def cerrar(conexion):
    if conexion is not None:
        conexion.close()
        print('Conexión finalizada.')