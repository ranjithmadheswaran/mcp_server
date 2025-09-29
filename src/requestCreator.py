
import streamlit as st
import yaml
import google.generativeai as genai
from google.api_core import exceptions
import logging

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit App ---
st.title("Request body/parameters Generator")

st.write(
    "This tool generates sample API request bodies from an OpenAPI (YAML) specification."
)

api_key = st.text_input("Enter your Google AI API Key to begin", type="password")

if not api_key:
    st.warning("Please enter your Google AI API Key to use the generator.")
    logging.warning("API key not entered. Stopping execution.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model_name = "gemini-2.5-flash"  # A reliable model for the free tier
    model = genai.GenerativeModel(model_name)
    st.info(f"Using model: `{model_name}`")
    logging.info(f"Successfully configured Google AI with model: {model_name}")
        
except Exception as e:
    st.error(f"An error occurred while configuring the Google AI model: {e}")
    logging.error(f"Failed to configure Google AI model: {e}", exc_info=True)
    st.stop()

uploaded_file = st.file_uploader("Upload your OpenAPI specification file", type=["yaml", "yml"])

if uploaded_file is not None:
    # To read file as string:
    try:
        string_data = uploaded_file.getvalue().decode("utf-8")
        spec = yaml.safe_load(string_data)
        st.success("OpenAPI specification loaded and parsed successfully!")
        logging.info(f"Successfully parsed uploaded file: {uploaded_file.name}")

        with st.expander("View YAML Content"):
            st.text_area("YAML Content", string_data, height=300)

        user_prompt = st.text_input(
            "Describe the request you want to generate (e.g., 'add a new pet to the store')",
            key="user_prompt",
        )

        if st.button("Generate Request"):
            if not user_prompt:
                st.warning("Please describe the request you want to generate.")
                logging.warning("Generate button clicked but user prompt was empty.")
            else:
                with st.spinner("Generating..."):
                    logging.info(f"Generating request for prompt: '{user_prompt}'")
                    try:
                        full_prompt = f"""You are an expert API assistant. Based on the following OpenAPI 3.0 specification, generate a valid JSON request body for the operation that matches the user's request.

OpenAPI Specification:
```yaml
{string_data}
```

User Request: Generate a request for the operation: "{user_prompt}"

Generate only the JSON request body with realistic example values. If the operation does not have a request body (e.g., for a GET request), list its parameters (path, query) and example values in JSON format.
"""
                        response = model.generate_content(full_prompt)
                        st.markdown("### Generated Request")
                        st.code(response.text, language="json")
                    except exceptions.ResourceExhausted as e:
                        st.error("API rate limit exceeded. Please wait a moment and try again.")
                        st.info("This is common on the free tier. See the link in the error details for more information on quotas.")
                        st.exception(e)
                    except Exception as e:
                        st.error(f"An unexpected error occurred while generating the request: {e}")

    except yaml.YAMLError as e:
        st.error(f"Error parsing YAML file: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")