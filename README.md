# Spam & Biorhaphy talks: an AI project containing three microservices: RAG, Spam Detection, and LangChain Agent uniting both previous

This project demonstrates a microservices architecture where three separate services — RAG (biography search), Spam Detection, and LangChain Agent are containerized and communicate via HTTP. A Gradio interface acts as a client to interact with the LangChain Agent.

## Prerequisites

- **Docker:**  
  Ensure that Docker is installed on your PC before running the project.  
  You can download and install Docker from [Docker's Official Website](https://www.docker.com/get-started).

- **OpenAI API Key:**  
  Before building the containers, set your OpenAI API key as an environment variable.  
  In working directory create `.env` file and insert following:

  ```bash
  OPENAI_API_KEY="your_openai_api_key_here"
  ```

  Change `your_openai_api_key_here` with your actual key

## How to start:

### First launch:

When launched at the first time build containers using command:

```bash
docker-compose up --build
```

Wait untill all dependencies are installed. Press `Ctrl+C` to stop containers.

### Running after building:

After first launch use:

```bash
docker-compose up
```

To launch containers.

### Running client:

To be able to use LC agent run Gradio interface. In this directory at `gradio_interface\gradio_interface_ms.py` right-click and select `Run Python - Run Python File in Terminal`. Gradio will run at `http://127.0.0.1:7860`
