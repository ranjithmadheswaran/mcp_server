# Request body/parameters Generator

This tool is a Streamlit web application that generates sample API request bodies from a provided OpenAPI (YAML) specification. It leverages the power of Google's Gemini large language model to understand natural language prompts and create accurate JSON examples.

## Features

- **Intuitive Web Interface**: Built with Streamlit for a clean and simple user experience.
- **Tabbed Interface**: For easy navigation between different functionalities.
- **Dynamic OpenAPI Parsing**: Upload any OpenAPI 3.0 specification in YAML format.
- **Natural Language Prompts**: Instead of manually searching for endpoints, simply describe the request you need (e.g., "add a new pet to the store").
- **AI-Powered Generation**: Uses the Google Gemini API to intelligently generate a valid JSON request body with realistic example values.
- **AI-Powered Specification Analysis**: Ask natural language questions about your API spec and get instant answers.
- **Interactive Swagger Editor**: Visualize and interact with your API specification directly within the app.
- **Raw Spec Viewer**: A simple text area to view the full content of your uploaded file.
- **Error Handling**: Provides feedback for API rate limits and other potential issues.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.8+
- A Google AI API Key. You can obtain one for free from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ranjithmadheswaran/swaggerRequestGenerator.git
    cd swaggerRequestGenerator
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1.  Navigate to the project's root directory (`swaggerRequestGenerator`).
2.  Run the Streamlit application from your terminal:
    ```bash
    streamlit run src/requestCreator.py
    ```
3.  Your web browser should automatically open a new tab with the running application.

## How to Use

1.  **Enter API Key**: Paste your Google AI API Key into the input field. The application will fetch the list of models available to you.
2.  **Select a Model**: Choose a generative model from the dropdown list. The application will attempt to select a powerful default like `gemini-2.5-flash` or `gemini-pro` if available.
3.  **Upload Spec**: Click the "Browse files" button to upload your OpenAPI `.yaml` or `.yml` file.
4.  **Interact with Tabs**: Once the file is parsed, you can use the tabs for different actions:
    -   **Generate Request**: Describe the API operation you need and click "Generate Request" to get a JSON example.
    -   **Analyze Specification**: Ask a question about the API (e.g., "What endpoints are available for users?") and click "Analyze" to get a summary from the AI.
    -   **Swagger Editor**: View and interact with your API in an embedded, interactive editor. For very large files, you may be prompted to use a Gist.
    -   **View Specification**: See the raw YAML content of your uploaded file.

## Project Structure

```
swaggerRequestGenerator/
├── src/
│   └── requestCreator.py             # The core Streamlit application logic
├── petStore.yaml          # An example OpenAPI specification file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```
