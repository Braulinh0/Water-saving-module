import panda as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Cargas datos
df = pd.read_csv("IA_training.csv")

# Información
X = df[["humedad", "temperatura"]] # Emisores
Y = df["riego_ml"] # Respuesta

# Separamos: 80% para entrenar y 20% para probar qué tan bien generaliza el modelo con datos que NUNCA vio
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size = 0.2, random_state = 42
)

# usamos un random forest para no usar un unico arbol
modelo = RandomForestRegressor(
    n_estimators = 200, 
    max_depth = 8,
    min_samples_leaf = 4,
    random_state = 42
)
modelo.fit(X_train, Y_train)

# Evaluación
predicciones_test = modelo.predict(X_test)
mae = mean_absolute_error(Y_test, predicciones_test)
r2 = r2_score(Y_test, predicciones_test)

print(f"Error promedio (MAE): {mae:.2f} ml")
print(f"R² (qué tan bien explica el patrón, 1.0 = perfecto): {r2:.3f}")

joblib.dump(modelo, "modeloIA_riego.pkl")

print("\nPrueba con temperatura fija en 25°C:")
for i in range(0, 101, 10) :
    pred = modelo.predict([[i, 25]])[0]
    print(f"Humedad {i:>3}% -> {pred:.1f} ml recomendados")