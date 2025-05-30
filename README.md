# MKT ANALYSIS

## Obtención de Cotizaciones de Bonos Argentinos en BYMA y Cálculo del Dólar MEP

Este repositorio contiene scripts para analizar datos de mercado financiero argentino.

### Scripts disponibles

1. **byma_bonos.py**: Conecta directamente con la API de BYMA
   - Obtiene cotizaciones de bonos soberanos, letras del tesoro y obligaciones negociables
   - Mayor confiabilidad al usar la API oficial
   - Guarda los resultados en archivos CSV separados y un archivo consolidado

2. **dolar_mep.py**: Calcula el dólar MEP usando bonos en pesos y dólares
   - Filtra bonos AL (pesos) y su versión en dólares (AL30D)
   - Calcula el tipo de cambio MEP dividiendo precio en pesos / precio en dólares
   - Genera un reporte detallado con la cotización promedio, mínima y máxima

3. **bonos_byma.py**: Método alternativo usando web scraping
   - Intenta extraer datos de varias fuentes web
   - Método de respaldo si la API directa no funciona

### Cómo usar byma_bonos.py

1. Instalar las dependencias necesarias:
   ```
   pip install -r requirements.txt
   ```

2. Ejecutar el script para obtener las cotizaciones:
   ```
   python byma_bonos.py
   ```

3. El script creará una carpeta "datos_bonos" con los siguientes archivos:
   - `bonos_publicos_YYYYMMDD.csv`: Bonos soberanos
   - `letras_tesoro_YYYYMMDD.csv`: Letras del tesoro
   - `obligaciones_negociables_YYYYMMDD.csv`: Obligaciones negociables
   - `todos_bonos_YYYYMMDD.csv`: Archivo consolidado con todos los instrumentos

### Cómo calcular el Dólar MEP

1. Ejecutar el script para obtener las cotizaciones y calcular el Dólar MEP:
   ```
   python dolar_mep.py
   ```

2. El script:
   - Obtiene los bonos de BYMA
   - Filtra los bonos AL en pesos (ej. AL30) y su versión en dólares (ej. AL30D)
   - Busca pares de bonos con la misma numeración
   - Calcula el tipo de cambio MEP dividiendo el precio en pesos por el precio en dólares
   - Genera un promedio de cotización

3. Los resultados se guardan en la carpeta "resultados_mep":
   - `bonos_pesos_YYYYMMDD.csv`: Bonos en pesos filtrados
   - `bonos_dolares_YYYYMMDD.csv`: Bonos en dólares filtrados
   - `dolar_mep_YYYYMMDD.csv`: Cálculo detallado para cada par de bonos
   - `cotizacion_mep_YYYYMMDD.txt`: Resumen con la cotización promedio

### Características

- Acceso directo a la API de BYMA sin necesidad de autenticación
- Obtiene información completa: precio, variación, volumen, etc.
- Maneja errores de conexión y problemas con los datos
- Cálculo automático del Dólar MEP con bonos compatibles

### Requisitos

- Python 3.6+
- Bibliotecas: requests, pandas, urllib3
