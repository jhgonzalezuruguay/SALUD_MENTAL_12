import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import base64

# ========== CONFIGURACIÓN DE USUARIOS Y SESIÓN ==========
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = [
        {"username": "admin", "password": hashlib.sha256("admin123".encode()).hexdigest(), "rol": "admin"}
    ]
if "user" not in st.session_state:
    st.session_state["user"] = None
if "estado_animo_data" not in st.session_state:
    st.session_state["estado_animo_data"] = []
if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False
if "do_rerun" not in st.session_state:
    st.session_state["do_rerun"] = False

# ========== CONTROL DE RERUN ==========
if st.session_state["do_rerun"]:
    st.session_state["do_rerun"] = False
    st.rerun()

# ========== FUNCIONES AUXILIARES ==========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    return next((u for u in st.session_state["usuarios"] if u["username"] == username), None)

def get_table_download_link(df, filename="datos.csv"):
    csv_str = df.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar como CSV</a>'
    return href

# ========== AUTENTICACIÓN ==========
def mostrar_login():
    st.title("🔒 Ingreso a Salud Mental 2.0")
    tabs = st.tabs(["Iniciar sesión", "Registrarse"])
    with tabs[0]:
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            user = get_user(username)
            if user and user["password"] == hash_password(password):
                st.session_state["user"] = user
                st.success("¡Bienvenido/a!")
                st.session_state["do_rerun"] = True
            else:
                st.error("Usuario o contraseña incorrectos.")
    with tabs[1]:
        username = st.text_input("Nuevo usuario", key="reg_user")
        password = st.text_input("Nueva contraseña", type="password", key="reg_pass")
        if st.button("Registrarse"):
            if not username or not password:
                st.warning("Completa todos los campos.")
            elif get_user(username):
                st.warning("El nombre de usuario ya existe.")
            else:
                st.session_state["usuarios"].append({
                    "username": username,
                    "password": hash_password(password),
                    "rol": "usuario"
                })
                st.success("Usuario registrado. Ahora puedes iniciar sesión.")
                st.session_state["do_rerun"] = True

# ========== BLOQUE DE AUTENTICACIÓN ==========
if not st.session_state["user"]:
    mostrar_login()
    st.stop()

user = st.session_state["user"]
es_admin = user["rol"] == "admin"

st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")

# ========== CHAT DE ASISTENCIA ==========
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

# ========== REGISTRO DE ESTADO DE ÁNIMO ==========
st.markdown("---")
st.subheader("📊 Seguimiento del Estado de Ánimo")
st.write("Registra tu estado de ánimo cada vez que sientas un cambio del mismo o cuando consideres necesario registrarlo, para así llevar un seguimiento de cómo te sientes a lo largo del tiempo.")

estados_opciones = [
    "Feliz 😀", "Triste 😢", "Ansioso 😰", "Relajado 😌", "Enojado 😡",
    "Fiesta 🥳", "Enamorado 😍", "Cool 😎", "Asombrado 🤩", "Arcoíris 🌈",
    "Neutral 😐", "Pensativo 🤔", "Tristeza leve 😔", "Miedo 😱",
    "Agotado 😩", "Meditación 🧘", "Idea 💡", "Energía ⚡", "Confuso 🌪️",
    "Corazón roto 💔"
]

if st.session_state.reset_form:
    estado_default = estados_opciones[0]
    comentario_default = ""
    st.session_state.reset_form = False
else:
    estado_default = estados_opciones[0]
    comentario_default = ""

estado_animo = st.selectbox(
    "¿Cómo te sientes hoy?",
    estados_opciones,
    index=estados_opciones.index(estado_default),
    key="estado"
)
comentario = st.text_area("¿Quieres agregar un comentario? (Opcional)", max_chars=500, key="comentario", value=comentario_default)

if st.button("Registrar Estado de Ánimo"):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Usuario": user["username"],
        "Fecha": fecha_actual,
        "Estado de Ánimo": estado_animo,
        "Comentario": (comentario or "").replace('\n', ' ').replace(',', ';')
    }
    st.session_state["estado_animo_data"].append(entry)
    st.success(f"¡Estado de ánimo '{estado_animo}' registrado para la fecha {fecha_actual}!")
    st.session_state.reset_form = True
    st.rerun()

# ========== HISTORIAL DE ESTADOS DE ÁNIMO ==========
st.markdown("---")
st.subheader("📋 Historial de Estados de Ánimo")

df = pd.DataFrame(st.session_state["estado_animo_data"])
if not df.empty:
    if es_admin:
        datos_vista = df
    else:
        datos_vista = df[df["Usuario"] == user["username"]]
else:
    datos_vista = pd.DataFrame(columns=["Fecha", "Estado de Ánimo", "Comentario"])

if not datos_vista.empty:
    st.write(datos_vista[["Fecha", "Estado de Ánimo", "Comentario"]])
    if not es_admin:
        st.info("Solo el administrador puede descargar el historial en CSV.")
else:
    st.info("No hay datos registrados aún para este usuario.")

# ========== GRÁFICO DE FRECUENCIAS ==========
if not datos_vista.empty:
    st.subheader("📊 Frecuencia de Estados de Ánimo")
    resumen = datos_vista["Estado de Ánimo"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(resumen.index, resumen.values, color="skyblue")
    ax.set_title("Frecuencia de Estados de Ánimo")
    ax.set_xlabel("Estado de Ánimo")
    ax.set_ylabel("Frecuencia")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

# ========== ACCESO ADMINISTRATIVO (SOLO ADMIN PUEDE DESCARGAR) ==========
if es_admin:
    st.markdown("---")
    st.subheader("🔑 Acceso administrativo (descarga de datos)")
    if not df.empty:
        # Listado de usuarios únicos
        st.markdown("#### Usuarios registrados")
        usuarios_unicos = sorted(df["Usuario"].unique())
        st.write("Usuarios registrados:")
        st.code('\n'.join(usuarios_unicos), language="text")

        # Descarga historial individual de cualquier usuario
        st.markdown("#### Descargar historial individual de usuario")
        buscar_usuario = st.text_input("Nombre de usuario para descargar historial:", key="descarga_individual")
        if buscar_usuario:
            buscar_usuario = buscar_usuario.strip()
            df_usuario = df[df["Usuario"] == buscar_usuario]
            if not df_usuario.empty:
                st.dataframe(df_usuario)
                st.markdown(get_table_download_link(df_usuario, filename=f"estado_animo_{buscar_usuario}.csv"), unsafe_allow_html=True)
            else:
                st.info("No hay datos para ese usuario.")

        # Descarga historial grupal de todos los usuarios
        st.markdown("#### Descargar historial grupal/completo")
        st.dataframe(df)
        st.markdown(get_table_download_link(df, filename="estado_animo_completo.csv"), unsafe_allow_html=True)
    else:
        st.info("No hay ingresos registrados aún.")

# ========== CIERRE DE SESIÓN ==========
if st.button("Cerrar sesión"):
    st.session_state["user"] = None
    st.session_state["do_rerun"] = True

# ========== OPCIONES ADICIONALES Y FOOTER ==========
st.markdown("---")
st.subheader("📅 Agendar una consulta con un profesional")
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
