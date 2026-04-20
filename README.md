# CS 178 — Lab 20: Building an AI Agent

Starter repository for Lab 20. You'll build a working AI agent that can answer natural language questions by deciding which tools to call, executing them, and incorporating the results into its response.

## What's in this repo

```!
cs178-lab20-starter/
├── agent.py               <- the agent loop (read this first)
├── tools.py               <- tool implementations (your main task)
├── tool_schemas.py        <- describes tools to the model
├── knowledge_base/
│   ├── movies.json        <- 15 films with ratings, genres, and personal notes
│   ├── books.json         <- read list and to-be-read list
│   └── boardgames.json    <- game collection and play log with winners
└── README.md
```

## Setup

### 1. Get a free Anthropic API key

Go to [https://console.anthropic.com](https://console.anthropic.com) and create an account.
No credit card required. Once logged in: **API Keys → Create Key** → name it `cs178-lab20`.

### 2. Set your API key as an environment variable

**Mac / Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

> Do not paste your key into any Python file. Do not commit it to GitHub.
> The `anthropic` library reads it from the environment automatically.

### 3. Install the Anthropic SDK

```bash
pip install anthropic
```

Verify:
```bash
python -c "import anthropic; print('SDK ready')"
```

## Your tasks (in order)

| Task | File | What to do |
|------|------|------------|
| Part A | `agent.py` | Write the `SYSTEM_PROMPT` |
| Part B | `tools.py` | Implement `get_weather()` |
| Part C | `tools.py` | Implement `get_fun_fact()` |
| Part D | `tool_schemas.py` | Write all four `description` fields |

**Read `agent.py` completely before writing any code.** The loop is already implemented — understanding it is Exercise 1.

## Testing your tools individually

Before running the full agent, test each tool function on its own:

```bash
# Test get_weather
python -c "from tools import get_weather; print(get_weather('Des Moines'))"

# Expected output (values will vary with actual weather):
# {"city": "Des Moines", "temperature_f": 58.2, "condition": "partly cloudy"}

# Test get_fun_fact
python -c "from tools import get_fun_fact; print(get_fun_fact('AWS Lambda'))"

# Expected output:
# {"topic": "AWS Lambda", "fact": "AWS Lambda is an event-driven, serverless..."}
```

## Running the agent

Once all four tasks are complete:

```bash
python agent.py
```

Test with these questions to see different loop behaviors:

| Question | Expected behavior |
|----------|-------------------|
| `What's the weather like in Chicago?` | calls `get_weather` |
| `Tell me something interesting about the Amazon rainforest.` | calls `get_fun_fact` |
| `What's 2 + 2?` | answers directly — no tool call |
| `What's the weather in Seattle, and give me a fun fact about rain.` | calls both tools |

Watch the `[Agent]` lines in your terminal to see the loop running in real time.

## APIs used (both free, no key required)

- **Open-Meteo** — weather data: https://open-meteo.com/en/docs
- **Wikipedia REST API** — article summaries: https://en.wikipedia.org/api/rest_v1/

## Common issues

**`ANTHROPIC_API_KEY` not set error**
You need to re-export the key in your current terminal session. If you close and reopen VS Code, run the `export` command again.

**City not found / no results**
Check your URL encoding. City names with spaces (like "Des Moines") must be encoded before putting them in a URL. Use `urllib.parse.quote(city)`.

**Wikipedia returns 404**
The topic might not have a Wikipedia article, or the title might need adjustment. Your function should handle 404 gracefully and return a "No information found" message — see the docstring hint.

**Model never calls a tool**
Check your `tool_schemas.py` descriptions. If they're vague or say "TODO", the model doesn't know when to use the tools. Write clear, specific descriptions.

**Model calls the wrong tool**
Same fix — sharpen your descriptions to distinguish the two tools clearly.