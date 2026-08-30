from main import obtener_temperatura_api

def test_temperatura_api_no_rompe() :
    resultado = obtener_temperatura_api()
    assert resultado is None or isinstance(resultado, float)