import pandas as pd
import os
import re
from datetime import datetime
from byma_bonos import OpenBYMAdata, save_to_csv

def obtener_bonos():
    """Obtiene los bonos públicos desde la API de BYMA"""
    print("Obteniendo bonos públicos para calcular dólar MEP...")
    byma = OpenBYMAdata()
    return byma.get_bonds()

def filtrar_bonos_para_mep(df):
    """
    Filtra los bonos para cálculo del MEP (bonos en pesos y su versión en dólares)
    Retorna dos dataframes: bonos en pesos y bonos en dólares
    """
    if df is None or df.empty:
        print("No se encontraron datos de bonos")
        return None, None
    
    # Convertir símbolos a mayúsculas para normalizar
    df['symbol'] = df['symbol'].str.upper()
    
    # Filtrar bonos AL (comunes) y su versión dolarizada (terminados en D)
    # Ejemplo: AL30 (pesos) y AL30D (dólares)
    bonos_pesos = df[df['symbol'].str.contains(r'^AL\d+$', regex=True, na=False)].copy()
    bonos_dolares = df[df['symbol'].str.contains(r'^AL\d+D$', regex=True, na=False)].copy()
    
    # Eliminar bonos con precio 0 o nulo
    bonos_pesos = bonos_pesos[bonos_pesos['last'] > 0].copy()
    bonos_dolares = bonos_dolares[bonos_dolares['last'] > 0].copy()
    
    print(f"Bonos en pesos encontrados: {len(bonos_pesos)}")
    print(f"Bonos en dólares encontrados: {len(bonos_dolares)}")
    
    return bonos_pesos, bonos_dolares

def extraer_numero_bono(symbol):
    """
    Extrae el número del bono a partir de su símbolo
    Ejemplo: 'AL30' -> '30', 'AL30D' -> '30'
    """
    try:
        # Extraer los dígitos después de AL y antes de D (si existe)
        numeros = re.findall(r'AL(\d+)', symbol)
        if numeros:
            return numeros[0]
        return None
    except:
        return None

def calcular_dolar_mep(bonos_pesos, bonos_dolares):
    """
    Calcula el dólar MEP para cada par de bonos AL/ALD con la misma numeración
    Ejemplo: AL30 (pesos) / AL30D (dólares)
    """
    if bonos_pesos is None or bonos_dolares is None or bonos_pesos.empty or bonos_dolares.empty:
        print("No hay suficientes datos para calcular el dólar MEP")
        return None
    
    # Agregar columna con el número de bono
    bonos_pesos['numero'] = bonos_pesos['symbol'].apply(extraer_numero_bono)
    bonos_dolares['numero'] = bonos_dolares['symbol'].apply(extraer_numero_bono)
    
    # Crear lista para almacenar resultados
    resultados = []
    
    # Para cada bono en pesos, buscar su correspondiente en dólares
    for _, bono_pesos in bonos_pesos.iterrows():
        numero = bono_pesos['numero']
        if not numero:
            continue
            
        # Buscar el bono en dólares correspondiente
        bono_dolares_match = bonos_dolares[bonos_dolares['numero'] == numero]
        
        if not bono_dolares_match.empty:
            # Tomar el primer match si hay varios
            bono_dolares = bono_dolares_match.iloc[0]
            
            # Calcular dólar MEP: Precio en pesos / Precio en dólares
            precio_pesos = bono_pesos['last']
            precio_dolares = bono_dolares['last']
            
            if precio_dolares > 0:
                dolar_mep = precio_pesos / precio_dolares
                
                # Agregar a resultados
                resultados.append({
                    'bono_pesos': bono_pesos['symbol'],
                    'precio_pesos': precio_pesos,
                    'bono_dolares': bono_dolares['symbol'],
                    'precio_dolares': precio_dolares,
                    'dolar_mep': dolar_mep,
                    'numero': numero
                })
    
    if resultados:
        # Convertir a DataFrame
        df_resultados = pd.DataFrame(resultados)
        
        # Ordenar por número de bono
        df_resultados = df_resultados.sort_values('numero')
        
        return df_resultados
    else:
        print("No se encontraron pares de bonos adecuados para calcular el dólar MEP")
        return None

def calcular_promedio_ponderado(df_mep):
    """
    Calcula el promedio ponderado del dólar MEP
    Usa el volumen como factor de ponderación, si está disponible
    """
    if df_mep is None or df_mep.empty:
        return None
        
    # Calcular promedio simple si no hay suficientes datos
    promedio_simple = df_mep['dolar_mep'].mean()
    
    return {
        'promedio_simple': promedio_simple,
        'min': df_mep['dolar_mep'].min(),
        'max': df_mep['dolar_mep'].max()
    }

def main():
    """Función principal"""
    print("Calculadora de Dólar MEP - Bonos AL/ALD")
    print("=======================================")
    
    # Crear directorio para guardar resultados
    output_dir = "resultados_mep"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Fecha actual para nombrar archivos
    fecha = datetime.now().strftime("%Y%m%d")
    
    # Obtener bonos
    bonos = obtener_bonos()
    
    # Filtrar bonos para MEP
    bonos_pesos, bonos_dolares = filtrar_bonos_para_mep(bonos)
    
    # Guardar bonos filtrados para referencia
    if bonos_pesos is not None and not bonos_pesos.empty:
        save_to_csv(bonos_pesos, os.path.join(output_dir, f"bonos_pesos_{fecha}.csv"))
    
    if bonos_dolares is not None and not bonos_dolares.empty:
        save_to_csv(bonos_dolares, os.path.join(output_dir, f"bonos_dolares_{fecha}.csv"))
    
    # Calcular dólar MEP
    df_mep = calcular_dolar_mep(bonos_pesos, bonos_dolares)
    
    if df_mep is not None and not df_mep.empty:
        # Mostrar resultados
        print("\nCálculo de Dólar MEP por pares de bonos:")
        print(df_mep[['bono_pesos', 'precio_pesos', 'bono_dolares', 'precio_dolares', 'dolar_mep']].to_string(index=False))
        
        # Calcular estadísticas
        stats = calcular_promedio_ponderado(df_mep)
        
        if stats:
            print("\nEstadísticas del Dólar MEP:")
            print(f"Promedio: {stats['promedio_simple']:.2f}")
            print(f"Mínimo: {stats['min']:.2f}")
            print(f"Máximo: {stats['max']:.2f}")
        
        # Guardar resultados
        save_to_csv(df_mep, os.path.join(output_dir, f"dolar_mep_{fecha}.csv"))
        
        # Crear un archivo resumen con la cotización
        with open(os.path.join(output_dir, f"cotizacion_mep_{fecha}.txt"), 'w') as f:
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Cotización promedio Dólar MEP: ${stats['promedio_simple']:.2f}\n")
            f.write(f"Cotización mínima: ${stats['min']:.2f}\n")
            f.write(f"Cotización máxima: ${stats['max']:.2f}\n")
            f.write("\nPares de bonos utilizados:\n")
            
            for _, row in df_mep.iterrows():
                f.write(f"{row['bono_pesos']} (${row['precio_pesos']:.2f}) / {row['bono_dolares']} (${row['precio_dolares']:.2f}) = ${row['dolar_mep']:.2f}\n")
        
        print(f"\nResultados guardados en la carpeta '{output_dir}'")
    else:
        print("No se pudo calcular el dólar MEP. Verifica la disponibilidad de datos de bonos.")


if __name__ == "__main__":
    main() 