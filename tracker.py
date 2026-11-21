import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from groq import Groq


# Paid pricing for Gemini 3.1 Flash Lite (USD for every 1M tokens).
# See: https://aistudio.google.com/docs/pricing#gemini-3.1-flash-lite
GEMINI_RATE_IN = 0.25
GEMINI_RATE_OUT = 1.50

# Paid pricing for Groq GPT OSS 20B (USD for every 1M tokens).
# See: https://console.groq.com/docs/model/openai/gpt-oss-20b
GROQ_RATE_IN = 0.075
GROQ_RATE_OUT = 0.30


def estimate_price(
    tokens_in,
    tokens_out,
    rate_in,
    rate_out,
):
    price_in = tokens_in * rate_in / 1_000_000
    price_out = tokens_out * rate_out / 1_000_000

    return price_in + price_out


def ask_gemini(question, secret, model_id):
    gemini_client = genai.Client(api_key=secret)

    begin = time.perf_counter()

    result = gemini_client.models.generate_content(
        model=model_id,
        contents=question,
    )

    lapse = time.perf_counter() - begin

    answer = result.text
    tokens_in = result.usage_metadata.prompt_token_count
    tokens_out = result.usage_metadata.candidates_token_count

    return answer, tokens_in, tokens_out, lapse


def ask_groq(question, secret, model_id):
    groq_client = Groq(api_key=secret)

    chat = [
        {
            "role": "user",
            "content": question,
        }
    ]

    begin = time.perf_counter()

    result = groq_client.chat.completions.create(
        model=model_id,
        messages=chat,
    )

    lapse = time.perf_counter() - begin

    answer = result.choices[0].message.content
    tokens_in = result.usage.prompt_tokens
    tokens_out = result.usage.completion_tokens

    return answer, tokens_in, tokens_out, lapse


load_dotenv()

gemini_secret = os.getenv("GEMINI_API_KEY")
groq_secret = os.getenv("GROQ_API_KEY")
gemini_model_id = os.getenv("GEMINI_MODEL")
groq_model_id = os.getenv("GROQ_MODEL")


if not gemini_secret:
    print("The Gemini API key was not found.")
    sys.exit(1)

if not groq_secret:
    print("The Groq API key was not found.")
    sys.exit(1)

if not gemini_model_id:
    print("The Gemini model name was not found.")
    sys.exit(1)

if not groq_model_id:
    print("The Groq model name was not found.")
    sys.exit(1)


if len(sys.argv) < 2:
    print('Usage: uv run tracker.py "your prompt"')
    sys.exit(1)

question = " ".join(sys.argv[1:]).strip()

if not question:
    print("The prompt must not be empty.")
    sys.exit(1)


gemini_answer, gemini_in, gemini_out, gemini_lapse = (
    ask_gemini(
        question,
        gemini_secret,
        gemini_model_id,
    )
)

groq_answer, groq_in, groq_out, groq_lapse = ask_groq(
    question,
    groq_secret,
    groq_model_id,
)


gemini_price = estimate_price(
    gemini_in,
    gemini_out,
    GEMINI_RATE_IN,
    GEMINI_RATE_OUT,
)

groq_price = estimate_price(
    groq_in,
    groq_out,
    GROQ_RATE_IN,
    GROQ_RATE_OUT,
)


comparison = [
    {
        "provider": "gemini",
        "model": gemini_model_id,
        "reply": gemini_answer,
        "input_tokens": gemini_in,
        "output_tokens": gemini_out,
        "input_price_per_m": GEMINI_RATE_IN,
        "output_price_per_m": GEMINI_RATE_OUT,
        "cost_usd": gemini_price,
    },
    {
        "provider": "groq",
        "model": groq_model_id,
        "reply": groq_answer,
        "input_tokens": groq_in,
        "output_tokens": groq_out,
        "input_price_per_m": GROQ_RATE_IN,
        "output_price_per_m": GROQ_RATE_OUT,
        "cost_usd": groq_price,
    },
]


with open("results.json", "w", encoding="utf-8") as results_file:
    json.dump(comparison, results_file, indent=2, ensure_ascii=False)


print("\nGEMINI REPLY\n")
print(gemini_answer)

print("\nGROQ REPLY\n")
print(groq_answer)


print()
print(
    f"{'Provider':<10}"
    f"{'Input Tokens':>15}"
    f"{'Output Tokens':>16}"
    f"{'Seconds':>12}"
    f"{'Cost USD':>16}"
)

print("-" * 69)

print(
    f"{'gemini':<10}"
    f"{gemini_in:>15}"
    f"{gemini_out:>16}"
    f"{gemini_lapse:>12.3f}"
    f"{gemini_price:>16.10f}"
)

print(
    f"{'groq':<10}"
    f"{groq_in:>15}"
    f"{groq_out:>16}"
    f"{groq_lapse:>12.3f}"
    f"{groq_price:>16.10f}"
)

print("Saved results to results.json")