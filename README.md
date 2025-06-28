# K8s Copilot

An interactive AI assistant to manage Kubernetes with natural language, powered by `fast-agent` and modern LLMs.

This project aims to create a "K8s Copilot" that allows developers, testers, and operations engineers to interact with Kubernetes clusters using simple, conversational language. It dramatically lowers the barrier to entry for K8s and improves day-to-day operational efficiency.

## 📚 Documentation

For a detailed understanding of the project's vision, features, and MVP plan, please refer to our documentation:

- **[Product Requirements Document (PRD.md)](./doc/PRD.md)**: Defines the "what" and "why" of this project.
- **[Technical Architecture (ARCHITECTURE.md)](./doc/ARCHITECTURE.md)**: Outlines the technical design and "how" we will build it.

## 🚀 Getting Started (MVP)

_Instructions to be refined as development progresses._

1.  **Setup Environment**:
    ```bash
    # Create a virtual environment using uv
    uv venv

    # Activate the environment
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    # Install required packages
    uv pip install -r requirements.txt
    ```

3.  **Configure**:
    - Copy `.env.example` to `.env`.
    - Fill in your `OPENROUTER_API_KEY`.

4.  **Run the CLI**:
    ```bash
    python src/main.py
    ``` 