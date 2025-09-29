# Request body/parameters Generator

This tool is a Streamlit web application that generates sample API request bodies from a provided OpenAPI (YAML) specification. It leverages the power of Google's Gemini large language model to understand natural language prompts and create accurate JSON examples.

## Features

- **Intuitive Web Interface**: Built with Streamlit for a clean and simple user experience.
- **Dynamic OpenAPI Parsing**: Upload any OpenAPI 3.0 specification in YAML format.
- **Natural Language Prompts**: Instead of manually searching for endpoints, simply describe the request you need (e.g., "add a new pet to the store").
- **AI-Powered Generation**: Uses the Google Gemini API to intelligently generate a valid JSON request body with realistic example values.
- **Error Handling**: Provides feedback for API rate limits and other potential issues.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.8+
- A Google AI API Key. You can obtain one for free from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ranjithmadheswaran/mcp_server.git
    cd mcp_server
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

1.  Navigate to the project's root directory (`mcp_server`).
2.  Run the Streamlit application from your terminal:
    ```bash
    streamlit run src/app.py
    ```
3.  Your web browser should automatically open a new tab with the running application.

## How to Use

1.  **Enter API Key**: Paste your Google AI API Key into the first input field.
2.  **Upload Spec**: Click the "Browse files" button to upload your OpenAPI `.yaml` or `.yml` file. The application will confirm once it's successfully parsed.
3.  **Describe Request**: In the text input field, describe the API operation for which you want to generate a request (e.g., "Find pets by status" or "create a new user").
4.  **Generate**: Click the "Generate Request" button.
5.  **View Result**: The generated JSON request body will appear below the button.

## Project Structure

```
mcp_server/
├── src/
│   └── requestCreator.py             # The core Streamlit application logic
├── petStore.yaml          # An example OpenAPI specification file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```