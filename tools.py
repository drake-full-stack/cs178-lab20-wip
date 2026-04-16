"""
tools.py — CS 178 Lab 20: Building an AI Agent

This file contains the tool implementations — the real Python functions
that run when the agent decides to call a tool.

Four tools, at different levels of completion:

  Tool 1 — get_weather()            FULLY IMPLEMENTED — read and understand it
  Tool 2 — save_note() / get_notes() SCAFFOLDED — fill in TODOs (Parts B & C)
  Tool 3 — search_knowledge_base()  SCAFFOLDED — fill in TODOs (Parts D & E)
  Tool 4 — your own function        WRITE FROM SCRATCH (Part G)

Do NOT modify execute_tool() until you're ready to register Tool 4.

To test tools individually before running the full agent:
  python -c "from tools import get_weather; print(get_weather('Des Moines'))"
  python -c "from tools import save_note; print(save_note('test', 'hello'))"
  python -c "from tools import get_notes; print(get_notes())"
  python -c "from tools import search_knowledge_base; print(search_knowledge_base('movies', 'horror'))"
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import boto3


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1: get_weather
# Status: FULLY IMPLEMENTED — read this carefully, no changes needed.
#
# This tool shows the complete pattern every tool follows:
#   1. Accept structured input
#   2. Go get real data from somewhere (API, database, S3, etc.)
#   3. Transform the response into a clean dict
#   4. Return the dict — execute_tool() will JSON-encode it for the agent
# ─────────────────────────────────────────────────────────────────────────────

def get_weather(city: str) -> dict:
    """
    Fetches current weather for a city using the Open-Meteo API.
    Open-Meteo is completely free and requires no API key.

    Returns: {"city": ..., "temperature_f": ..., "condition": ...}
    """
    # Step 1: URL-encode the city name so spaces become %20, etc.
    # Without this, "Des Moines" would produce an invalid URL and crash.
    encoded_city = urllib.parse.quote(city)

    # Step 2: Convert city name to latitude/longitude using the geocoding endpoint
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1"
    with urllib.request.urlopen(geo_url) as response:
        geo_data = json.loads(response.read().decode("utf-8"))

    if not geo_data.get("results"):
        return {"city": city, "error": "City not found"}

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    # Step 3: Fetch current weather for those coordinates
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true&temperature_unit=fahrenheit"
    )
    with urllib.request.urlopen(weather_url) as response:
        weather_data = json.loads(response.read().decode("utf-8"))

    # Step 4: Map the numeric weather code to a human-readable condition string
    weather_codes = {
        0:  "clear sky",
        1:  "mainly clear",
        2:  "partly cloudy",
        3:  "overcast",
        45: "foggy",
        51: "light drizzle",
        61: "light rain",
        71: "light snow",
        80: "rain showers",
        95: "thunderstorm",
    }
    code      = weather_data["current_weather"]["weathercode"]
    condition = weather_codes.get(code, "unknown conditions")

    return {
        "city":          city,
        "temperature_f": weather_data["current_weather"]["temperature"],
        "condition":     condition,
    }


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2: save_note / get_notes
# Status: SCAFFOLDED — fill in the TODOs marked Part B and Part C.
#
# These two functions give the agent persistent memory using DynamoDB.
# The table (CS178AgentNotes) has a single partition key: "topic" (String).
# ─────────────────────────────────────────────────────────────────────────────

def save_note(topic: str, content: str) -> dict:
    """
    Saves a note to DynamoDB so the agent can remember things between sessions.

    Parameters:
        topic   -- short label, e.g. "AWS Lambda"
        content -- note body, e.g. "A serverless compute service"

    Returns: {"status": "saved", "topic": topic}
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table    = dynamodb.Table("CS178AgentNotes")

    # TODO (Part B): Write the item to DynamoDB using table.put_item().
    #
    # put_item() takes one argument: Item — a dict of the data to store.
    # Your dict needs two keys: "topic" and "content".
    #
    # Hint:
    #   table.put_item(Item={"topic": topic, "content": content})
    #
    # If the topic already exists, put_item() overwrites it — that's fine.

    # YOUR CODE HERE

    return {"status": "saved", "topic": topic}


