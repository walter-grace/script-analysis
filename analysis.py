import os
import re
import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import openai

st.title("Film Script Analysis")

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Define rate as $0.000004 per token
rate = 0.000004

if openai_api_key:
    # Set the OpenAI API key
    openai.api_key = openai_api_key

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
    Think of yourself as a movie reviewer who knows a lot about films. You've also got the know-how of a successful movie maker. Now, take a look at this latest popular movie. Think about its story, the acting, the camera work, and how well it was made. Also, think about how it could have been better if you were in charge, like who to cast, how to spend the budget, how to promote it, and where to show it. Pay extra attention to dialogues that sound too musical or are said over and over. Here's the scene to look at:"""

    user_prompt = f"\n{scene_content}\n\n"
    user_prompt += (("Also, please consider: " + prompt) if prompt else "")
    user_prompt += "\n\nAfter considering the scene's narrative structure, character development, dialogue, pacing, and themes, provide a detailed analysis. Highlight areas that work well, those that need refinement, and any observed inconsistencies or plot holes. Also, suggest any necessary alterations or additions to enhance the story's depth, emotional impact, and overall quality."

    response, cost = generate_response(system_prompt, user_prompt, model)
    return response, cost

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
    cost = response['usage']['total_tokens']
    return reply, cost

def write_to_pdf(text, filename="output.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)

# Replace this line with your name and website or any details you want to display
st.subheader("A Streamlit web app by [nico](https://nico.super.site/)")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    text = pdf_to_text("temp.pdf")
    story_first_half, story_second_half = split_story_in_half(text)
    scenes = split_into_scenes(text)

    total_cost = 0
    pdf_content = ""

    # Initialize the progress bar and the percentage completion text at the top of the loop
    progress_bar = st.progress(0)
    progress_text = st.empty()

    for i, scene in enumerate(scenes):
        if scene.strip() == "":
            continue
        story_part = story_first_half if i < len(scenes) // 2 else story_second_half
        scene_with_context = story_part + "\n" + scene

        scene_title = f"Scene {i+1}"
        st.subheader(scene_title)
        st.write(scene)

        analysis, cost = analyze_scene(scene_with_context)

        total_cost += cost
        cost_in_usd = cost * rate
        analysis_section = f"Analysis of {scene_title}:\n{analysis}\nCost of analysis: ${cost_in_usd:.2f}\n"
        pdf_content += analysis_section
        st.write(analysis_section)

        # Update the progress bar and the percentage completion text based on the ratio of current scene to total scenes
        progress = (i + 1) / len(scenes)
        progress_bar.progress(progress)
        progress_text.text(f"Progress: {progress*100:.1f}%")

    total_cost_in_usd = total_cost * rate
    pdf_content += f"\nTotal cost of analyses: ${total_cost_in_usd:.2f}"
    st.write(f"Total cost of analyses: ${total_cost_in_usd:.2f}")

    write_to_pdf(pdf_content, "analysis_output.pdf")
    st.download_button(label="Download PDF", data=open("analysis_output.pdf", "rb"), file_name="analysis_output.pdf", mime="application/pdf")
