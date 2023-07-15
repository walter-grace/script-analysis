import os
import re
import time
import streamlit as st
from PyPDF2 import PdfReader
import openai
from dotenv import load_dotenv
from fpdf import FPDF

st.title("Film Script Analysis")

openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    # Set the OpenAI API key
    openai.api_key = openai_api_key

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

        scenes_analysis = []  # Initialize empty list to store the analysis of each scene

        for i, scene in enumerate(scenes):
            if scene.strip() == "":
                continue
            story_part = story_first_half if i < len(scenes) // 2 else story_second_half
            scene_with_context = story_part + "\n" + scene
            analysis = analyze_scene(scene_with_context)
            st.write(f"Analysis of Scene {i+1}:")
            st.write(analysis)

            scenes_analysis.append(analysis)  # Add the analysis to the list

            # Save analysis to a text file
            with open(f'analysis_files/scene{i+1}_analysis.txt', 'w') as file:
                file.write(analysis)

            progress_value = (i+1) / len(scenes)  # Calculate the current progress
            progress.progress(progress_value)  # Update the progress bar

            time.sleep(2)  # optional sleep to prevent rate limiting

        # When the loop is done, generate the PDF report
        export_to_pdf(scenes_analysis)

        # Then create a download button for the PDF
        with open("scene_analysis.pdf", "rb") as f:
            pdf_file = f.read()

        st.download_button(
            label="Download Scene Analysis Report",
            data=pdf_file,
            file_name='scene_analysis.pdf',
            mime='application/pdf',
        )
