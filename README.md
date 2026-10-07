# Hyperion Agent

Built by team **Solo Bolo** for Veles Hack 2026, Challenge 1 by HYPER-AI, *Hyperion, an LLM powered agentic assistant*.

Hyperion is the chat assistant of the [HyperAI IDE](https://ide.hyperai.di.uoa.gr/). It answers questions about HYPER-AI from the project's documents, turns plain language requests into IDE actions (create, edit, validate and delete files), remembers the conversation, declines off topic requests and asks before deleting or overwriting anything.

It is a [FastAPI](https://fastapi.tiangolo.com/) service on **port 8000** with a `POST /chat` endpoint that streams its reply to the IDE as Server Sent Events (SSE). The deliverable is the Docker image **`paolo189/hyperion`** with version tags, where `latest` is always the newest version.

```
You        Create a deployment YAML for a service using the nginx Docker image
Hyperion   Writing `nginx.yaml`...
           Created `nginx.yaml` as a native app profile. It is open in the editor.
           Checked it with the IDE validator: valid.
You        change the cpu to 250m
Hyperion   Updating `nginx.yaml`...
           Updated `nginx.yaml`. It is open in the editor.
           Checked it with the IDE validator: valid.
You        delete it
Hyperion   Please confirm: delete `nginx.yaml`? Reply yes or no.
You        yes
Hyperion   Deleted `nginx.yaml`.
```

## Features

| Challenge criterion | How Hyperion covers it |
|---|---|
| Answers questions about HYPER-AI | Retrieval over the HYPER-AI documents and the IDE documentation, and every answer names its sources |
| Natural language to IDE actions | Creates, edits, reads, validates and deletes files and folders through the IDE's action events, and writes app profiles from valid templates |
| Guardrails | Off topic requests are declined, role change and prompt injection attempts are refused, paths outside the workspace are refused, and existing files are only touched when the user refers to them |
| RAG | 12 documents, 77 chunks, hybrid search (embeddings plus keyword match), with the index shipped inside the image |
| Memory | Conversation history per IDE session (`user_id`), trimmed to fit the model's 8k token context, and recently used files are remembered |
| Human in the loop (optional) | Deleting a file or folder and overwriting an existing file wait for an explicit "yes" |

Every generated or edited app profile is checked with the IDE's own validator, and validation errors are fixed automatically in up to two rounds.

## Running it

### 1. Start the HyperAI IDE locally

Each command runs in the foreground, so use one terminal per service.

```bash
docker run --rm -p 3001:3001 -e AUTH_ENABLED=false --name ide-backend donmichael/ide-backend:latest
docker run --rm -p 5000:80 --name ide-gui donmichael/ide-gui:latest
```

Then open the IDE at <http://localhost:5000/>.

### 2. Start Hyperion

Hyperion needs a key for the LLM server provided by the organizers (`legion1.di.uoa.gr`), passed as the `API_KEY` environment variable. The key is never stored in the image.

**From Docker Hub**

```bash
docker run --rm -p 8000:8000 -e API_KEY=<your key> \
  --add-host=host.docker.internal:host-gateway paolo189/hyperion:latest
```

**From source**, after copying `.env.example` to `.env` and adding the key

```bash
docker compose up --build    # in Docker
uv run main.py               # or locally with uv
```

Then open **Hyperion** in the IDE sidebar (the robot icon) and start typing. You can also call the endpoint directly.

```bash
curl -N -X POST http://localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"user_id": "123e4567-e89b-12d3-a456-426614174000", "text": "What is HyperAI?"}'
```

| Variable | Default | Purpose |
|---|---|---|
| `API_KEY` | none, required | Key for the LLM server |
| `IDE_BACKEND_URL` | `http://localhost:3001/api`, or `http://host.docker.internal:3001/api` inside the image | Where Hyperion reads and validates workspace files |

## How it works

```
IDE  ──POST /chat {user_id, text}──►  Hyperion  ──►  legion1 (llama3.1, nomic-embed-text)
     ◄──── SSE text and actions ────            ──►  IDE backend (read and validate files)
```

Every message goes through these steps.

1. **Pending confirmation?** If Hyperion asked the user to confirm a change in its previous reply, the answer is checked in code. Yes runs the change, no cancels it, and anything else cancels it and the message is handled normally.
2. **Router.** One short classification call with JSON schema output sorts the message into `hyperai_question`, `ide_action`, `chit_chat` or `off_topic`. Rules in code run first or override the model. Role change attempts are always off topic, a message that names a file is an action, and "how do I" questions are answered rather than acted on.
3. **Off topic** messages get a fixed reply that says what Hyperion can help with. They are stored in memory as a placeholder, so injected instructions never reach later prompts.
4. **Questions** are answered from the documents. The question is embedded and compared with every chunk, a small bonus is added for rare words both share, and the four best chunks go into the prompt with the instruction to answer only from them. The sources line at the end is added by code from the chunks that were used and is never written by the model.
5. **Actions** go through a planner with JSON schema output that returns steps such as `create_file nginx.yaml`. Rules in code then check the plan. Paths must stay inside the workspace, existing files may only be touched if the user named them or referred to them ("it", "that file", or a clear follow up like "change the cpu to 250m"), paths typed by the user win, and only one step is kept unless the user asked for several.
   * **Create.** A writer adapts the matching template (`templates/native.yaml` or `templates/device.yaml`) to the request and Hyperion sends a `create_file` action. If the file already exists, a new version is prepared and the user is asked to confirm the overwrite.
   * **Edit.** The current file is read from the IDE backend, an editor applies the requested change, and Hyperion sends `edit_file`.
   * **Read and validate.** The real file content or the IDE validator's report, with no model involved.
   * **Delete.** The file is looked up, then the user is asked to confirm.
   * After a create or edit, Hyperion waits until the IDE has saved the file and runs the IDE validator. If there are errors, a fixer corrects them and the corrected file is sent, in at most two rounds.
6. **Memory.** The turn is saved for that `user_id`, and old turns are dropped when the history gets too long for the model's context.

### Why it is built this way

* **Small, strict model calls instead of one large agent loop.** The model is Llama 3.1 8B with an 8k token context. It is reliable at one simple task at a time (classify, plan, write YAML) and much less so at long tool calling loops or at writing whole files inside JSON tool arguments.
* **Adapt valid examples instead of inventing YAML.** The templates are the IDE cookbook's own examples, which pass the IDE validator with zero errors.
* **Code decides what must never go wrong.** Path safety, which files may be touched, native or device profile format, confirmations and citations are all handled in code. The model does the open ended parts.
* **Check the result with the IDE's own validator** rather than trusting the output.

## Project structure

| File | Purpose |
|---|---|
| `main.py` | FastAPI app, `/chat` endpoint, model setup and the flow of each message |
| `router.py` | Message classification and the off topic, role change and how to rules |
| `actions.py` | Planner, writer, editor and fixer prompts, plan checks, file actions, validation loop and confirmations |
| `rag.py` | Retrieval (embeddings plus keyword bonus) and the grounded answer prompt |
| `memory.py` | History, pending confirmations and recently used files for each session |
| `events.py` | Server Sent Events formatting |
| `helpers.py` | `read_file` and `validate_file` against the IDE backend, from the organizers' starter |
| `build_index.py` | Builds `knowledge/index.json` from the documents |
| `templates/` | Native and device app profile templates, from the IDE cookbook |
| `knowledge/` | HYPER-AI documents, IDE documentation and the search index |

To rebuild the index after changing the documents in `knowledge/`, run `uv run build_index.py` with `API_KEY` set.

## Testing and results

During development the agent was tested against the real IDE backend with scripted conversations that apply Hyperion's actions the way the IDE does.

| Test | Result |
|---|---|
| Router, 57 labelled messages (questions, actions, chit chat, off topic, injection attempts, follow ups) | 57/57 |
| Planner, 19 action requests with conversation context and exact paths checked | 19/19 in repeated runs |
| Generated profiles checked with the IDE validator | 15/15 on known requests, 5/6 on new ones before the last rule fix |
| Deliberately broken profile through the fix loop | 3 errors, then 1, then valid after two rounds |
| Retrieval, 22 questions with the document that holds the answer | right document first in 21/22, in the top 4 in 22/22 |
| Answers containing the key facts from the documents | 20/20 |
| End to end scenarios, 37 checks covering identity, off topic, injection, the nginx example, follow up edits, validation, confirmations, folders, path attacks, automatic fixing and RAG | 37/37, also inside Docker |

Typical response times are about 1 to 3 seconds for answers, 2 to 4 seconds for creating or editing a profile including validation, and well under a second for reads, deletes and confirmations.

## Limitations

* The knowledge base contains the provided document excerpts and the IDE documentation, so other HYPER-AI topics get "the documents don't cover it".
* Memory and pending confirmations live in the process and are cleared when the container restarts.
* Plain edits are applied without confirmation because the user asked for that change. Deletes and overwrites always ask.
* Confirmation words and the role change filter are English only.
* The LLM server ignores token limits, so answer length is controlled through the prompts.

## Credits and license

* Built on the organizers' [Hyperion starter](https://gitlab.eclipse.org/eclipse-research-labs/hyper-ai-project/hyperion-starter) (Apache 2.0). `helpers.py`, the Dockerfile base and the SSE protocol come from it.
* `knowledge/ide/` and `templates/` are adapted from the [HyperAI IDE documentation](https://github.com/donMichaelL/ide-hyperai) (Apache 2.0).
* `knowledge/hyperai/` contains excerpts of HYPER-AI project deliverables provided by the organizers for building the RAG index. HYPER-AI is funded by the European Union's Horizon Europe programme (GA 101135982).
* This project is released under the [Apache License 2.0](LICENCE).
