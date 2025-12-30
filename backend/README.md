### Downloading Models

You will need to download a model to use. This can be done via the hugging face cli

For example the following will download the Qwen3 1.7B model to the `qwen3-1.7B` folder in the current directory

```bash
uvx hf download Qwen/Qwen3-1.7B --local-dir=./qwen3-1.7B
```

### Local Environment Setup

Create an `.env` file with the following contents:

```dotenv
# Disable serving static files when running locally, since UI will be run seperatly
CC_SERVE_STATIC_FILES=false
# Path to the model (path downloaded to in previous step)
CC_MODEL_PATH=/path/to/model/to/use/qwen3-1.7B

# Database connection info
CC_DB_HOST=
CC_DB_PORT=
CC_DB_USER=
CC_DB_PASSWORD=
CC_DB_DATABASE=
```

### Running application

```bash
uvicorn src.main:app --port 5005 --env-file=.env
```