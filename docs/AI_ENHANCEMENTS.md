# AI enhancement hooks

Dragon Studio exposes optional AI enrichment without requiring a key to use the core chart engine.

## Endpoints

- `POST /api/ai/reading` — body `{ "chart": <chart JSON>, "question": "..."? }`
  - If `OPENAI_API_KEY` or `PERPLEXITY_API_KEY` is set in the environment, the server calls that provider.
  - Otherwise returns a templated / heuristic rewrite grounded on Sun, Moon, Ascendant, and elemental balance.

## Ideas (roadmap)

1. **Natal reading** — poetic overview from placements + house cusps; tone: celestial Chinese-dragon (vivid, respectful, concise).
2. **Q&A grounded on chart** — answer user questions using only returned placements/aspects (no invented orbs); cite planet/sign/house.
3. **Smart parse** — free-text birth blurbs (“born around dusk in Brooklyn, June 1990”) → structured `{date,time,place,timezone}` for `/api/chart`.
4. **Privacy** — never log raw birth data by default; strip PII from model prompts except chart vectors; local-only heuristic mode for Paranoid users.
5. **Aspect storytelling** — narrate tight aspects and stelliums detected by `ChartInterpreter`.
6. **Transit briefings** — optional daily/weekly overlay when ephemeris backends are present.

## Env vars

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Live OpenAI chat completions |
| `PERPLEXITY_API_KEY` | Live Perplexity (`sonar`) completions |

Keys are optional. Chart compute never depends on them.
