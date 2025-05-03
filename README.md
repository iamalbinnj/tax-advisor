# TaxAdvisor

TaxAdvisor is a Retrieval-Augmented Generation (RAG) system built using Ollama AI to provide tax advice and information. The application leverages the Zephyr 7B Beta model for text generation and Nomic Embed Text for embeddings.

## Prerequisites

- [Node.js](https://nodejs.org/) (v16+)
- [Python](https://www.python.org/) (v3.8+)
- [Ollama](https://ollama.ai/) (latest version)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/iamalbinnj/tax-advisor.git
cd tax-advisor
```

### 2. Pull the dataset and vector database

The dataset and vector database are available as a Docker image:

```bash
docker pull albinnj/taxadvisor:latest
```

To extract the dataset and vector database from the Docker image:

```bash
# Create a container from the image
docker create --name taxadvisor-data albinnj/taxadvisor:latest

# Copy the dataset and vector database to your local system
docker cp taxadvisor-data:/app/dataset ./dataset
docker cp taxadvisor-data:/app/model ./model/

# Remove the temporary container
docker rm taxadvisor-data
```

### 3. Set up Ollama and required models

First, ensure Ollama is installed on your system. Then download the required models:

```bash
# Start Ollama service
ollama serve

# In a new terminal, pull the text generation model
ollama pull zephyr:7b-beta-q4_K_S

# Pull the embedding model
ollama pull nomic-embed-text
```

### 4. Set up the Python Environment

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Set up the Web Frontend

```bash
cd web
npm install
```

## Running the Application

### Start Ollama

Ensure Ollama is running:

```bash
ollama serve
```

### Run the API

```bash
# Run the API server
cd api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run the Web Application

#### Development mode

```bash
cd web
npm run dev
```

#### Production mode

```bash
cd web
npm run build
npm start
```

<!-- ## Environment Variables

Create a `.env` file in the api directory with the following variables:

```
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
GENERATION_MODEL=zephyr:7b-beta-q4_K_S
VECTOR_DB_PATH=../dataset/vector_db
``` -->

## Project Structure

```
taxadvisor/
├── api/                # FastAPI backend
├── dataset/            # Tax data for the RAG system
├── model/              # Model configuration files
├── notebook/           # Jupyter notebooks for development/testing
├── web/                # Frontend application
├── .dockerignore       # Docker ignore file
├── .gitignore          # Git ignore file
├── Dockerfile          # Docker configuration
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Docker Support

You can also run the entire application using Docker:

```bash
# Build the Docker image
docker build -t taxadvisor:latest .

# Run the Docker container
docker run -p 8000:8000 -p 3000:3000 taxadvisor:latest
```

## Contributing

Thank you for considering contributing to TaxAdvisor! Here's how you can help:

### Contribution Guidelines

1. **Fork the repository**
   - Go to the project repository on GitHub: https://github.com/iamalbinnj/tax-advisor
   - Click the "Fork" button in the upper right corner
   - This will create a copy of the repository in your GitHub account

2. **Create a branch**
   - Create a branch with a descriptive name related to your contribution:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Implement your feature or bug fix
   - Write or update tests as needed
   - Add or update documentation as needed

4. **Follow the code style**
   - Python: Follow PEP 8 guidelines
   - JavaScript/TypeScript: Follow the project's ESLint configuration
   - Include meaningful comments where necessary

5. **Commit your changes**
   - Use clear and meaningful commit messages
   - Reference issue numbers if applicable
   ```bash
   git commit -m "Add feature X that does Y (fixes #123)"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a pull request**
   - Go to the original repository and create a pull request
   - Provide a clear description of the changes
   - Link any relevant issues

<!-- ### Development Setup Tips

1. **Setting up a development environment**
   - Follow the installation instructions above
   - For the API, consider using a tool like `pytest` for testing
   - For the web app, use the built-in linting and testing tools

2. **Testing**
   - Write unit tests for new features
   - Ensure all tests pass before submitting a pull request
   - Test your changes in different environments if possible

3. **Documentation**
   - Update documentation to reflect your changes
   - Document any new features or APIs
   - Include examples where appropriate -->

### Code of Conduct

- Be respectful and inclusive in your communications
- Provide constructive feedback
- Help create a positive community

## License
