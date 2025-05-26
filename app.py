import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Archivo CSV para almacenar los datos del estado de ánimo
CSV_FILE = "historial_estado_animo.csv"

# Inicializar archivo CSV si no existe o si tiene cabecera vieja
def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w") as file:
            file.write("Usuario,Fecha,Estado de Ánimo\n")
    else:
        # Si el archivo existe pero no tiene la columna Usuario, migrar datos antiguos
        with open(CSV_FILE, "r") as file:
            header = file.readline().strip()
        if header == "Fecha,Estado de Ánimo":
            df_old = pd.read_csv(CSV_FILE)
            df_old.insert(0, "Usuario", "")
            df_old.to_csv(CSV_FILE, index=False)
            # Reescribir la cabecera
            with open(CSV_FILE, "r+") as file:
                content = file.read()
                file.seek(0, 0)
                file.write("Usuario,Fecha,Estado de Ánimo\n" + content.partition('\n')[2])

# Guardar estado de ánimo en el archivo CSV
def guardar_estado_animo(usuario, fecha, estado):
    with open(CSV_FILE, "a") as file:
        file.write(f"{usuario},{fecha},{estado}\n")

# Cargar los datos del CSV
def cargar_datos_estado_animo():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Usuario", "Fecha", "Estado de Ánimo"])

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

# Título de la aplicación
st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")

# --- Sección de usuario ---
st.sidebar.title("🧑 Identificación de Usuario")
usuario = st.sidebar.text_input("Por favor, ingresa tu nombre o identificador:")

if not usuario:
    st.warning("Por favor, ingresa tu nombre o identificador en la barra lateral para continuar.")
    st.stop()

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

# Sección 2: Seguimiento del Estado de Ánimo
st.markdown("---")
st.subheader("📊 Seguimiento del Estado de Ánimo")
st.write("Registra tu estado de ánimo cada vez que sientas un cambio del mismo o cuando consideres necesario registrarlo, para así llevar un seguimiento de cómo te sientes a lo largo del tiempo.")

estado_animo = st.selectbox(
    "¿Cómo te sientes hoy?",
    [
        "Feliz 😀", "Triste 😢", "Ansioso 😰", "Relajado 😌", "Enojado 😡",
        "Fiesta 🥳", "Enamorado 😍", "Cool 😎", "Asombrado 🤩", "Arcoíris 🌈",
        "Neutral 😐", "Pensativo 🤔", "Tristeza leve 😔", "Miedo 😱",
        "Agotado 😩", "Meditación 🧘", "Idea 💡", "Energía ⚡", "Confuso 🌪️",
        "Corazón roto 💔"
    ]
)

if st.button("Registrar Estado de Ánimo"):
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    guardar_estado_animo(usuario, fecha_actual, estado_animo)
    st.success(f"¡Estado de ánimo '{estado_animo}' registrado para la fecha {fecha_actual} para el usuario {usuario}!")

# Sección 3: Historial de Estados de Ánimo
st.markdown("---")
datos = cargar_datos_estado_animo()

# Filtrar por usuario
datos_usuario = datos[datos["Usuario"] == usuario] if not datos.empty and "Usuario" in datos.columns else pd.DataFrame(columns=["Fecha", "Estado de Ánimo"])

st.subheader("📋 Historial de Estados de Ánimo")
if not datos_usuario.empty:
    st.write(datos_usuario[["Fecha", "Estado de Ánimo"]])
else:
    st.write("No hay datos registrados aún para este usuario.")

# Sección 4: Generación de gráficos
if not datos_usuario.empty:
    datos_usuario["Fecha"] = pd.to_datetime(datos_usuario["Fecha"]).dt.date  # Solo fecha, sin hora.
    st.subheader("📊 Tendencia Temporal de Estados de Ánimo")
    resumen = datos_usuario["Estado de Ánimo"].value_counts()
    fig, ax = plt.subplots()
    ax.bar(resumen.index, resumen.values, color="skyblue")
    ax.set_title("Frecuencia de Estados de Ánimo")
    ax.set_xlabel("Estado de Ánimo")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

# Sección 5: Opciones adicionales (Agendar cita, Registro, WhatsApp)
st.markdown("---")
st.subheader("📅 Agendar una consulta con un profesional")
st.write("Si deseas hablar con un profesional de salud mental, agenda una cita a continuación.")
booking_url = "https://forms.gle/MQwofoD14ELSp4Ye7"  # Enlace de tu formulario de citas
st.markdown(f'<a href="{booking_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">AGENDAR CITA</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("📋 Registro de Usuario")
registro_url = "https://forms.gle/ZsM2xrWyUUU9ak6z7"
st.markdown(f'<a href="{registro_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">REGISTRARSE</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("💬 Enviar Mensaje por WhatsApp")
st.write("Si deseas enviar un mensaje por WhatsApp, haz clic en el siguiente botón:")
whatsapp_url = "https://wa.me/59897304859?text=Hola,%20necesito%20ayuda%20con%20mi%20salud%20mental."
st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">Enviar Mensaje</button></a>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("VITAL LE AGRADECE POR CONFIAR Y USAR NUESTRO SERVICIO ❤️")
st.subheader("⚠️  Por consultas, y/o para participar y brindar tu servicio como profesional de la salud en nuestra app, comunicarse con:")
st.write("Mag. José González Gómez")
st.write("Correo: josehumbertogonzalezgomez@gmail.com")
st.write("Ps. Bryan Mora Durán")
st.write("Correo: bryanmoraduran@gmail.com")
st.write("**Nota:** Esta herramienta proporciona diagnósticos preliminares basados en los síntomas ingresados. No reemplaza una consulta profesional.")
