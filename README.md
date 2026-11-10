# Medical LLM Chatbot

A retrieval-augmented generation (RAG) chatbot that answers questions using information retrieved from a medical PDF knowledge source. It uses **LangChain** to manage the RAG workflow, **Sentence Transformers** to create embeddings, **Pinecone** to search the document vectors, **Groq** to generate answers, and **Flask** to provide a web interface.

> **Disclaimer:** This is an educational project, not a medical device. Its responses may be incomplete or incorrect and must not be used as a substitute for professional medical advice, diagnosis, or treatment. Consult a qualified healthcare professional for medical concerns.

## How it works

1. **Load the source document:** The ingestion script reads PDF files from the `data/` directory.
2. **Split the text:** The extracted text is divided into smaller chunks (currently 500 characters, with 20 characters of overlap).
3. **Create embeddings:** The `sentence-transformers/all-MiniLM-L6-v2` model converts each text chunk into a numerical vector.
4. **Store vectors:** The vectors and their text are stored in a Pinecone index named `medical-chatbot`.
5. **Retrieve context:** When a user asks a question, the application searches Pinecone for the three most similar chunks.
6. **Generate an answer:** The retrieved context and question are sent to the Groq chat model configured in `app.py` (`openai/gpt-oss-120b`).
7. **Display the response:** Flask serves the chat page and returns the generated answer to the browser.

## Technology stack

| Technology | Purpose |
|---|---|
| Python | Application language |
| Flask | Web application |
| LangChain | RAG pipeline and prompt orchestration |
| Sentence Transformers | Text embeddings |
| Pinecone | Vector database and similarity search |
| Groq | Language-model inference |
| Docker | Application containerization |
| GitHub Actions | CI/CD automation |
| Amazon ECR | Docker image registry |
| AWS EC2 | Application host |

## Project structure

```text
Medical-LLM-Chatbot/
├── .github/
│   └── workflows/
│       └── cicd.yaml       # GitHub Actions CI/CD workflow
├── data/
│   └── Medical_book.pdf   # PDF knowledge source
├── research_notebooks/    # Experiments and development notebooks
├── src/
│   ├── __init__.py
│   ├── helper.py           # PDF loading, text splitting, embeddings
│   └── prompt.py           # System prompt for the chatbot
├── static/                 # CSS and other static assets
├── templates/
│   └── chat.html            # Chat interface
├── app.py                   # Flask application and RAG chain
├── store_index.py           # Creates/populates Pinecone index
├── requirements.txt         # Python dependencies
├── setup.py                 # Python package metadata
└── Dockerfile               # Docker image instructions
```

## Run the project locally

### 1. Clone the repository

```bash
git clone https://github.com/shanu202000/Medical-LLM-Chatbot.git
cd Medical-LLM-Chatbot
```

### 2. Create and activate a virtual environment

The repository's Dockerfile currently uses Python 3.12. Use a Python version supported by all packages in `requirements.txt`.

**Windows (PowerShell):**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Dependency note:** The current `app.py` imports Flask, but `Flask` is not listed in the repository's current `requirements.txt`. Add `Flask` to `requirements.txt` and reinstall the dependencies, or install it directly with `pip install Flask` before running the app.

### 4. Add API keys

Create a file named `.env` in the repository root:

```env
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholders with your own keys. Keep `.env` private. It is already covered by the repository's `.gitignore`; never commit API keys or paste them into public logs or screenshots.

### 5. Build the Pinecone knowledge index

Run the ingestion script from the repository root:

```bash
python store_index.py
```

This script reads PDFs from `data/`, creates text embeddings, and stores them in the Pinecone index. The current code uses:

- Index name: `medical-chatbot`
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Vector dimension: `384`
- Pinecone region configured in the script: `us-east-1`

Run ingestion when you first set up the knowledge base or after changing the source PDF. The Pinecone index must exist and contain vectors before the chat application can retrieve relevant context.

### 6. Start the application

```bash
python app.py
```

Open the chat interface at **http://localhost:8080**.

## Run with Docker

The repository's Dockerfile copies the project files into the image before installing dependencies. This is important if you later add a local editable install such as `-e .` to `requirements.txt`, because `setup.py` and the package source must then already be present.

Build the image from the project root:

```bash
docker build -t medical-llm-chatbot .
```

Run the container with the required application keys:

```bash
docker run --rm -p 8080:8080 \
  -e PINECONE_API_KEY="your_pinecone_api_key" \
  -e GROQ_API_KEY="your_groq_api_key" \
  medical-llm-chatbot
