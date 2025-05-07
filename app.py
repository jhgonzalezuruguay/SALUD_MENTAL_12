import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
import os

# Archivo CSV para almacenar los datos del estado de ánimo
CSV_FILE = "historial_estado_animo.csv"

# Inicializar archivo CSV si no existe
def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w") as file:
            file.write("Fecha,Estado de Ánimo\n")

# Guardar estado de ánimo en el archivo CSV
def guardar_estado_animo(fecha, estado):
    with open(CSV_FILE, "a") as file:
        file.write(f"{fecha},{estado}\n")

# Cargar los datos del CSV
def cargar_datos_estado_animo():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Fecha", "Estado de Ánimo"])

# Inicializar el archivo CSV
inicializar_csv()

# Cargar datos desde el archivo CSV enriquecido con verificación
@st.cache_data
def cargar_datos_enriquecidos():
    try:
        return pd.read_csv("datos_enriquecidos.csv", encoding="latin-1")
    except FileNotFoundError:
        st.error("Error: El archivo CSV no se encuentra en el directorio. Asegúrate de que el archivo exista.")
        return pd.DataFrame()  # Retorna un DataFrame vacío si el archivo no se encuentra

data = cargar_datos_enriquecidos()

# Función para normalizar nombres de enfermedades
def normalizar_enfermedad(enfermedad):
    enfermedad = enfermedad.lower()
    if "pánico" in enfermedad:
        return "Trastorno de Pánico"
    elif "bipolar" in enfermedad:
        return "Trastorno Bipolar"
    elif "estado de ánimo" in enfermedad:
        return "Trastorno del Estado de Ánimo"
    elif "obsesivo" in enfermedad or "compulsivo" in enfermedad:
        return "Trastorno Obsesivo-Compulsivo"
    elif "fobia" in enfermedad:
        return "Fobias"
    elif "postparto" in enfermedad:
        return "Depresión Postparto"
    return enfermedad

# Función para obtener diagnóstico basado en los síntomas
def obtener_diagnostico(sintomas):
    resultados = {}
    if not data.empty:
        sintomas_lista = [sintoma.lower().strip() for sintoma in sintomas.split(',')]
        for index, row in data.iterrows():
            if any(sintoma in row['Síntomas'].lower() for sintoma in sintomas_lista):
                enfermedad = normalizar_enfermedad(row['Enfermedad'])
                descripcion = row['Descripción']
                url = row['URL']
                
                if enfermedad not in resultados:
                    resultados[enfermedad] = {'descripcion': descripcion, 'urls': [url]}
                else:
                    if descripcion not in resultados[enfermedad]['descripcion']:
                        resultados[enfermedad]['descripcion'] += f"\n\n{descripcion}"
                    if url not in resultados[enfermedad]['urls']:
                        resultados[enfermedad]['urls'].append(url)
    return resultados

# Título de la aplicación
st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")
st.title("Diagnóstico Preliminar de Salud Mental")
st.markdown(
    "Bienvenido a **VITAL**, una aplicación que utiliza Inteligencia Artificial "
    "para analizar síntomas y proporcionar un diagnóstico estimado de salud mental. "
    "⚠️ **Recuerda**: Este diagnóstico es solo una guía. Para una evaluación completa, "
    "puedes consultar con un profesional de la salud mental registrándote a nuestro servicio."
)

# Robot de chat
st.sidebar.title("🤖 Chat de Asistencia")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hola! Soy tu asistente de salud mental. ¿Cómo te sientes hoy?"}
    ]

for message in st.session_state.messages:
    with st.sidebar:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.sidebar.chat_input("Cuéntame cómo te sientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.sidebar:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = "Gracias por compartir. Si necesitas más ayuda, revisa las secciones de la aplicación."
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sección 1: Diagnóstico basado en síntomas
st.subheader("📋 Ingresa tus síntomas")
st.write("Ingresa tus síntomas separados por comas y recibe información y enlaces a posibles trastornos relacionados.")
st.write("Cuanta mas información ingreses sobre como te sientes, ayuda a mejorar el posible diagnóstico")

sintomas_usuario = st.text_input("Describe tus síntomas (por ejemplo: tristeza, insomnio, fatiga)")

if st.button("Obtener Diagnóstico"):
    if sintomas_usuario:
        diagnostico = obtener_diagnostico(sintomas_usuario)
        if diagnostico:
            st.success("**POSIBLE DIAGNÓSTICO O PATOLOGÍAS ASOCIADAS A TUS SÍNTOMAS:**")
            for enfermedad, info in diagnostico.items():
                st.subheader(enfermedad)
                st.write(info['descripcion'])
                for url in info['urls']:
                    st.markdown(f"[Más información aquí]({url})", unsafe_allow_html=True)
        else:
            st.warning("No se identificaron trastornos específicos basados en los síntomas proporcionados. Por favor, consulta con un profesional.")
    else:
        st.error("Por favor, ingresa al menos un síntoma para obtener el diagnóstico.")

# Sección 2: Seguimiento del Estado de Ánimo
st.markdown("---")
st.subheader("📊 Seguimiento del Estado de Ánimo")
st.write("Registra tu estado de ánimo diario para llevar un seguimiento de cómo te sientes a lo largo del tiempo.")

estado_animo = st.selectbox(
    "¿Cómo te sientes hoy?",
    ["Feliz 😀", "Triste 😢", "Ansioso 😰", "Relajado 😌", "Enojado 😡"]
)

if st.button("Registrar Estado de Ánimo"):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guardar_estado_animo(fecha_actual, estado_animo)
    st.success(f"¡Estado de ánimo '{estado_animo}' registrado para la fecha {fecha_actual}!")

# Sección 3: Historial de Estados de Ánimo
st.markdown("---")
datos = cargar_datos_estado_animo()
st.subheader("📋 Historial de Estados de Ánimo")
if not datos.empty:
    st.write(datos)
else:
    st.write("No hay datos registrados aún.")

# Sección 4: Generación de gráficos
if not datos.empty:
    datos["Fecha"] = pd.to_datetime(datos["Fecha"])
    datos["Fecha_Dia"] = datos["Fecha"].dt.date  # Extraer solo la fecha (sin hora)

    st.subheader("📊 Tendencia Temporal de Estados de Ánimo")
    resumen = datos["Estado de Ánimo"].value_counts()
    fig, ax = plt.subplots()
    ax.bar(resumen.index, resumen.values, color="skyblue")
    ax.set_title("Frecuencia de Estados de Ánimo")
    ax.set_xlabel("Estado de Ánimo")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Configuración del formateador de fechas
    date_form = DateFormatter("%Y-%m-%d")  # Año-Mes-Día

    # Gráfico de tendencia temporal
    fig, ax = plt.subplots()
    datos.groupby("Fecha_Dia").size().plot(ax=ax, kind="line", marker="o", color="green")
    ax.set_title("Tendencia de Estados de Ánimo a lo Largo
