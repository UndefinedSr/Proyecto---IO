import streamlit as st
import pandas as pd

st.set_page_config(page_title="SSD Horarios", layout="wide")

st.title("🎓 Sistema de Gestión de Horarios")

# --- 1. CARGA DE DATOS ---
# !!! CAMBIO IMPORTANTE 1: Nombre del archivo actualizado
archivo_excel = 'HorarioColegio1.xlsx' 
nombre_hoja = 'BASE DE DATOS' # Asegúrate que esta hoja exista en el nuevo Excel

try:
    df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    
    # Aseguramos que los grados sean texto (string) para evitar errores si Excel los lee como números
    df['GRADO'] = df['GRADO'].astype(str) 

    # Filtramos solo lo asignado (Donde LINGO puso un 1)
    df = df[df['VALOR'] == 1]

    # --- 2. LÓGICA DE PROFESORES ---
    def asignar_profe(fila):
        grado = fila['GRADO']
        curso = fila['CURSO']
        
        # !!! CAMBIO IMPORTANTE 2: Ajuste a Minúsculas/Mayúsculas
        # Convertimos 'grado' a mayúsculas (.upper()) para asegurar que coincida 
        # sin importar si en Lingo escribiste "1ero" o "1ERO".
        if grado.upper() in ['1ERO', '2DO', '3RO']:
            return f"PROF_{curso}_A"
        else:
            return f"PROF_{curso}_B"

    # Aplicamos la función
    df['PROFESOR'] = df.apply(asignar_profe, axis=1)

    # --- 3. BARRA LATERAL (CONTROLES) ---
    st.sidebar.header("Panel de Control")
    
    tipo_vista = st.sidebar.radio("¿Qué horario desea ver?", ["Por Grado (Alumnos)", "Por Profesor (Docentes)"])

    # --- 4. VISUALIZACIÓN ---
    
    if tipo_vista == "Por Grado (Alumnos)":
        # --- VISTA ORIGINAL ---
        opcion = st.sidebar.selectbox("Seleccione Grado:", sorted(df['GRADO'].unique()))
        st.subheader(f"📅 Horario de Clases: {opcion}")
        
        data_filtrada = df[df['GRADO'] == opcion]
        valor_celda = 'CURSO'

    else:
        # --- NUEVA VISTA DE PROFESORES ---
        opcion = st.sidebar.selectbox("Seleccione Profesor:", sorted(df['PROFESOR'].unique()))
        st.subheader(f"👨‍🏫 Agenda Docente: {opcion}")
        
        data_filtrada = df[df['PROFESOR'] == opcion]
        # Mostramos GRADO en la celda
        valor_celda = 'GRADO'

    # --- 5. ARMADO DE LA MATRIZ (TABLA) ---
    if not data_filtrada.empty:
        # Pivot: Filas=HORA, Columnas=DIA
        matriz = data_filtrada.pivot(index='HORA', columns='DIA', values=valor_celda)

        # Ordenar para que no salga alfabético
        dias_orden = ['LUN', 'MAR', 'MIE', 'JUE', 'VIE']
        horas_orden = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7']
        
        # Reindexamos para forzar el orden correcto
        matriz = matriz.reindex(columns=dias_orden, index=horas_orden)
        matriz = matriz.fillna("-") 

        st.table(matriz)
        
        # Métrica de Carga
        horas_ocupadas = data_filtrada.shape[0]
        
        # Mensaje dinámico según quién sea
        if tipo_vista == "Por Profesor (Docentes)":
             st.info(f"⚡ Carga Laboral: {horas_ocupadas} horas esta semana.")
        else:
             st.success(f"📚 Horas de clase: {horas_ocupadas} horas esta semana.")
        
    else:
        st.warning("No hay horarios asignados para esta selección.")

except FileNotFoundError:
    st.error(f"❌ No se encuentra el archivo '{archivo_excel}'. Verifica que esté en la misma carpeta que este script.")
except Exception as e:
    st.error(f"❌ Ocurrió un error: {e}")