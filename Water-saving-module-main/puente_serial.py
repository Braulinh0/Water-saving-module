import serial
import requests
import time

#Configuracion del puerto (se debe seleccionar segun OS)

puerto = 'COM3' #COM1, COM2, COM3... para Windows y /dev/tty/USB0, ~/USB1... para Linux y Mac
velocidad = 9600

try:
    arduino = serial.Serial(puerto, velocidad, timeout=1)
    print(f"Sensor Conectado y Activado en {puerto}")
except:
    print(f"EWW Eta mal")
    exit()

#URL de API

url = "http://127.0.0.1:8000/recibir-datos"

while True:
    if arduino.in_waiting > 0:
        #Lectura del microcontrolador
        linea = arduino.readline().decode('utf-8').strip()
        print(f"Dato recibido: {linea}")

        try:

            valores = linea.split(',')
            if len(valores) >= 2:
                humedad = float(valores[0])
                temperatura = float(valores[1])

            payload = {
                "humedad_tierra": humedad,
                "temperatura_ambiental": temperatura
            }

            #Emitir Datos
            respuesta = requests.post(url, json=payload)

            if respuesta.status_code == 200:
                datos_ia = respuesta.json()
                print(f"Emitido a FastAPI, respuesta de la IA: {datos_ia['riego_ml']} ml")
            else:
                print("No se a podido emitir los datos")
        
        except Exception as e:
            print(f"Error al procesar el dato: {e}")
    
    time.sleep(0.1)