def get_notes(topic: str = "") -> dict:
    """
    Retrieves notes from DynamoDB.
    If topic is given, returns that specific note.
    If topic is empty, returns all notes.

    Returns: {"notes": [ list of {"topic": ..., "content": ...} dicts ]}
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table    = dynamodb.Table("CS178AgentNotes")

    if topic:
        # TODO (Part C): Retrieve a single note by topic (the partition key).
        #
        # Use table.get_item() with a Key dict.
        #
        # Hint:
        #   response = table.get_item(Key={"topic": topic})
        #   item = response.get("Item", None)
        #
        # Return {"notes": [item]} if found, {"notes": []} if not found.

        # YOUR CODE HERE
        pass

    else:
        # Scan returns every item — already implemented, no changes needed.
        response = table.scan()
        return {"notes": response.get("Items", [])}


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 3: search_knowledge_base
# Status: SCAFFOLDED — fill in the TODOs marked Part D and Part E.
#
# This tool reads JSON files from an S3 bucket and searches them for items
# matching the user's query. This is a simplified RAG (Retrieval-Augmented
# Generation) pipeline — the agent retrieves relevant data before answering.
#
# The S3 bucket contains three files:
#   movies.json      — 15 favorite films with ratings, genres, and notes
#   books.json       — read list + to-be-read list with ratings and notes
#   boardgames.json  — game collection + full play log with winners
#
# How the search works:
#   1. Fetch the right JSON file from S3 based on `category`
#   2. Flatten each item into a single searchable string
#   3. Return items where the query keyword appears anywhere in that string
#   4. If query is empty, return everything (useful for "list all my movies")
# ─────────────────────────────────────────────────────────────────────────────

# The name of your S3 bucket — set this to your own bucket name in setup.
# Format: "[your-initials]-knowledge-base"  e.g. "mkm-knowledge-base"
S3_BUCKET_NAME = "YOUR-BUCKET-NAME-HERE"


def _fetch_from_s3(filename: str) -> dict | list:
    """
    Helper: downloads and parses a JSON file from the knowledge base S3 bucket.
    Returns the parsed Python object (dict or list depending on the file).

    This function is complete — do not modify it.
    """
    s3     = boto3.client("s3", region_name="us-east-1")
    obj    = s3.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
    body   = obj["Body"].read().decode("utf-8")
    return json.loads(body)


def _item_matches_query(item: dict, query: str) -> bool:
    """
    Helper: returns True if the query string appears anywhere in the item's values.

    Converts the entire item to a lowercase string and checks for the query.
    This means searching "horror" will match genre fields, notes, titles, etc.

    This function is complete — do not modify it.
    """
    # json.dumps converts the whole dict to a string, including nested lists
    item_text = json.dumps(item).lower()
    return query.lower() in item_text


def search_knowledge_base(category: str, query: str = "") -> dict:
    """
    Searches the personal knowledge base stored in S3.

    Parameters:
        category -- which file to search: "movies", "books", or "boardgames"
        query    -- keyword to search for (case-insensitive); empty = return all

    Returns:
        {"category": category, "query": query, "results": [...matching items...]}
    """
    # Map category names to their filenames in S3
    valid_categories = {
        "movies":     "movies.json",
        "books":      "books.json",
        "boardgames": "boardgames.json",
    }

    # TODO (Part D): Validate the category.
    #
    # If category is not in valid_categories, return an error dict:
    #   {"error": f"Unknown category '{category}'. Choose from: movies, books, boardgames"}
    #
    # Hint: check  if category not in valid_categories

    # YOUR CODE HERE

    # TODO (Part E): Fetch the data, filter it, and return the results.
    #
    # Step 1 — get the filename and fetch the data from S3:
    #   filename = valid_categories[category]
    #   data = _fetch_from_s3(filename)
    #
    # Step 2 — books.json has a different structure than the others.
    #   movies.json    → a list of items directly
    #   boardgames.json → a dict with keys "collection" and "play_log"
    #   books.json     → a dict with keys "read" and "to_be_read"
    #
    #   To keep things simple, flatten books and boardgames into a single list:
    #     movies:     items = data
    #     boardgames: items = data["collection"] + data["play_log"]
    #     books:      items = data["read"] + data["to_be_read"]
    #
    # Step 3 — filter with _item_matches_query():
    #   If query is non-empty:
    #     results = [item for item in items if _item_matches_query(item, query)]
    #   If query is empty:
    #     results = items   (return everything)
    #
    # Step 4 — return the results dict:
    #   return {"category": category, "query": query, "results": results}

    # YOUR CODE HERE
    pass


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 4: your own tool
# Status: WRITE FROM SCRATCH (Part G)
#
# Ideas:
#
#   Option A — calculate(expression: str) -> dict
#     Evaluate a math expression string.
#     Hint: result = eval(expression)
#     Return: {"expression": expression, "result": result}
#
#   Option B — get_stock_price(ticker: str) -> dict
#     Fetch a stock price from Yahoo Finance (free, no key):
#     URL: https://query1.finance.yahoo.com/v8/finance/chart/{ticker}
#     Return: {"ticker": ticker, "price": price}
#
#   Option C — query_my_database(sql: str) -> dict
#     Run a query against your Project 1 RDS database using the
#     execute_query() helper from dbCode.py.
#     Return: {"results": execute_query(sql)}
#
# After writing your function:
#   1. Add an elif branch for it in execute_tool() below
#   2. Add its schema to TOOL_SCHEMAS in tool_schemas.py
# ─────────────────────────────────────────────────────────────────────────────

# YOUR TOOL 4 FUNCTION HERE


# ─────────────────────────────────────────────────────────────────────────────
# Tool dispatcher — called by the agent loop in agent.py
# DO NOT modify existing branches. Add Tool 4 at the bottom.
# ─────────────────────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Routes a tool call from the agent loop to the correct Python function.
    Returns a JSON string — the agent loop feeds this back to the model.
    """
    if tool_name == "get_weather":
        result = get_weather(tool_input["city"])
        return json.dumps(result)

    elif tool_name == "save_note":
        result = save_note(tool_input["topic"], tool_input["content"])
        return json.dumps(result)

    elif tool_name == "get_notes":
        result = get_notes(tool_input.get("topic", ""))
        return json.dumps(result)

    elif tool_name == "search_knowledge_base":
        result = search_knowledge_base(
            tool_input["category"],
            tool_input.get("query", "")   # query is optional
        )
        return json.dumps(result)

    # TODO (Part H): Add an elif branch for your Tool 4 here.

    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})