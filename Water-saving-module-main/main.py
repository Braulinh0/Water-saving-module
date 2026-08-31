import csv
import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
import joblib
from fastapi.middleware.cors import CORSMiddleware
import requests

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
Ciudad = os.getenv("CIUDAD", "Santiago,CL")

# Funcion del Clima de Internet

def obtener_temperatura_api():
    if not API_KEY :
        print("No se encontró la API-KEY. Revisa tu .env")
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={Ciudad}&appid={API_KEY}&units=metric"
        respuesta = requests.get(url, timeout = 5).json()
        temp_real = respuesta["main"]["temp"]
        return temp_real
    except Exception as e:
        print(f"Error al consultar clima: {e}")
        return None

# Modelo
try :
    modelo = joblib.load("modeloIA_riego.pkl")
except FileNotFoundError :
    print("No se encontró modeloIA_riego.pkl. Ejecuta ia_training.py primero.")
    modelo = None

# Molde
class DatosSensor(BaseModel):
    humedad_tierra: float = Field(ge=0, le=100)
    temperatura_ambiental: float = Field(ge=-20, le=60)

#Aplicacion
app = FastAPI()

# Ruta
@app.get("/")
def home():
    return {
        "mensaje" : "Open Server"
    }
    
@app.get("/health")
def health():
    return {"status": "ok"}
    
def leer_raiz():
    return {"mensaje": "Open Server"}

#POST
@app.post("/recibir-datos")

#Receptor

def recibir_datos_sensor(datos: DatosSensor):
    if modelo is None :
        return {
            "error" : "El modelo de IA no está cargado. Ejecuta ia_training.py."
        }
        
    # Temperatura real
    temp_api = obtener_temperatura_api()

    # Desicion de la API o Local

    if temp_api is not None:
        temp_para_ia = temp_api
        origen = "Internet (API)"
    else:
        temp_para_ia = datos.temperatura_ambiental # Fallback al sensor si no hay internet.
        origen = "Sensor local"

    datos_df = pd.DataFrame([[datos.humedad_tierra, temp_para_ia]],
                            columns=['humedad', 'temperatura'])
    
    #Prediccion del algoritmo especializado.

    prediccion = modelo.predict(datos_df)
    ml_recomendado = round(float(prediccion[0]), 2)

    # Emision del algoritmo especializado y entrenado por horas.

    if ml_recomendado == 0:
        aviso = "La tierra esta en condiciones ideales, no es necesario regar"
    else:
        aviso = f"La tierra requiere riego, se recomienda aplicar {ml_recomendado} ml de agua."

    # Hora

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    fila = [ahora, datos.humedad_tierra, temp_para_ia, ml_recomendado]
    
    # Historial de Riego

    with open("historial_riego.csv", mode="a", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(fila)
    
    print(f"Datos guardados: {datos.humedad_tierra}%, {temp_para_ia}°C, {ml_recomendado}ml")
    return{"estado": "guardado", 
           "fecha":ahora,
           "origen": origen,
           "humedad_recibida": datos.humedad_tierra,
        "temperatura_recibida": temp_para_ia,
        "riego_ml": ml_recomendado,
        "recomendacion": aviso}

@app.get("/obtener-datos")
def obtener_datos():
    try:
        # 1. Leemos el archivo
        df_historial = pd.read_csv("historial_riego.csv", names=["fecha", "humedad", "temperatura", "riego_ml"])
        
        # 2. ESCUDO ANTI-ERRORES: Borramos cualquier fila que esté vacía (que tenga 'nan')
        df_historial = df_historial.dropna()
        
        # 3. Verificamos que hayan quedado datos después de limpiar
        if df_historial.empty:
            return {"error": "El historial está vacío"}

        # 4. Tomamos el último dato válido
        ultimo_dato = df_historial.iloc[-1].to_dict() 
        
        # 5. Generamos el aviso
        if float(ultimo_dato['riego_ml']) == 0:
            aviso = "La tierra está en condiciones ideales"
        else:
            aviso = f"Se recomienda aplicar {ultimo_dato['riego_ml']} ml de agua."
            
        ultimo_dato["recomendacion"] = aviso
        return ultimo_dato
        
    except Exception as e:
        return {"error": f"Error leyendo historial: {str(e)}"}


# PERMITIR QUE EL FRONTEND SE CONECTE

# En producción, reemplazar "*" por el dominio real del frontend, ej: allow_origins=["https://tu-dashboard.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite cualquier origen (para desarrollo)
    allow_methods=["*"],
    allow_headers=["*"],
)
