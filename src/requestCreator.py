
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
    except exceptions.NotFound as e:
        logging.error(f"Model not found: {e}", exc_info=True)        
        error_message = (
            f"The selected model `{model.model_name}` was not found for your API key or region. "
            "This can happen if the model is not available in your region. "
            "Please try selecting a different model from the dropdown."
        )
        return None, (error_message, None)

    except Exception as e:
        logging.error("An unexpected error occurred during generation.", exc_info=True)
        error_message = f"An unexpected error occurred while generating the response: {e}"
        return None, (error_message, None)


api_key = st.text_input("Enter your Google AI API Key to begin", type="password")

# Initialize session state
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "models_list" not in st.session_state:
    st.session_state.models_list = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "current_file_name" not in st.session_state:
    st.session_state.current_file_name = None

# Fetch models if a new API key is entered
if api_key and api_key != st.session_state.api_key:
    st.session_state.api_key = api_key
    st.session_state.models_list = []
    st.session_state.selected_model = None
    try:
        genai.configure(api_key=api_key)
        with st.spinner("Fetching available models..."):
            st.session_state.models_list = [
                m.name for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]
            # Set a preferred default model if available
            preferred_models = ["models/gemini-2.5-flash", "models/gemini-pro"]
            for model in preferred_models:
                if model in st.session_state.models_list:
                    st.session_state.selected_model = model
                    break
            if not st.session_state.selected_model and st.session_state.models_list:
                st.session_state.selected_model = st.session_state.models_list[0]

    except Exception as e:
        st.error(f"Failed to configure Google AI or fetch models. Please check your API key. Error: {e}")
        st.session_state.api_key = "" # Reset to allow re-entry

if not st.session_state.api_key:
    st.warning("Please enter your Google AI API Key to use the generator.")
    st.stop()

if not st.session_state.models_list:
    st.warning("No compatible models found for this API key. Please check your Google AI project and permissions.")
    st.stop()

# Determine the default index for the selectbox
try:
    default_index = st.session_state.models_list.index(st.session_state.selected_model)
except (ValueError, TypeError):
    default_index = 0

# Let the user select a model
st.session_state.selected_model = st.selectbox(
    "Select a Model", 
    st.session_state.models_list,
    index=default_index
)

model = genai.GenerativeModel(st.session_state.selected_model)

uploaded_file = st.file_uploader("Upload your OpenAPI specification file", type=["yaml", "yml"])

if uploaded_file is not None:
    # To read file as string:
    try:
        string_data = uploaded_file.getvalue().decode("utf-8")
        spec = yaml.safe_load(string_data)
        st.success("OpenAPI specification loaded and parsed successfully!")
        # Reset history only if a new file is uploaded
        if uploaded_file.name != st.session_state.current_file_name:
            st.session_state.current_file_name = uploaded_file.name
            st.session_state.analysis_history = []
            st.session_state.generate_history = []
            st.session_state.erp_history = []



        logging.info(f"Successfully parsed uploaded file: {uploaded_file.name}")
        
        # Create tabs for different actions        
        generate_tab, analyze_tab, erp_tab, editor_tab, view_spec_tab = st.tabs(["Generate Request", "Analyze Specification", "ERP Integration", "Swagger Editor", "View Specification"])

        with generate_tab:
            # Display previous generations
            for item in st.session_state.generate_history:
                st.markdown(f"**Your Request:** `{item['prompt']}`")
                st.code(item['response'], language="json")
                st.divider()
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
                            st.session_state.generate_history.append({"prompt": user_prompt, "response": response_text})
                            # The script will rerun automatically after the button press, no need for forceful rerun.
        
        with analyze_tab:
            st.subheader("Analyze OpenAPI Specification")
            st.markdown("Ask questions about your API specification in a conversational manner.")

            # Display existing chat messages
            for message in st.session_state.analysis_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input for new messages
            if analysis_prompt := st.chat_input("What would you like to know?"):
                # Add user message to history and display it
                st.session_state.analysis_history.append({"role": "user", "content": analysis_prompt})
                with st.chat_message("user"):
                    st.markdown(analysis_prompt)

                # Generate and display assistant response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Construct the prompt with history
                        history_context = "\n".join([f"**{m['role']}**: {m['content']}" for m in st.session_state.analysis_history])
                        analysis_full_prompt = "\n".join([
                            "You are an expert API assistant. Your task is to analyze the provided OpenAPI 3.0 specification and answer the user's questions about it in a clear and concise way.",
                            "You must maintain a conversational context based on the chat history provided.",
                            "",
                            "OpenAPI Specification:",
                            "```yaml",
                            string_data,
                            "```",
                            "---",
                            "Chat History:",
                            history_context,
                            "---"
                        ])

                        response_text, error = get_gemini_response(model, analysis_full_prompt)
                        if error:
                            st.error(error[0])
                        else:
                            st.markdown(response_text)
                            st.session_state.analysis_history.append({"role": "assistant", "content": response_text})

        with erp_tab:
            st.subheader("Generate ERP Integration Code")
            st.markdown("Generate a code snippet to integrate the API with an ERP system.")

            # Display previous generations
            for item in st.session_state.erp_history:
                st.markdown(f"**Your Request:** `{item['prompt']}` for `{item['language']}`")
                st.markdown(item['response'])
                st.divider()

            erp_prompt = st.text_input(
                "Describe the integration logic (e.g., 'sync new pets to our ERP as products')",
                key="erp_prompt"
            )
            erp_language = st.text_input(
                "Specify the language or ERP system (e.g., 'Python', 'SAP ABAP', 'NetSuite SuiteScript')",
                key="erp_language"
            )

            if st.button("Generate Integration Code"):
                if not erp_prompt or not erp_language:
                    st.warning("Please describe the integration logic and specify the language/system.")
                else:
                    with st.spinner("Generating integration code..."):
                        logging.info(f"Generating ERP integration for prompt: '{erp_prompt}' in '{erp_language}'")
                        erp_full_prompt = "\n".join([
                            "You are a world-class ERP integration specialist. Your task is to write integration code that connects a system described by an OpenAPI specification to an ERP system.",
                            f"The user wants to generate code in '{erp_language}'.",
                            "",
                            "Based on the following OpenAPI 3.0 specification, write a code snippet that accomplishes the user's goal.",
                            "OpenAPI Specification:",
                            "```yaml",
                            string_data,
                            "```",
                            f"User's Goal: \"{erp_prompt}\"",
                            "",
                            "Provide a complete, well-commented code snippet that is ready to be used. Explain the purpose of the code and any prerequisites (like libraries to install)."
                        ])

                        response_text, error = get_gemini_response(model, erp_full_prompt)
                        if error:
                            st.error(error[0])
                        else:
                            st.session_state.erp_history.append({
                                "prompt": erp_prompt, 
                                "language": erp_language, 
                                "response": response_text
                            })
                            # The script will rerun automatically after the button press, no need for forceful rerun.
        
        with editor_tab:
            st.subheader("Interactive Swagger Editor")
            # URL encoding is not safe for large specs (>~4KB), which can cause a 414 error.
            # We use a hybrid approach: direct embedding for small files, Gist for large ones.
            if len(string_data.encode('utf-8')) < 4096:
                # For small specs, encode and embed directly in the URL for a seamless experience.
                # The spec must be URL-encoded.
                url_encoded_spec = urllib.parse.quote(string_data)
                editor_url = f"https://editor-next.swagger.io/?spec={url_encoded_spec}"
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