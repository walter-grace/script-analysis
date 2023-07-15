import os
import re
import time
import streamlit as st
from PyPDF2 import PdfReader
import openai
from dotenv import load_dotenv

# Load your OpenAI API key from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def pdf_to_text(file_path):
    reader = PdfReader(file_path)
    text = " ".join([page.extract_text() for page in reader.pages])
    return text

def split_into_scenes(text):
    text = re.sub(r'\b(INT\.|EXT\.)', r' \1', text)
    scenes = re.split(r' (?=INT\.|EXT\.)', text)
    return scenes

def split_story_in_half(text):
    tokens = text.split(' ')
    half = len(tokens)//2
    return ' '.join(tokens[:half]), ' '.join(tokens[half:])

def analyze_scene(scene_content, prompt=None, model="gpt-3.5-turbo-16k"):
    system_prompt = """ 
    Imagine you are a seasoned movie critic with a deep understanding of the film industry, known for your insightful and detailed reviews. 
    You also have the experience of an Oscar-winning Hollywood producer, with a keen eye for what makes a film successful both critically and commercially. 
    Analyze the latest blockbuster movie, considering its storytelling, acting performances, cinematography, and production quality. 
    Also, provide insights on how it could have been improved from a producer's perspective, considering factors like casting, budget allocation, marketing strategy, and distribution.
    Please pay special attention to dialogues that are too 'sing-songy' or repetitive. Here is the scene to analyze:"""

    user_prompt = f"\n{scene_content}\n\n"
    user_prompt += (("Also, please consider: " + prompt) if prompt else "")
    user_prompt += "\n\nAfter considering the scene's narrative structure, character development, dialogue, pacing, and themes, provide a detailed analysis. Highlight areas that work well, those that need refinement, and any observed inconsistencies or plot holes. Also, suggest any necessary alterations or additions to enhance the story's depth, emotional impact, and overall quality."

    response = generate_response(system_prompt, user_prompt, model)
    return response

def generate_response(system_prompt, user_prompt, model="gpt-3.5-turbo-16k"):
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    params = {
        'model': model,
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.6,
    }

    response = openai.ChatCompletion.create(**params)
    reply = response.choices[0]["message"]["content"]
    return reply

st.title("Film Script Analysis")
st.subheader("Analyzing script scene by scene...")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Convert PDF to text
    text = pdf_to_text("temp.pdf")

    # Split the story in half
    story_first_half, story_second_half = split_story_in_half(text)

    # Split into scenes
    scenes = split_into_scenes(text)

    progress = st.progress(0)  # Initial progress is 0

    # Create directory to save analysis files
    if not os.path.exists('analysis_files'):
        os.makedirs('analysis_files')

    for i, scene in enumerate(scenes):
        if scene.strip() == "":
            continue
        story_part = story_first_half if i < len(scenes) // 2 else story_second_half
        scene_with_context = story_part + "\n" + scene
        analysis = analyze_scene(scene_with_context)
        st.write(f"Analysis of Scene {i+1}:")
        st.write(analysis)

        # Save analysis to a text file
        with open(f'analysis_files/scene{i+1}_analysis.txt', 'w') as file:
            file.write(analysis)

        progress_value = (i+1) / len(scenes)  # Calculate the current progress
        progress.progress(progress_value)  # Update the progress bar

        time.sleep(2)  # optional sleep to prevent rate limiting
