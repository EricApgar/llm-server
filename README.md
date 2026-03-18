# llm-server
Host an LLM as a non-blocking HTTP server with a simple interface for managing and querying models. Built on [FastAPI](https://fastapi.tiangolo.com/) and [uvicorn](https://www.uvicorn.org/), it wraps the [large-language-model](https://github.com/EricApgar/large-language-model) library to expose LLM inference over a REST API.

# Setup
See [Releases](https://github.com/EricApgar/llm-server/releases) to install from wheel file.

See ```pyproject.toml``` for required Python version and dependencies.

## Optional Dependencies
This library uses optional dependencies for additional features. See the ```pyproject.toml``` for the list of optional library tags. To install with the GUI support, use the ```gui``` tag.

## Library
Install this repo as a library into another project.

### ...with uv:
```
uv add "llm_server @ git+https://github.com/EricApgar/llm-server"
```

...with optional libraries:
```
uv add "llm_server[gui] @ git+https://github.com/EricApgar/llm-server"
```

### ...with pip:
```
pip install "llm_server @ git+https://github.com/EricApgar/llm-server"
```

...with optional libraries:
```
pip install "llm_server[gui] @ git+https://github.com/EricApgar/llm-server"
```

## Repo
Run locally for development of this repo.
Create a virtual environment and then install the dependencies into the environment.

### ...with uv:
```
uv sync
```

...with optional libraries:
```
uv sync --extra gui
```

### ...with pip:
```
pip install -e "."
```

...with optional libraries:
```
pip install -e ".[gui]"
```

## Hardware
Running an LLM requires an NVIDIA GPU with ideally a large number of TOPS. See the [large-language-model](https://github.com/EricApgar/large-language-model) repo for hardware details and GPU driver setup.

# Usage
Create a server, register a model with a tag, load it, and start serving. Then send a request and receive a response.

## Server
```
import llm_server


server = llm_server.Server()
server.set_host(ip_address='127.0.0.1', port=8000)
server.add_model(tag='gpt', name='openai/gpt-oss-20b')
server.load_model(tag='gpt', location=<path to model cache dir>)
server.start()  # Non-blocking.

server.stop()
```

## Requester
```
URL = 'http://127.0.0.1:8001/ask'
details = {...}  # See request body examples below.

response = requests.post(URL, json=details, timeout=15)
data = response.json()
print(data['text'])
```

# API Endpoints
| Method | Endpoint | Description |
|-|-|-|
| GET | `/` | Health check — returns `"Running."`. |
| GET | `/get-models` | List all available hosted models and their tags. |
| GET | `/ask-test` | Send a test prompt (`"Tell me a joke."`) to the first available model. |
| POST | `/ask` | Send a prompt to a specific model. |

### POST /ask — Request Body

#### Text Example
```
{
    "tag": "gpt",
    "prompt": "Tell me a joke.",
    "max_tokens": 64,
    "temperature": 0.9
}
```
* `prompt` may also be a Conversation formatted dict output (see [llm-conversation](https://github.com/EricApgar/llm-conversation)). 
    * ```llm_conversation.Conversation.to_dict()```

#### Image Example
```
{
    "tag": "Phi4",
    "prompt": "Describe the image.",
    "images": [llm_server.encode_image(<path to image>)],
    "max_tokens": 64,
}
```
* ```temperature``` arg currently not supported for Phi-4-multimodal-instruct.
* ```images``` accepts base64-encoded PNG strings for multimodal models. Encoder is provided by ```llm_server```.