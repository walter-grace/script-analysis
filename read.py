import os
import re
from PyPDF2 import PdfReader

def pdf_to_text(file_path):
    reader = PdfReader(file_path)
    text = " ".join([page.extract_text() for page in reader.pages])
    return text

def split_into_scenes(text):
    # Add a space before "INT." and "EXT." so we can split on them
    text = re.sub(r'\b(INT\.|EXT\.)', r' \1', text)
    # Split the text into scenes
    scenes = re.split(r' (?=INT\.|EXT\.)', text)
    return scenes

def save_scenes(scenes, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, scene in enumerate(scenes):
        # Skip any scenes that are just whitespace
        if scene.strip() == "":
            continue
        filename = os.path.join(output_dir, f'scene_{i+1}.txt')
        try:
            with open(filename, 'w') as file:
                file.write(scene)
            print(f"Saved scene {i+1} to {filename}")
        except Exception as e:
            print(f"Error saving scene {i+1} to {filename}: {e}")

# Convert PDF to text
text = pdf_to_text("temp.pdf")

# Split into scenes
scenes = split_into_scenes(text)

# Save scenes
save_scenes(scenes, "read")
