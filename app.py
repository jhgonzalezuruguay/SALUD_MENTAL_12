import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import csv
import base64

# ================== CONFIGURACIÓN DE ADMIN ==================
ADMIN_USER_CODE = "16990037"  # Cambia esto por tu código personal de 8 dígitos de administrador
ADMIN_PASSWORD = "16990037"    # Cambia esto por tu clave secreta de administrador

CSV_FILE = "historial_estado_animo.csv"

def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", encoding="utf-8") as file:
            file.write("Usuario,Fecha,Estado de Ánimo\n")

def guardar_estado_animo(usuario, fecha, estado):
    with open(CSV_FILE, "a", encoding="utf-8") as file:
        file.write(f"{usuario},{fecha},{estado}\n")

def cargar_datos_estado_animo():
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE, dtype=str)
        except Exception:
            return pd.DataFrame(columns=["Usuario", "Fecha", "Estado de Ánimo"])
    else:
        return pd.DataFrame(columns=["Usuario", "Fecha", "Estado de Ánimo"])

def get_table_download_link(df, filename="datos.csv"):
    csv_str = df.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar como CSV</a>'
    return href

# Inicializar el archivo CSV
inicializar_csv()

st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")

# Identificación de usuario
st.sidebar.title("🧑 Identificación de Usuario")
usuario = st.sidebar.text_input("Por favor, ingresa tu documento de identidad sin puntos ni guiones y presiona ingresar:").strip().lower()

if not usuario:
    st.warning("Por favor, ingresa tu código dentificador en la barra lateral para continuar (Documento de Identidad).")
    st.stop()

# Chat
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

# Registro de estado de ánimo
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
    st.success(f"¡Estado de ánimo '{estado_animo}' registrado para la fecha {fecha_actual}!")
    st.cache_data.clear()

# Historial de estados de ánimo
st.markdown("---")
st.subheader("📋 Historial de Estados de Ánimo")
datos = cargar_datos_estado_animo()

# Normaliza nombres de usuario en el DataFrame para evitar errores de filtrado
if not datos.empty:
    datos["Usuario"] = datos["Usuario"].astype(str).str.strip().str.lower()
    datos_usuario = datos[datos["Usuario"] == usuario]
else:
    datos_usuario = pd.DataFrame(columns=["Fecha", "Estado de Ánimo"])

if not datos_usuario.empty:
    st.write(datos_usuario[["Fecha", "Estado de Ánimo"]])
    st.info("Solo el administrador puede descargar el historial en CSV.")
else:
    st.info("No hay datos registrados aún para este usuario.")

# Gráfico de frecuencias
if not datos_usuario.empty:
    st.subheader("📊 Tendencia Temporal de Estados de Ánimo")
    resumen = datos_usuario["Estado de Ánimo"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(resumen.index, resumen.values, color="skyblue")
    ax.set_title("Frecuencia de Estados de Ánimo")
    ax.set_xlabel("Estado de Ánimo")
    ax.set_ylabel("Frecuencia")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

# =========== ACCESO ADMINISTRATIVO (SOLO VISIBLE A ADMIN) =========
if usuario == ADMIN_USER_CODE:
    st.markdown("---")
    st.subheader("🔑 Acceso administrativo (descarga de datos)")

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        admin_code = st.text_input("Código de administrador:", type="password")
        if st.button("Ingresar como administrador"):
            if admin_code == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.success("Acceso concedido. Puedes descargar los historiales.")
            else:
                st.error("Código incorrecto.")
    else:
        st.success("🟢 Acceso de administrador activo.")

        # Listado de códigos únicos de usuario
        st.markdown("#### Códigos de usuario registrados")
        codigos_unicos = sorted(datos["Usuario"].unique())
        st.write("Códigos únicos registrados:")
        st.code('\n'.join(codigos_unicos), language="text")

        # Descarga historial individual de cualquier usuario
        st.markdown("#### Descargar historial individual de usuario")
        buscar_codigo = st.text_input("Código identificador de usuario para descargar historial:", max_chars=50, key="descarga_individual")
        if buscar_codigo:
            buscar_codigo = buscar_codigo.strip().lower()
            df_usuario = datos[datos["Usuario"] == buscar_codigo]
            if not df_usuario.empty:
                st.dataframe(df_usuario)
                st.markdown(get_table_download_link(df_usuario, filename=f"estado_animo_{buscar_codigo}.csv"), unsafe_allow_html=True)
            else:
                st.info("No hay datos para ese código de usuario.")

        # Descarga historial grupal de todos los usuarios
        st.markdown("#### Descargar historial grupal/completo")
        if not datos.empty:
            st.dataframe(datos)
            st.markdown(get_table_download_link(datos, filename="estado_animo_completo.csv"), unsafe_allow_html=True)
        else:
            st.info("No hay ingresos registrados aún.")

# Opciones adicionales
st.markdown("---")
st.subheader("📅 Agendar una consulta con un profesional")
st.write("Si deseas hablar con un profesional de salud mental, agenda una cita a continuación.")
booking_url = "https://forms.gle/MQwofoD14ELSp4Ye7"
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
