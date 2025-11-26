import streamlit as st
import pandas as pd

st.set_page_config(page_title="SSD Horarios", layout="wide")

st.title("🎓 Sistema de Gestión de Horarios")

# --- 1. CARGA DE DATOS ---
archivo_excel = 'HorarioColegio.xlsx'
nombre_hoja = 'BASE DE DATOS' 

try:
    df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    # Filtramos solo lo asignado
    df = df[df['VALOR'] == 1]

    # --- 2. LÓGICA DE PROFESORES (NUEVO) ---
    # Creamos una función para asignar el nombre del profesor según tu regla
    def asignar_profe(fila):
        grado = fila['GRADO']
        curso = fila['CURSO']
        
        # Tu regla: 1ro, 2do, 3ro -> Profesor A | 4to, 5to -> Profesor B
        if grado in ['1ERO', '2DO', '3RO']:
            return f"PROF_{curso}_A"
        else:
            return f"PROF_{curso}_B"

    # Aplicamos la función para crear una nueva columna "PROFESOR" en memoria
    df['PROFESOR'] = df.apply(asignar_profe, axis=1)

    # --- 3. BARRA LATERAL (CONTROLES) ---
    st.sidebar.header("Panel de Control")
    
    # Selector de VISTA (La clave de tu pregunta)
    tipo_vista = st.sidebar.radio("¿Qué horario desea ver?", ["Por Grado (Alumnos)", "Por Profesor (Docentes)"])

    # --- 4. VISUALIZACIÓN ---
    
    if tipo_vista == "Por Grado (Alumnos)":
        # --- VISTA ORIGINAL ---
        opcion = st.sidebar.selectbox("Seleccione Grado:", sorted(df['GRADO'].unique()))
        st.subheader(f"📅 Horario de Clases: {opcion}")
        
        # Filtramos por grado
        data_filtrada = df[df['GRADO'] == opcion]
        # Mostramos CURSO en la celda
        valor_celda = 'CURSO'

    else:
        # --- NUEVA VISTA DE PROFESORES ---
        opcion = st.sidebar.selectbox("Seleccione Profesor:", sorted(df['PROFESOR'].unique()))
        st.subheader(f"👨‍🏫 Agenda Docente: {opcion}")
        
        # Filtramos por profesor
        data_filtrada = df[df['PROFESOR'] == opcion]
        # Mostramos GRADO en la celda (para saber a quién le enseña)
        valor_celda = 'GRADO'

    # --- 5. ARMADO DE LA MATRIZ (TABLA) ---
    if not data_filtrada.empty:
        # Pivot: Filas=HORA, Columnas=DIA
        matriz = data_filtrada.pivot(index='HORA', columns='DIA', values=valor_celda)

        # Ordenar para que no salga alfabético
        dias_orden = ['LUN', 'MAR', 'MIE', 'JUE', 'VIE']
        horas_orden = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7']
        
        matriz = matriz.reindex(columns=dias_orden, index=horas_orden)
        matriz = matriz.fillna("-") # Los guiones son los "huecos" o descansos

        st.table(matriz)
        
        # Métrica de "Huecos" (Opcional pero útil para tu informe)
        horas_ocupadas = data_filtrada.shape[0]
        st.info(f"Carga Horaria Total: {horas_ocupadas} horas semanales.")
        
    else:
        st.warning("Este profesor no tiene horas asignadas.")

except Exception as e:
    st.error(f"Error: {e}")