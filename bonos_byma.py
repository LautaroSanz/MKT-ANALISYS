import requests
import pandas as pd
from datetime import datetime
import urllib3
import time
from bs4 import BeautifulSoup

# Desactivar advertencias de inseguridad para requests sin verificación
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_byma_bonds_from_web():
    """
    Obtiene información de bonos directamente del sitio web de BYMA
    utilizando requests y pandas para extraer tablas
    """
    print("Obteniendo datos de bonos desde la web de BYMA...")
    
    # URL de la página de bonos de BYMA
    url = "https://www.byma.com.ar/productos/bonos/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }
    
    try:
        # Realizar la solicitud a la página web
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            print("Conexión exitosa a la página de bonos de BYMA")
            
            # Intentamos extraer las tablas de HTML
            tables = pd.read_html(response.text)
            
            if tables:
                print(f"Se encontraron {len(tables)} tablas en la página")
                
                # Buscamos la tabla que contiene información de bonos
                for i, table in enumerate(tables):
                    print(f"Tabla {i+1}: {table.shape[0]} filas x {table.shape[1]} columnas")
                    
                    # Si la tabla tiene datos relevantes (más de 3 columnas y filas)
                    if table.shape[0] > 3 and table.shape[1] > 3:
                        print(f"Usando tabla {i+1} como fuente de datos")
                        return table
                
                # Si no encontramos una tabla adecuada, usamos la primera tabla con datos
                if len(tables) > 0 and tables[0].shape[0] > 0:
                    print("Usando la primera tabla disponible")
                    return tables[0]
                    
            else:
                print("No se encontraron tablas en la página")
                
                # Intentamos extraer la información usando BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Intentamos extraer datos de cualquier tabla
                tables_html = soup.find_all('table')
                
                if tables_html:
                    print(f"Se encontraron {len(tables_html)} tablas con BeautifulSoup")
                    
                    # Construimos manualmente un DataFrame a partir de la primera tabla
                    headers = []
                    rows = []
                    
                    table = tables_html[0]
                    
                    # Obtener encabezados
                    th_tags = table.find_all('th')
                    if th_tags:
                        headers = [th.get_text().strip() for th in th_tags]
                    else:
                        # Si no hay encabezados, usar la primera fila
                        headers = [td.get_text().strip() for td in table.find('tr').find_all('td')]
                    
                    # Obtener filas
                    tr_tags = table.find_all('tr')[1:] if th_tags else table.find_all('tr')[1:]
                    for tr in tr_tags:
                        rows.append([td.get_text().strip() for td in tr.find_all('td')])
                    
                    # Crear DataFrame
                    if headers and rows:
                        return pd.DataFrame(rows, columns=headers)
        else:
            print(f"Error al conectar a la página: código {response.status_code}")
        
    except Exception as e:
        print(f"Error al procesar datos de la web: {e}")
    
    return None

def get_bonds_from_iol():
    """
    Intenta obtener datos de bonos desde la plataforma IOL
    """
    print("\nIntentando obtener datos desde IOL...")
    
    url = "https://www.invertironline.com/mercado/cotizaciones/argentina/bonos/todos"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            print("Conexión exitosa a IOL")
            
            # Extraer tablas
            tables = pd.read_html(response.text)
            
            if tables:
                print(f"Se encontraron {len(tables)} tablas en IOL")
                
                # La tabla principal de bonos suele ser la más grande
                largest_table = None
                max_rows = 0
                
                for i, table in enumerate(tables):
                    print(f"Tabla {i+1}: {table.shape[0]} filas x {table.shape[1]} columnas")
                    
                    if table.shape[0] > max_rows:
                        max_rows = table.shape[0]
                        largest_table = table
                
                if largest_table is not None and largest_table.shape[0] > 5:
                    print(f"Usando la tabla más grande con {max_rows} filas")
                    return largest_table
            
            print("No se encontraron tablas válidas en IOL")
    
    except Exception as e:
        print(f"Error al obtener datos de IOL: {e}")
    
    return None

def save_to_csv(df, filename=None):
    """
    Save the DataFrame to a CSV file
    """
    if df is not None:
        if filename is None:
            today = datetime.now().strftime("%Y%m%d")
            filename = f"bonos_byma_{today}.csv"
        
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        return True
    return False

if __name__ == "__main__":
    # Intentar obtener datos de BYMA
    bonds_df = get_byma_bonds_from_web()
    
    # Si no funciona BYMA, intentar con IOL
    if bonds_df is None or bonds_df.empty:
        bonds_df = get_bonds_from_iol()
    
    if bonds_df is not None and not bonds_df.empty:
        # Display the first few rows
        print(f"\nTotal bonds retrieved: {len(bonds_df)}")
        print("\nSample of the data:")
        print(bonds_df.head())
        
        # Save to CSV
        if save_to_csv(bonds_df):
            print("\nDatos guardados exitosamente")
    else:
        print("\nNo se pudieron obtener datos de bonos. Por favor, intente más tarde o verifique su conexión a internet.") 