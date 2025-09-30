
import streamlit as st
import yaml
import google.generativeai as genai
from google.api_core import exceptions
import logging
import base64
import urllib.parse

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("Request body/parameters Generator")

st.write(
    "This tool generates sample API request bodies from an OpenAPI (YAML) specification."
)

def get_gemini_response(model, prompt_text):
    """Generates content using the Gemini model with error handling."""
    try:
        response = model.generate_content(prompt_text)
        return response.text, None
    except exceptions.ResourceExhausted as e:
        logging.error("API rate limit exceeded.", exc_info=True)
        error_message = (
            "API rate limit exceeded. Please wait a moment and try again. "
            "This is common on the free tier. See the link in the error details for more information on quotas."
        )
        return None, (error_message, e)
    except Exception as e:
        logging.error("An unexpected error occurred during generation.", exc_info=True)
        error_message = f"An unexpected error occurred while generating the response: {e}"
        return None, (error_message, None)


api_key = st.text_input("Enter your Google AI API Key to begin", type="password")

if not api_key:
    st.warning("Please enter your Google AI API Key to use the generator.")
    logging.warning("API key not entered. Stopping execution.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model_name = "gemini-2.5-flash"  # A powerful and efficient model
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
        
        # Create tabs for different actions        
        generate_tab, analyze_tab, editor_tab, view_spec_tab = st.tabs(["Generate Request", "Analyze Specification", "Swagger Editor", "View Specification"])

        with generate_tab:
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
                        full_prompt_parts = [
                            "You are an expert API assistant. Based on the following OpenAPI 3.0 specification, generate a valid JSON request body for the operation that matches the user's request.",
                            "",
                            "OpenAPI Specification:",
                            "```yaml",
                            string_data,
                            "```",
                            f"User Request: Generate a request for the operation: \"{user_prompt}\"",
                            "",
                            "Generate only the JSON request body with realistic example values. If the operation does not have a request body (e.g., for a GET request), list its parameters (path, query) and example values in JSON format."
                        ]
                        full_prompt = "\n".join(full_prompt_parts)

                        response_text, error = get_gemini_response(model, full_prompt)
                        if error:
                            st.error(error[0])
                            if error[1]:
                                st.exception(error[1])
                        else:
                            st.markdown("### Generated Request")
                            st.code(response_text, language="json")
        
        with analyze_tab:
            st.subheader("Analyze OpenAPI Specification")
            analysis_prompt = st.text_input(
                "What would you like to know about this specification? (e.g., 'What endpoints are available for pets?')",
                key="analysis_prompt",
            )

            if st.button("Analyze"):
                if not analysis_prompt:
                    st.warning("Please enter a question about the specification.")
                    logging.warning("Analyze button clicked but analysis prompt was empty.")
                else:
                    with st.spinner("Analyzing..."):
                        logging.info(f"Analyzing specification for prompt: '{analysis_prompt}'")
                        analysis_full_prompt = "\n".join([
                            "You are an expert API assistant. Your task is to analyze the provided OpenAPI 3.0 specification and answer the user's question about it in a clear and concise way.",
                            "",
                            "OpenAPI Specification:",
                            "```yaml",
                            string_data,
                            "```",
                            f"User's Question: \"{analysis_prompt}\""
                        ])
                        
                        response_text, error = get_gemini_response(model, analysis_full_prompt)
                        if error:
                            st.error(error[0])
                        else:
                            st.markdown("### Analysis Result")
                            st.markdown(response_text)
        
        with editor_tab:
            st.subheader("Interactive Swagger Editor")
            # URL encoding is not safe for large specs (>~4KB), which can cause a 414 error.
            # We use a hybrid approach: direct embedding for small files, Gist for large ones.
            if len(string_data.encode('utf-8')) < 4096:
                # For small specs, encode and embed directly in the URL for a seamless experience.
                # We must URL-encode the spec, not Base64-encode it.
                encoded_spec = urllib.parse.quote(string_data)
                editor_url = f"https://editor-next.swagger.io/?spec={encoded_spec}"                
                st.components.v1.iframe(editor_url, height=1000, scrolling=True)
            else:
                # For large specs, instruct the user to use a Gist to prevent errors.
                st.warning("Your OpenAPI specification is too large to be embedded directly.")
                st.markdown("""
                    To view it in the Swagger Editor, please follow these steps as a workaround:
                    1. **Create a public Gist** on GitHub Gist.
                    2. Paste the content of your YAML file into the Gist.
                    3. Create the public Gist and click on the **"Raw"** button.
                    4. Copy the URL from the "Raw" view.
                    5. Paste the Raw URL below.
                """)
                gist_url = st.text_input("Enter the Raw URL of your public Gist")
                if gist_url:
                    # Use the 'url' parameter to load the spec from the Gist.
                    editor_url = f"https://editor-next.swagger.io/?url={urllib.parse.quote(gist_url)}"
                    st.components.v1.iframe(editor_url, height=1000, scrolling=True)

        with view_spec_tab:
            st.text_area("YAML Content", string_data, height=400)

    except yaml.YAMLError as e:
        st.error(f"Error parsing YAML file: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")