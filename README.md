## Setup

1. Install the required Python packages by running `uv sync`.

2. Make a copy of `.env.example` and name the copy `.env`.

3. Fill in `.env` with your values for `GEMINI_API_KEY`, `GROQ_API_KEY`, `GEMINI_MODEL`, and `GROQ_MODEL`.

4. The `.env` file holds your secret API keys, so keep it private and never push it to GitHub.

## Run

From the root folder of the repository, run the tracker and put your prompt inside quotation marks.

`uv run tracker.py "What is machine learning, answer briefly"`

## Sample Output

The replies from each provider are printed first, and a comparison table follows them.

| Provider | Input Tokens | Output Tokens | Seconds |     Cost USD |
| -------- | -----------: | ------------: | ------: | -----------: |
| gemini   |            9 |            53 |   6.842 | 0.0000812000 |
| groq     |           82 |           172 |   0.931 | 0.0000575500 |

Replies, token counts, response times, and costs can vary from one run to another.

## What I Learned

I learned how a Python program can use APIs to talk to different LLM providers. I also learned how to keep API keys safe, read the actual token usage, time each response, and estimate the cost of every model call. This assignment showed me that for the same prompt, providers can differ in how many tokens they use, how fast they respond, and how much they cost.
# Two-provider-Cost-Tracker
# Two-provider-Cost-Tracker