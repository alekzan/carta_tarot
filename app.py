import streamlit as st
import streamlit.components.v1 as components
import base64
import sqlite3
import os
import uuid
import datetime
import requests  # For downloading the image

from agents_card_tarot import agent_card  # Import the agent to generate the tarot card

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Set the date range for ages 16 to 90 years
min_date = datetime.date.today() - datetime.timedelta(days=90 * 365)  # 90 years ago
max_date = datetime.date.today() - datetime.timedelta(days=16 * 365)  # 16 years ago


# Function to convert image to base64
def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Function to initialize the database schema
def initialize_db():
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    # Create table with the correct schema
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            nombre text,
            fecha_nacimiento text,
            color_favorito text,
            animal_representa text,
            estado_animo text,
            correo text
        )"""
    )
    conn.commit()
    conn.close()


# Function to save user data
def save_user_data(
    nombre,
    fecha_nacimiento,
    color_favorito,
    animal_representa,
    estado_animo,
    correo,
):
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (nombre, fecha_nacimiento, color_favorito, animal_representa, estado_animo, correo) VALUES (?, ?, ?, ?, ?, ?)",
        (
            nombre,
            fecha_nacimiento,
            color_favorito,
            animal_representa,
            estado_animo,
            correo,
        ),
    )
    conn.commit()
    conn.close()


def download_image(image_url, file_name="tarot_card.png"):
    # Download the image from the provided URL
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
        return file_name
    else:
        return None


def main():
    st.set_page_config(
        page_title="Tu Carta de Tarot Personalizada",
        page_icon="🔮",
    )

    if "config" not in st.session_state:
        thread_id_number = str(uuid.uuid4())
        st.session_state.config = {"configurable": {"thread_id": thread_id_number}}

    # Initialize the database schema
    initialize_db()

    # Convert the image to base64 and display it at the top of the sidebar
    img_path = "images/carta.jpg"  # Replace with the correct path to your image
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f"""
        <style>
        .cover-glow {{
            width: 100%;  /* Adjust the width as needed */
            height: auto; /* Maintain the aspect ratio */
            padding: 3px;
            box-shadow: 1px 2px 23px 0px rgba(188,150,255,0.75);
            border-radius: 30px;
        }}
        </style>
        <img src="data:image/png;base64,{img_base64}" class="cover-glow">
        """,
        unsafe_allow_html=True,
    )

    # Sidebar content
    st.sidebar.title("Bienvenid@ al Tarot MAI MAI")
    st.sidebar.markdown(
        """
        Llena tus datos y genera tu propia tarjeta de Tarot personalizada.
        Si quieres conocer la joyería que mejor va con tu interior místico, visita nuestra tienda en línea: 
        [MAI MAI](https://www.maimai.com.mx/)
        """,
        unsafe_allow_html=True,
    )

    # Main content
    st.title("🔮 Tu Carta de Tarot Personalizada")
    st.subheader("Llena tus datos para generar tu propia tarjeta de tarot.")

    # Form to collect user information
    with st.form("tarot_form"):
        nombre = st.text_input("Tu nombre")
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento", min_value=min_date, max_value=max_date
        )
        color_favorito = st.text_input("Tu color favorito")
        animal_representa = st.text_input("El animal que te representa")
        estado_animo = st.text_area("¿Cómo te sientes hoy?")
        correo = st.text_input("Tu correo electrónico")  # Solicitamos el correo

        # Button to submit the form
        generar_tarjeta = st.form_submit_button("Generar mi carta de tarot")

    # Process form submission
    if generar_tarjeta:
        if not (
            nombre and color_favorito and animal_representa and estado_animo and correo
        ):
            st.warning("Por favor, completa todos los campos obligatorios.")
        else:
            # Save user data
            save_user_data(
                nombre,
                str(fecha_nacimiento),
                color_favorito,
                animal_representa,
                estado_animo,
                correo,
            )

            with st.spinner("Generando tu carta de tarot..."):
                # Call the agent_card function from agents_card_tarot.py
                tarot_card_description, tarot_card_url = agent_card(
                    nombre,
                    str(fecha_nacimiento),
                    color_favorito,
                    animal_representa,
                    estado_animo,
                )

                # Ensure the URL is a string, not a list
                tarot_card_url = (
                    tarot_card_url[0]
                    if isinstance(tarot_card_url, list)
                    else tarot_card_url
                )

                # Display the card description
                st.markdown(f"### Descripción de la carta:\n\n{tarot_card_description}")

                # Display the tarot card image, resized for better visibility
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: center;'>
                        <img src="{tarot_card_url}" width="400"/>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Download the image and provide a download button
                downloaded_file_path = download_image(tarot_card_url)

                if downloaded_file_path:
                    with open(downloaded_file_path, "rb") as file:
                        btn = st.download_button(
                            label="Descargar imagen",
                            data=file,
                            file_name="tu_carta_de_tarot.png",
                            mime="image/png",
                        )

    st.markdown(
        "<div style='text-align: center; color: #a491ff;'>Creado por MAI MAI. Todos los derechos reservados</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
