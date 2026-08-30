import csv
import random

# Nombre del archivo
archivo = "IA_training.csv"

# Definimos los encabezados
encabezados = ["humedad", "temperatura", "riego_ml"]

with open(archivo, mode="w", newline="") as f:
    escritor = csv.writer(f)
    escritor.writerow(encabezados)

    for i in range(100):
        # Generamos datos aleatorios realistas
        humedad = random.randint(10, 90)
        temperatura = random.randint(15, 40)
        
        # Lógica para que la IA aprenda (Riego recomendado)
        if humedad > 70:
            riego = 0
        elif humedad < 30 and temperatura > 30:
            riego = random.randint(600, 900)
        elif humedad < 50:
            riego = random.randint(200, 500)
        else:
            riego = random.randint(0, 100)
        
        escritor.writerow([humedad, temperatura, riego])

print(f"✅ ¡Listo! Se ha creado el archivo '{archivo}' con 100 filas de datos.")