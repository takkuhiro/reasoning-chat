# Reasoning Chat

A sophisticated AI chat system built with Python that implements reasoning capabilities and memory management. The system uses OpenAI's models and includes various tools for enhanced functionality.

## Features

- Reasoning-based conversation flow
- Memory management for conversation context
- Integration with multiple tools:
  - Google Search functionality by Dify (not included in this repo)
  - Telephone number lookup by Dify (not included in this repo)
  - Memory updating capability by Dify (not included in this repo)
- Chainlit-based chat interface
- Docker support for easy deployment

## Prerequisites

- Python 3.13+
- Poetry
- Docker
- Google Cloud Platform account (for deployment)
- Required API keys:
  - OpenAI API key
  - Dify API keys (for Google Search and Telephone tools)

## Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd reasoning-chat
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file with required environment variables:
```bash
MODE=development
OPENAI_API_KEY=your_openai_api_key
DIFY_GOOGLESEARCH_API_ENDPOINT=your_dify_googlesearch_endpoint
DIFY_GOOGLESEARCH_API_KEY=your_dify_googlesearch_api_key
DIFY_TELEPHONE_API_ENDPOINT=your_dify_telephone_endpoint
DIFY_TELEPHONE_API_KEY=your_dify_telephone_api_key
```

4. Run the application locally:
```bash
poetry run chainlit run src/main.py
```

## Development Commands

- Format code:
```bash
make format
```

- Run linting:
```bash
make lint
```

- Run both format and lint:
```bash
make check
```

## Docker Build and Deployment

### Local Docker Build

1. Build the Docker image:
```bash
make build
```

2. Run the container locally:
```bash
docker compose up app
```

### Deploy to Google Cloud Run

1. Set up your Google Cloud environment variables:
```bash
export GCP_PROJECT_ID=your_project_id
export GCP_REGION=your_region
```

2. Build and push the image:
```bash
make build
make push
```

3. Deploy to Cloud Run:
```bash
make deploy
```

## Project Structure

- `src/`: Main application code
  - `tools/`: Custom tool implementations
  - `config/`: Configuration settings
  - `main.py`: Application entry point
  - `memory.py`: Memory management implementation
  - `prompts.py`: System prompts
- `Dockerfile`: Container configuration
- `compose.yml`: Docker Compose configuration
- `pyproject.toml`: Python project configuration

## Technical Details

- Uses Python 3.13
- Built with Chainlit for chat interface
- Implements OpenAI's GPT models
- Includes custom tools for Google Search and telephone number lookup
- Features an experimental memory system for context retention
- Supports both development and production configurations
