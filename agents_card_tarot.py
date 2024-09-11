from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import replicate

# Environment setup
load_dotenv(override=True)
os.environ.get("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.7)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def create_tarot_image(prompt):
    input = {
        "prompt": prompt,
        "aspect_ratio": "2:3",
        "output_quality": 80,
        "output_format": "png",
    }

    output = replicate.run(
        "apolinario/flux-tarot-v1:6c4ebdf049df552f8c02b3a7bbb3afec3d37b20924282bab8744f1168b6de470",
        input=input,
    )
    return output
    # => ["https://replicate.delivery/yhqm/ntpCLc1reMXKTKAipFQCgpD...


def agent_card_reader(nombre, estado_animo, tarot_card_description):
    # Prompt
    prompt = PromptTemplate(
        template="""
        Usa la información proporcionada para escribir una breve introducción en formato markdown sobre la carta que el Tarot Espacial ha elegido para {nombre}. El mensaje debe ser optimista y positivo, tomando en cuenta su estado de ánimo actual: {estado_animo}. Incluye una descripción corta de la carta que ha salido: {tarot_card_description}. 

        La introducción debe ser breve, no más de un párrafo, inspiradora y transmitir un mensaje de confianza en el futuro.
        
        Usa emojis misticos.

        """,
        input_variables=["nombre", "estado_animo", "tarot_card_description"],
    )

    chain = prompt | llm
    try:
        card_fate = chain.invoke(
            {
                "nombre": nombre,
                "estado_animo": estado_animo,
                "tarot_card_description": tarot_card_description,
            }
        )

        return card_fate
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def agent_card(
    nombre, fecha_nacimiento, color_favorito, animal_representa, estado_animo
):
    # Prompt
    prompt = PromptTemplate(
        template="""
        Create a short tarot card description that will be used to create an image with an AI model.
        
        The image should depict a scene influenced by the user's current state of mind (bear in mind that it could be in Spanish, translate it to English): {estado_animo}. If the state of mind is negative, create an uplifting and positive image that contrasts with the user's mood. If the state of mind is positive, the image should reflect that energy. Incorporate the mystical power of the color (translate it to English) {color_favorito} and the strength of the spirit animal, the (translate to English) {animal_representa}.
        
        Include a single word in Spanish, in quotation marks, that reflects the user's personality. This Spanish word should preferably be in the feminine form.
        
        Ensure in your description that this word is explicitly placed at the bottom of the tarot card.

        Do not start with "Create an image...". Go directly with the description of the image.
        
        IMPORTANT: Make it very short, like two lines top, and be very descriptive. Do not use ideas because the AI model can't understand those ideas.
        
        Your description MUST finish with "in the style of TOK a trtcrd tarot style."
        """,
        input_variables=["color_favorito", "animal_representa", "estado_animo"],
    )

    chain = prompt | llm
    try:
        tarot = chain.invoke(
            {
                "color_favorito": color_favorito,
                "animal_representa": animal_representa,
                "estado_animo": estado_animo,
            }
        )
        tarot_card = create_tarot_image(tarot.content)
        tarot_card_fate = agent_card_reader(nombre, estado_animo, tarot.content)
        return tarot_card_fate.content, tarot_card
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