```

Or, for local testing, pass the `.env` file:

```bash
docker run --rm -p 8080:8080 --env-file .env medical-llm-chatbot
```

Then visit **http://localhost:8080**. Do not copy your local `.venv/` directory into the image; use a `.dockerignore` file to exclude `.venv/`, `.env`, `.git/`, and `__pycache__/`.

## AWS deployment with GitHub Actions

The repository contains a workflow at `.github/workflows/cicd.yaml`. It is triggered by pushes to the `main` branch and has two jobs:

### Continuous Integration (GitHub-hosted runner)

The job runs on `ubuntu-latest`. It checks out the repository, configures AWS credentials, logs in to Amazon ECR, builds the Docker image, and pushes the image to the ECR repository configured in GitHub secrets.

### Continuous Deployment (self-hosted runner)

The job runs on `self-hosted`. The intended setup is an Ubuntu EC2 instance with Docker installed and a GitHub Actions self-hosted runner registered to this repository. After the CI job succeeds, the deployment job logs in to ECR and starts the container with port `8080` mapped.

### AWS resources to prepare

- An Amazon ECR repository to store the Docker image.
- An Ubuntu EC2 instance with Docker installed.
- A GitHub Actions self-hosted runner installed and registered on the EC2 instance; it must be online when the workflow runs.
- An EC2 security-group inbound rule for port `8080`, restricted to the intended client IP ranges.
- An IAM identity with permissions limited to the required ECR operations.

### GitHub Actions repository secrets

Add the following under **Settings → Secrets and variables → Actions** in the GitHub repository:

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS access key used by the workflow |
| `AWS_SECRET_ACCESS_KEY` | Matching AWS secret key |
| `AWS_DEFAULT_REGION` | Region containing the ECR repository |
| `ECR_REPO` | ECR repository name |
| `PINECONE_API_KEY` | Pinecone key used by the application |
| `GROQ_API_KEY` | Groq key used by the application |

### Deployment notes

- The workflow currently tags the image as `latest`. A commit-SHA tag can make releases easier to trace and roll back.
- The current deployment command starts a container but does not explicitly stop and remove a previous container. Add a controlled replacement step before using this as a repeatable production deployment.
- Make sure the deployment runner actually pulls the new image from ECR before starting it; otherwise, a locally cached image with the same `latest` tag may be used.
- The current workflow passes AWS access keys into the application container. The current `app.py` uses the Pinecone and Groq keys, not AWS keys. Avoid passing long-lived AWS credentials into the container unless the application genuinely needs them. Prefer an EC2 instance role for AWS access from the instance.
- Pin and review GitHub Actions versions and use least-privilege IAM permissions before production use.

## Troubleshooting

| Problem | What to check |
|---|---|
| Pinecone authentication fails | Confirm `PINECONE_API_KEY` is present and valid. |
| Index not found or no relevant context | Run `python store_index.py`; confirm the `medical-chatbot` index exists and contains vectors. |
| Groq authentication/model error | Confirm `GROQ_API_KEY` and check that the model configured in `app.py` is available to your account. |
| `ModuleNotFoundError: flask` | Add `Flask` to `requirements.txt` and reinstall dependencies. |
| Docker build fails while installing dependencies | Review the first package error above the final `exit code: 1`; check Python/package compatibility. |
| EC2 app cannot be reached | Confirm the container is running, port `8080` is mapped, and the EC2 security group allows intended traffic. |
| GitHub deployment job stays queued | Confirm the self-hosted runner is registered, online, and has the required labels. |

To inspect a running container:

```bash
docker ps
docker logs <container_id>
```

## License

See the [LICENSE](LICENSE) file in this repository.
