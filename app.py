import os
import cohere
import streamlit as st
from dotenv import load_dotenv

# 1. Configuración de la página de Streamlit
st.set_page_config(page_title="Asistente de Certificados", page_icon="🎓", layout="centered")

# 2. Variables de entorno y validación de API Key
load_dotenv()
api_key = os.getenv("COHERE_API_KEY")

if not api_key:
    st.error("Error: No se encontró la clave de API 'COHERE_API_KEY' en el archivo .env")
    st.stop()

# Inicializar el cliente de Cohere V2
co = cohere.ClientV2(api_key)

# 3. Prompt del Sistema (Instrucciones del Agente)
SYSTEM_PROMPT = """Rol: Actúa como un asistente administrativo experto y amable encargado de la emisión de certificados académicos y profesionales.
Objetivo: Tu tarea es recolectar del usuario tres bloques de información esenciales para poder redactar el texto formal de un certificado de aprobación o asistencia.
Instrucciones de interacción:
- Preséntate de forma breve y explica qué vas a hacer.
- Solicita la información de manera ordenada, paso a paso, para no abrumar al usuario (o toda junta si el usuario prefiere enviarla en un solo mensaje).
- Asegúrate de obtener exactamente los siguientes datos:
  * Bloque 1: Identificación del Curso (Para el título): Nombre completo del curso o capacitación.
  * Bloque 2: Detalles Técnicos (Para el cuerpo del texto): Duración total en horas reloj (ej. "40 horas reloj"), Localidad/Ciudad y Provincia/País donde se dictó.
  * Bloque 3: Datos de Emisión (Para las firmas al pie): Nombre y Apellido de la autoridad firmante, Cargo u organización que representa (ej. "Director de Capacitación", "Presidente").
Validación: Si el usuario olvida algún dato (por ejemplo, dice las horas pero no la localidad), vuelve a solicitarlo amablemente antes de avanzar.
Confirmación: Una vez que tengas todos los datos, muestra un resumen estructurado al usuario y dile que ya está listo para procesar el listado de alumnos (el archivo Excel)."""

# 4. Inicialización del historial del chat en la sesión de Streamlit
if "messages" not in st.session_state:
    # Prompt de sistema oculto al inicio del historial para guiar a Cohere
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Llamada inicial automática para que el agente se presente
    try:
        response = co.chat(
            model="command-r-08-2024",
            messages=st.session_state.messages
        )
        # Guarda la respuesta del asistente en el historial para mostrarla
        assistant_reply = response.message.content[0].text
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        st.error(f"Error al conectar con Cohere: {e}")

# 5. Interfaz de Usuario (UI)
st.title("Generador Automatizado de Certificados")
st.subheader("Paso 1: Configuración de la capacitación con el Agente IA")
st.write("Responde a las preguntas del asistente para definir los datos que irán en el certificado.")

# Mostrar los mensajes anteriores del chat (saltando el prompt del sistema que está en el índice 0)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.write(msg["content"])

# Entrada de texto del usuario
if user_input := st.chat_input("Escribe aquí tu respuesta..."):
    # 1. Mostrar el mensaje del usuario 
    with st.chat_message("user"):
        st.write(user_input)
    
    # 2. Agregar el mensaje del usuario al historial del estado
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 3. Llamar a la API de Cohere enviando todo el historial conversacional
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        with st.spinner("Pensando..."):
            try:
                response = co.chat(
                    model="command-r-08-2024",
                    messages=st.session_state.messages
                )
                assistant_reply = response.message.content[0].text
                message_placeholder.write(assistant_reply)
                
                # 4. Agregar la respuesta del asistente al historial
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
            except Exception as e:
                st.error(f"Hubo un problema al procesar tu solicitud: {e}")

# --- Próximo paso (Visual) ---
st.markdown("---")
st.subheader("Paso 2: Carga del listado de Alumnos")
uploaded_file = st.file_uploader("Una vez que el agente confirme los datos, sube tu archivo Excel (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    st.success("¡Archivo Excel recibido con éxito! (Listo para conectar con la lógica de generación de PDFs)")