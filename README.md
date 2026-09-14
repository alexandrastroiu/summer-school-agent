# Milan City Guide AI Assistant

A travel assistant designed to answer questions about Milan, provide travel recommendations, and estimate ticket costs for a group of tourists based on the number of visitors, visitor categories and selected attractions using a custom tool.

The project was developed during the **Google Cloud and Agentic AI Summer School at POLITEHNICA Bucharest**.

## Project status

The application was successfully deployed to Google Cloud Run, using Vertex AI for Gemini access and Cloud Storage for the knowledge base.

The live deployment is no longer available because the temporary Google Cloud project provided during the summer school was deleted after the program. The application can be deployed again using a new Google Cloud project.

## Key features

- Conversational assistant built with Google ADK and designed to use Gemini through Vertex AI
- Markdown knowledge base containing information about the city, travel tips and tourist attractions
- Document listing, reading, and keyword-search tools
- Custom tool for attraction cost estimation
- Automated unit tests
- Docker support for consistent execution across environments
- Support for local files and Google Cloud Storage as knowledge sources

## Application architecture

```text
User
  |
  v
ADK Agent
  |
  +-- list_documents()
  |
  +-- read_document(filename)
  |
  +-- search_documents(keyword)
  |
  |
  |
  +-- estimate_ticket_cost(number_of_visitors, visitor_categories, attractions)

             |
             v
       KnowledgeProvider
          /       \
         /         \
Local files      Cloud Storage
```

The application initially uses `LocalKnowledgeProvider`. It can switch from local Markdown files to Google Cloud Storage by selecting `CloudKnowledgeProvider` without changing the agent or its tools.

## Repository structure

```text
summer-school-agent/
|
|-- app/
|   |-- __init__.py
|   |-- agent.py
|   |-- config.py
|   |-- knowledge.py
|   |-- prompts.py
|   `-- tools.py
|
|-- knowledge/
|   |-- attractions.md
|   |-- average_travel_costs.md
|   |-- events.md
|   |-- faq.md
|   |-- food_and_shopping.md
|   |-- milan_overview.md
|   `-- transportation.md
|
|-- scripts/
|   |-- generate_dependency_files.py
|   |-- upload_knowledge.py
|   `-- verify_local_setup.py
|
|-- tests/
|   |-- __init__.py
|   |-- test_agent.py
|   |-- test_custom_tool.py
|   |-- test_knowledge.py
|   `-- test_tools.py
|
|-- .env.example
|-- .gitignore
|-- .dockerignore
|-- Dockerfile
|-- main.py
|-- server.py
|-- requirements.txt
|-- requirements-lock.txt
`-- README.md
```

## Custom tool: attraction cost estimator

 The application includes a custom tool that estimates the ticket cost and provides a cost breakdown for a trip to Milan. The calculation is based on the number of people, the selected attractions and the visitor category for each person in the group.

```python
 estimate_ticket_cost( 
  number_of_visitors, 
  visitor_categories, 
  attractions 
  )
 ```

 The tool uses information stored in the `average_travel_costs.md` file and accounts for different visitor categories when calculating the result. Actual ticket prices are subject to change, so the results should be treated as estimates.

## Technologies
- Python 3.13
- Google Agent Development Kit (ADK)
- Gemini through Vertex AI
- Google Cloud Storage
- Google Cloud Run
- Docker

## Prerequisites

Install the following:

- Python 3.13
- Git
- Google Cloud CLI
- Visual Studio Code or another Python editor
- Docker Desktop or Docker Engine, if running the containerized version

Verify the local tools:

```bash
python3.13 --version
git --version
gcloud --version
docker --version
```

**Running the interactive assistant requires an active Google Cloud project, valid Google Cloud credentials, and access to Vertex AI.**

## Local setup

### 1. Open the repository

```bash
cd summer-school-agent
```

### 2. Create a Python 3.13 virtual environment

macOS or Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Verify the active Python interpreter

```bash
python --version
```

Expected:

```text
Python 3.13.x
```

On macOS or Linux, also check:

```bash
which python
```

The path should point inside:

```text
summer-school-agent/.venv/
```

### 4. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Local configuration

Create the local environment file.

macOS or Linux:

```bash
cp .env.example .env
```

Windows Command Prompt:

```cmd
copy .env.example .env
```

Use the following configuration for local execution:

```text
MODEL=gemini-2.5-flash

KNOWLEDGE_SOURCE=local
LOCAL_KNOWLEDGE_DIRECTORY=knowledge

GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=global

KNOWLEDGE_BUCKET=
```

The empty cloud fields are valid while:

```text
KNOWLEDGE_SOURCE=local
```

## Run the local demonstration

```bash
python main.py
```

This command:

1. loads the local knowledge provider;
2. lists the available Markdown files;
3. reads one document;
4. searches the knowledge base;
5. displays matching excerpts.

It does not call Gemini and does not connect to Google Cloud.

## Verify the complete local setup

```bash
python scripts/verify_local_setup.py
```

Expected final result:

```text
All local checks passed.
No Google Cloud request or Gemini request was made.
```

## Run the automated tests

```bash
python -m unittest discover -s tests -v
```

The tests cover:

- local document discovery
- local document reading
- missing-document handling
- keyword search
- attraction cost calculation
- structured tool responses
- mocked Cloud Storage behavior
- ADK agent construction

The Cloud Storage tests use a mocked client and make no network requests.

## Preview the future Cloud Storage upload

```bash
python scripts/upload_knowledge.py --dry-run
```

This displays the files that will eventually be uploaded.

It does not contact Google Cloud.

## ADK agent

The agent is defined in:

```text
app/agent.py
```

The package exposes:

```python
root_agent
```

The agent currently has four tools:

```text
list_documents
read_document
search_documents
estimate_ticket_cost
```

The tools use the local knowledge provider until cloud mode is enabled.

## Run with Docker

Build and run the application locally using Docker. 

Build the image:

```bash
docker build \
  --tag summer-school-agent:local \
  .
```

Run the container:

```bash
docker run --rm -d \
  --name summer-school-agent-local \
  -p 8080:8080 \
  --env-file .env \
  -v "$HOME/.config/gcloud/application_default_credentials.json:/tmp/adc.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/adc.json \
  summer-school-agent:local
```

After the container starts, open [http://localhost:8080](http://localhost:8080) in a browser.


## Cloud setup

Complete this section after creating a new Google Cloud project.

Authenticate:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default login
```

Update `.env`:

```text
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
KNOWLEDGE_BUCKET=YOUR_UNIQUE_BUCKET_NAME
```

The initial Gemini test may still use:

```text
KNOWLEDGE_SOURCE=local
```

This allows the ADK agent to use Gemini through Vertex AI while retrieving knowledge from the local Markdown files.

Later, after creating the bucket and uploading the files, switch to:

```text
KNOWLEDGE_SOURCE=cloud
```

## Upload the knowledge base

After the bucket exists:

```bash
python scripts/upload_knowledge.py
```

Verify the upload plan first:

```bash
python scripts/upload_knowledge.py --dry-run
```

## Run the ADK development interface

After Google Cloud authentication is configured:

```bash
adk web
```

Alternatively, use the terminal interface:

```bash
adk run app
```

Do not run these commands before the Vertex AI configuration and authentication steps are complete.

## Useful test prompts

Once the ADK agent is connected to Gemini:

```text
What documents are available?
What can I visit in Milan?
What is the best time to visit Milan?
Estimate the ticket cost for two adults visiting the Scala Museum and the Royal Palace of Milan.
```