from flask import Flask,request
from deepface import DeepFace
from deepface.basemodels import VGGFace
import json 
import base64
from PIL import Image
from io import BytesIO
import bd as base
import os

##iniciar conexion con bd
conexion = base.conectar()

#--------------------------------
#-----Obtener Todas las fotos----
"""
personas,fotos = base.consulta(conexion)
for x,ft in enumerate(fotos):
   os.makedirs('Data/'+personas[x], exist_ok=True)
   with open('Data/'+personas[x]+'/imagen.jpg', 'wb') as f:
     f.write(base64.b64decode(ft.replace('data:image/jpg;base64,','')))
"""

##inicia flask
app = Flask(__name__)

#modelo a ocupar
vggface_model = VGGFace.loadModel()

#ruta inicial
@app.route('/',methods=['GET'])
def hello_world():
  if request.method == 'GET':
    print(request.values.get('id_persona'))
    personas,fotos = base.consulta(conexion,request.values.get('id_persona'))
    if os.path.exists('Data/representations_vgg_face.pkl'):
      os.remove('Data/representations_vgg_face.pkl',dir_fd=None)    
    os.makedirs('Data/'+personas[0]+'-'+personas[1], exist_ok=True)
    with open('Data/'+personas[0]+'-'+personas[1]+'/imagen.jpg', 'wb') as f:
      f.write(base64.b64decode(fotos[0].replace('data:image/jpg;base64,','').replace('data:image/png;base64,','')))
  return {"ok": 200},200

#rutar para verificar
@app.route('/verify',methods=['POST'])
def verify():
    if request.method == 'POST':
      #obtener como parametro la foto
      photob64 = request.values.get('Foto')
      #reemplazar caracteres de base64 en urlbase64
      photob64 = photob64.replace('+','-').replace('/','_')
      #decodifico 
      photob64 = base64.urlsafe_b64decode(photob64 + '=' * (4 - len(photob64) % 4))
      #guardo img
      with open('app.jpg', 'wb') as f:
        f.write(photob64)
      try:
        #proceso de reconocimiento facial
        resp = DeepFace.find('app.jpg','Data', model_name = "VGG-Face", distance_metric = "cosine", model = vggface_model)

        #Obtencion de reconocimiento 
        temp = resp.iloc[0]['identity'] 
        temp = temp.replace('\\','/').split('/')        
        temp = temp[1].split('-')
        
        if(base.validar(conexion,temp[1])):
          base.registro(conexion,temp[1],'Acceso Autorizado')
          return { "estado" : "Acceso Autorizado", "nombre" : temp[0]},200
        else:
          base.registro(conexion,temp[1],'Acceso Restringido por Falta de Pago')
          return { "estado" : "Acceso Restringido por Falta de Pago", "nombre" : temp[0]},200
      except Exception as err:
        print("Error")
        print(err)
        return { "estado" : "Acceso No Autorizado", "nombre" : "Desconocido"},200    

#ejecucion servidor
if __name__ == '__main__': 
  app.run() 
