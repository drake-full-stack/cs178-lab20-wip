"""
agent.py — CS 178 Lab 20: Building an AI Agent

This file contains the agent loop. It is fully implemented — read it carefully
before touching anything else. Your only task in this file is Part A:
writing the SYSTEM_PROMPT at the top.

The agent loop works like this:
  1. Send the conversation history to the model
  2. If the model wants to call a tool → execute it, add the result, go to 1
  3. If the model is done → return the final text response
"""

import json
import anthropic
from tools import execute_tool
from tool_schemas import TOOL_SCHEMAS

# ── Agent configuration ───────────────────────────────────────────────────────

# TODO (Part A): Write a system prompt that tells the agent what it is and
# what tools it has access to. Keep it to 3–5 sentences.
#
# A good system prompt answers:
#   - What is this agent? (a research assistant, a helpful bot, etc.)
#   - What tools does it have? (mention them by name)
#   - When should it use tools vs. answer from its own knowledge?
#
# Example structure (replace this entirely with your own):
#   "You are a helpful research assistant. You have access to two tools:
#    get_weather (for current weather) and get_fun_fact (for interesting facts).
#    Use tools when the question requires real-time or specific factual data.
#    For general knowledge questions, answer directly without using tools."

SYSTEM_PROMPT = """
YOUR SYSTEM PROMPT HERE
"""

# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(user_question: str) -> str:
    """
    Runs the agent loop for a single user question and returns the final answer.

    Parameters:
        user_question (str): The question typed by the user.

    Returns:
        str: The agent's final text response after any tool calls are complete.
    """
    # The Anthropic client reads your API key from the ANTHROPIC_API_KEY
    # environment variable automatically — no need to pass it here.
    client = anthropic.Anthropic()

    # Message history grows with each iteration of the loop.
    # This is how the agent "sees" what has already happened:
    # the original question, any tool calls it made, and their results.
    messages = [
        {"role": "user", "content": user_question}
    ]

    print(f"\n[Agent] Question: {user_question}")
    print(f"[Agent] Starting loop...\n")

    # ── The loop ──────────────────────────────────────────────────────────────
    while True:

        # STEP 1 — Send the full conversation to the model.
        # `tools=TOOL_SCHEMAS` tells the model what tools are available.
        # The model reads the schema descriptions to decide which (if any) to call.
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        print(f"[Agent] Stop reason: {response.stop_reason}")

        # STEP 2 — The model wants to call one or more tools.
        if response.stop_reason == "tool_use":

            # Add the model's response (including its tool request) to history.
            # The model needs to see its own previous messages on the next iteration.
            messages.append({"role": "assistant", "content": response.content})

            # The model may request multiple tool calls in one turn.
            # We process all of them before looping back.
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name  = block.name   # e.g. "get_weather"
                    tool_input = block.input  # e.g. {"city": "Chicago"}

                    print(f"[Agent] → Calling tool : {tool_name}")
                    print(f"[Agent]   Input        : {json.dumps(tool_input, indent=2)}")

                    # Dispatch to the real Python function in tools.py
                    result = execute_tool(tool_name, tool_input)

                    print(f"[Agent]   Result       : {result}\n")

                    # Package the result so the API knows which tool call it answers
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,   # must match the request id
                        "content":     str(result)
                    })

            # Add all tool results to history, then loop back to Step 1.
            # The model will now compose its answer using these results.
            messages.append({"role": "user", "content": tool_results})

        # STEP 3 — The model is done. Extract and return the text response.
        elif response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            print(f"[Agent] Loop complete.\n")
            return final_text

        else:
            # Shouldn't happen under normal conditions — surface it for debugging
            return f"[Unexpected stop reason: {response.stop_reason}]"


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  CS 178 AI Research Assistant")
    print("  Type 'quit' to exit")
    print("=" * 60)

    while True:
        try:
            question = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        answer = run_agent(question)
        print(f"\nAssistant: {answer}")