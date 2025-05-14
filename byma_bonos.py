import json
import requests
import urllib3
import pandas as pd
from datetime import datetime
import os

# Desactivar advertencias SSL
urllib3.disable_warnings()


class OpenBYMAdata:
    def __init__(self):
        # Columnas y configuración para los datos de bonos
        self.__fixedIncome_columns = ['symbol', 'settlement', 'bid_size', 'bid', 'ask', 'ask_size', 'last', 'close', 'change', 'open', 'high', 'low', 'previous_close', 'turnover', 'volume', 'operations', 'datetime', 'group', "expiration"]
        self.__filter_columns_fixedIncome = ["symbol", "settlementType", "quantityBid", "bidPrice", "offerPrice", "quantityOffer", "settlementPrice", "closingPrice", "imbalance", "openingPrice", "tradingHighPrice", "tradingLowPrice", "previousClosingPrice", "volumeAmount", "volume", "numberOfOrders", "tradeHour", "securityType", "maturityDate"]
        self.__numeric_columns = ['last', 'open', 'high', 'low', 'volume', 'turnover', 'operations', 'change', 'bid_size', 'bid', 'ask_size', 'ask', 'previous_close']

        # Configuración de la sesión
        self.__s = requests.session()
        self.__s.get('https://open.bymadata.com.ar/#/dashboard', verify=False)
        self.__data='{"excludeZeroPxAndQty":false,"T2":false,"T1":true,"T0":false,"Content-Type":"application/json"}'

        # Configuración de headers
        self.__headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://open.bymadata.com.ar',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://open.bymadata.com.ar/',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8,en;q=0.7',
        }
        
        # Inicializar diccionario de traducción
        try:
            response = self.__s.get('https://open.bymadata.com.ar/assets/api/langs/es.json', headers=self.__headers, verify=False)
            self.__diction = response.json()
        except:
            self.__diction = {}
            print("No se pudo obtener el diccionario de traducción")

    def get_bonds(self):
        """Obtiene cotizaciones de bonos públicos"""
        return self.__get_fixed_income('public-bonds')

    def get_short_term_bonds(self):
        """Obtiene cotizaciones de letras del tesoro"""
        return self.__get_fixed_income('lebacs')

    def get_corporateBonds(self):
        """Obtiene cotizaciones de obligaciones negociables"""
        return self.__get_fixed_income('negociable-obligations')

    def __get_fixed_income(self, endpoint):
        """Método interno para obtener datos de renta fija"""
        print(f"Obteniendo datos de {endpoint}...")
        
        try:
            response = self.__s.post(
                f'https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/{endpoint}', 
                data=self.__data, 
                headers=self.__headers, 
                verify=False,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"Error al obtener datos: Código {response.status_code}")
                return None
                
            df = pd.DataFrame()
            
            if endpoint == "public-bonds" or endpoint == "lebacs":
                json_data = response.json()
                if 'data' in json_data:
                    df = pd.DataFrame(json_data.get('data', []))
                else:
                    print(f"No se encontraron datos en la respuesta de {endpoint}")
                    return None
            else:
                df = pd.DataFrame(response.json())

            if df.empty:
                print(f"No se encontraron datos para {endpoint}")
                return None
                
            # Filtrar y renombrar columnas
            try:
                df = df[self.__filter_columns_fixedIncome].copy()
                df.columns = self.__fixedIncome_columns
            except KeyError as e:
                print(f"Error al procesar columnas: {e}")
                # Mostrar columnas disponibles
                print(f"Columnas disponibles: {df.columns.tolist()}")
                return None
                
            # Convertir tipos de datos
            df['expiration'] = pd.to_datetime(df['expiration'], errors='coerce')
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            
            # Convertir columnas numéricas
            for col in self.__numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"Se obtuvieron {len(df)} registros de {endpoint}")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión para {endpoint}: {e}")
            return None
        except Exception as e:
            print(f"Error al procesar datos de {endpoint}: {e}")
            return None


def save_to_csv(df, filename):
    """Guarda un DataFrame en un archivo CSV"""
    if df is not None and not df.empty:
        df.to_csv(filename, index=False)
        print(f"Datos guardados en {filename}")
        return True
    return False


def main():
    """Función principal para obtener y guardar cotizaciones de bonos"""
    print("Obteniendo cotizaciones de bonos argentinos en BYMA...")
    
    # Crear directorio para guardar datos si no existe
    output_dir = "datos_bonos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Fecha actual para nombrar archivos
    fecha = datetime.now().strftime("%Y%m%d")
    
    # Inicializar la clase para acceder a BYMA
    byma = OpenBYMAdata()
    
    # Obtener bonos públicos
    bonos_publicos = byma.get_bonds()
    if bonos_publicos is not None:
        # Mostrar una vista previa
        print("\nVista previa de bonos públicos:")
        print(bonos_publicos[['symbol', 'last', 'change', 'bid', 'ask', 'volume']].head())
        # Guardar a CSV
        save_to_csv(bonos_publicos, os.path.join(output_dir, f"bonos_publicos_{fecha}.csv"))
    
    # Obtener letras del tesoro
    letras = byma.get_short_term_bonds()
    if letras is not None:
        # Mostrar una vista previa
        print("\nVista previa de letras del tesoro:")
        print(letras[['symbol', 'last', 'change', 'bid', 'ask', 'volume']].head())
        # Guardar a CSV
        save_to_csv(letras, os.path.join(output_dir, f"letras_tesoro_{fecha}.csv"))
    
    # Obtener obligaciones negociables
    obligaciones = byma.get_corporateBonds()
    if obligaciones is not None:
        # Mostrar una vista previa
        print("\nVista previa de obligaciones negociables:")
        print(obligaciones[['symbol', 'last', 'change', 'bid', 'ask', 'volume']].head())
        # Guardar a CSV
        save_to_csv(obligaciones, os.path.join(output_dir, f"obligaciones_negociables_{fecha}.csv"))
    
    # Crear un DataFrame combinado con todos los bonos
    print("\nCreando archivo combinado de todos los bonos...")
    dfs = []
    
    if bonos_publicos is not None:
        bonos_publicos['tipo'] = 'BONOS SOBERANOS'
        dfs.append(bonos_publicos)
    
    if letras is not None:
        letras['tipo'] = 'LETRAS DEL TESORO'
        dfs.append(letras)
    
    if obligaciones is not None:
        obligaciones['tipo'] = 'OBLIGACIONES NEGOCIABLES'
        dfs.append(obligaciones)
    
    if dfs:
        todos_bonos = pd.concat(dfs, ignore_index=True)
        save_to_csv(todos_bonos, os.path.join(output_dir, f"todos_bonos_{fecha}.csv"))
        print(f"\nTotal de bonos obtenidos: {len(todos_bonos)}")
    else:
        print("No se pudo obtener ninguna información de bonos")


if __name__ == "__main__":
    main() 