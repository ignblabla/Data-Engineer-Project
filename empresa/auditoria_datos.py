import pandas as pd
import re

def detectar_patrones_fecha(serie: pd.Series) -> dict:
    """
    Detecta los distintos formatos/patrones presentes en una columna de fechas (como texto).
    Reemplaza dígitos por 'D' y letras por 'L' para agrupar formatos equivalentes.
    """
    def a_patron(valor: str) -> str:
        valor = re.sub(r'\d', 'D', valor)
        valor = re.sub(r'[A-Za-z]', 'L', valor)
        return valor

    patrones = serie.dropna().astype(str).apply(a_patron)
    return patrones.value_counts().to_dict()


def detectar_columnas_fecha(df:pd.DataFrame) -> list:
    palabras_clave = ('fecha', 'date', '_at','timestamp')
    return [col for col in df.columns if any(p in col.lower() for p in palabras_clave)]


def auditoria(df: pd.DataFrame, nombre: str) -> dict:
    """Genera un resumen de calidad básico de un DataFrame."""
    total_filas = df.shape[0]
    total_columnas = df.shape[1]
    total_nulos = df.isnull().sum().sum()
    total_celdas = total_filas * total_columnas

    nulos_por_columna = df.isnull().sum()
    nulos_por_columna = nulos_por_columna[nulos_por_columna > 0].to_dict()

    filas_vacias = df.isnull().all(axis=1).sum()

    columnas_fecha = detectar_columnas_fecha(df)
    analisis_fechas = {}
    for col in columnas_fecha:
        analisis_fechas[col] = {
            'patrones': detectar_patrones_fecha(df[col]),
        }

    return {
        'archivo': nombre,
        'total_filas': total_filas,
        'total_columnas': total_columnas,
        'tipos_de_datos': df.dtypes.astype(str).to_dict(),
        'filas_duplicadas': df.duplicated().sum(),
        'total_nulos': total_nulos,
        'porcentaje_nulos': round((total_nulos / total_celdas) * 100, 2) if total_celdas > 0 else 0,
        'nulos_por_columna': nulos_por_columna,
        'filas_vacias': filas_vacias,
        'analisis_fechas': analisis_fechas,
    }


def imprimir_resumen(resumen: dict) -> None:
    """Imprime el resumen de forma legible, separando las secciones más densas."""
    print(f"\n{'='*80}")
    print(f"  {resumen['archivo'].upper()}")
    print(f"{'='*80}")

    campos_simples = [
        'total_filas', 'total_columnas', 'filas_duplicadas', 'total_nulos', 'porcentaje_nulos',
    ]
    for k in campos_simples:
        print(f"  {k}: {resumen[k]}")

    print("\n  --- Tipos de datos ---")
    for col, tipo in resumen['tipos_de_datos'].items():
        print(f"    {col}: {tipo}")

    if resumen['nulos_por_columna']:
        print("\n  --- Nulos por columna ---")
        for col, n in resumen['nulos_por_columna'].items():
            print(f"    {col}: {n}")
    else:
        print("\n  --- Nulos por columna: ninguno ---")

    if resumen['analisis_fechas']:
        print("\n  --- Análisis de columnas de fecha ---")
        for col, info in resumen['analisis_fechas'].items():
            print(f"    {col}:")
            n_patrones = len(info['patrones'])
            if n_patrones > 1:
                print(f"      ⚠ {n_patrones} formatos distintos detectados:")
            else:
                print(f"      1 formato detectado:")
            for patron, count in info['patrones'].items():
                print(f"        {patron}: {count} valores")


archivos = {
    'clientes': 'datos/campana_verano_ventas.csv'
}


for nombre, ruta in archivos.items():
    df = pd.read_csv(ruta)
    resumen = auditoria(df, nombre)
    imprimir_resumen(resumen)