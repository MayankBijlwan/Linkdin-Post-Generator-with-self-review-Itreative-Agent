# LinkedIn Post Generator — Iterative Workflow Agent with RAG

An autonomous content-generation agent that **writes, retrieves, reviews, and rewrites** LinkedIn posts in a closed loop until the output is publish-ready — built with [LangGraph](https://langchain-ai.github.io/langgraph/), [LangChain](https://www.langchain.com/), and a **Retrieval-Augmented Generation (RAG)** step powered by Tavily web search.

## What it does

Give the agent a topic, and it runs a multi-agent workflow:

1. **Writer agent** (Gemini) drafts a LinkedIn post on the topic.
2. **Retrieval step (RAG)** — if the topic needs current facts, statistics, or trends, the writer calls a live web search tool (Tavily) to ground the draft in up-to-date information before writing.
3. **Reviewer agent** (Llama 3.3 via Groq) critiques the draft against a strict rubric (hook, takeaway, skimmability, length, CTA, tone, no hashtags) and returns an APPROVED/REJECTED verdict with feedback.
4. **Iteration loop** — if rejected, the feedback is fed back to the writer, which produces a new draft addressing every point. This repeats until the post is approved or a maximum of 3 attempts is reached.

The result is a self-correcting content pipeline: the agent doesn't just generate once, it **critiques its own work and improves it**, using retrieved information rather than relying solely on the model's internal knowledge.

## Why "RAG"?

Instead of writing purely from the model's training data, the writer agent is equipped with a search tool. When a topic needs current or factual grounding, the model autonomously decides to retrieve fresh context from the web and incorporates it into generation — the core retrieval-then-generate pattern of RAG, applied here with live search instead of a static vector store.

## Architecture

```
START
  │
  ▼
writer ──(needs info?)──► tools (Tavily search) ──► reviewer
  │
  └──(no search needed)──► extract_draft ──► reviewer
                                                  │
                                     ┌────────────┴────────────┐
                                     ▼                          ▼
                                 APPROVED                   REJECTED
                                     │                          │
                                    END                 (attempt < 3?)
                                                                 │
                                                        ┌────────┴────────┐
                                                        ▼                 ▼
                                                     writer               END
                                                  (retry with          (max
                                                    feedback)         attempts)
```

The workflow is implemented as a `StateGraph` with conditional edges — the graph dynamically routes between the writer, the retrieval tool, and the reviewer based on model output and review verdicts.

## Project structure

| File | Purpose |
|---|---|
| `pipeline.py` | Core agent logic: state schema, writer/reviewer/tool nodes, routing functions, and the compiled LangGraph `app`. Exposes `run_pipeline(topic)`. |
| `main.py` | CLI interface — prompts the user for a topic, runs the pipeline, and prints the final approved post. |

## State

The graph tracks a single shared state across all nodes:

| Field | Type | Description |
|---|---|---|
| `topic` | `str` | The subject of the post |
| `messages` | `list` | Full conversation/tool-call history (writer ↔ tools) |
| `draft` | `str` | Current draft text |
| `review_feedback` | `str` | Latest reviewer feedback |
| `is_approved` | `bool` | Whether the current draft passed review |
| `attempt` | `int` | Number of writing attempts so far (capped at 3) |

## Models & tools

- **Writer:** `gemini-3.6-flash` (via `langchain_google_genai`), temperature `0.7` — creative, tool-calling enabled
- **Reviewer:** `llama-3.3-70b-versatile` (via `langchain_groq`), temperature `0.2` — strict, deterministic judging
- **Retrieval:** `TavilySearch` (via `langchain_tavily`) — live web search, max 3 results per query

## Setup

1. Install dependencies:
   ```bash
   pip install langgraph langchain-groq langchain-google-genai langchain-tavily python-dotenv
   ```
2. Create a `.env` file in the project root with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

## Usage

```bash
python main.py
```

You'll be prompted for a topic:

```
What topic do you want a LinkedIn post about?
> The future of AI agents in enterprise software
```

The agent will search, write, review, and iterate automatically, printing progress (verdicts and feedback) as it goes, then output the final approved post along with the number of attempts taken.

## Using the pipeline programmatically

```python
from pipeline import run_pipeline

result = run_pipeline("Remote work productivity tips")

print(result["draft"])
print(result["is_approved"])
print(result["attempt"])
```

## Notes & limitations

- If a topic is rejected 3 times, the loop stops and returns the last draft even if unapproved — check `is_approved` before publishing.
- Retrieval is triggered at the model's discretion (tool-calling), not forced on every run — factual/current-events topics are more likely to trigger a search than evergreen/opinion topics.
- No hashtags are used by design, per the writer's system prompt.
"# Linkdin-Post-Generator-with-self-review-Itreative-Agent" 
