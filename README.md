Sure, here is the formatted content for your README.md file:

---

# Script Critic

Script Critic is a Python application that performs a scene-by-scene analysis of a screenplay using OpenAI.

## Setup
Before running the scripts, you need to install the required Python packages. You can do this by running the following command in your terminal:

```
pip install -r requirements.txt
```

Then, set your OpenAI API key in the `.env` file or as an environment variable.

## How to Run

1. Place your screenplay PDF file in the root directory and rename it to `temp.pdf`.

2. Run `read.py` to split your screenplay into separate scenes and save each scene as a text file in the `read` directory. You can do this by running the following command in your terminal:

```
python read.py
```

This allows you to view what scenes are being created for reference to the critique.

3. Start the Streamlit app by running the following command in your terminal:

```
streamlit run analysis.py
```

4. In the Streamlit interface, upload your PDF file and enter your OpenAI API key. The app will analyze each scene and display the analysis results.

5. The results are also saved as a PDF file named `analysis_output.pdf`. Where you can download the file.

## Note

The analysis cost is calculated based on the OpenAI API's rate of $0.000004 per token.

---


Please let me know if you need any further help or modifications.