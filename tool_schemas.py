"""
tool_schemas.py — CS 178 Lab 20: Building an AI Agent

Describes all available tools to the model. The model reads these schemas
to decide which tool to call and what arguments to pass.

YOUR TASKS:
  Part D2 -- fill in save_note descriptions
  Part E2 -- fill in get_notes descriptions
  Part F  -- fill in search_knowledge_base descriptions
  Part G2 -- add your Tool 4 schema at the bottom

Tools 1 (get_weather) is fully written — use it as a style reference.
"""

TOOL_SCHEMAS = [

    # ── Tool 1: get_weather ───────────────────────────────────────────────────
    # FULLY WRITTEN — read as a reference for what a good schema looks like.
    # Notice: the description says what it does, when to use it, and what it
    # does NOT do. All three are important.
    {
        "name": "get_weather",
        "description": (
            "Get the current weather conditions and temperature for a city. "
            "Use this when the user asks about weather, temperature, or conditions "
            "in a specific location. Does not provide forecasts or historical data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city, e.g. 'Des Moines' or 'Tokyo'."
                }
            },
            "required": ["city"]
        }
    },

    # ── Tool 2a: save_note ────────────────────────────────────────────────────
    # TODO (Part D2): Fill in the three description fields.
    # Think about: when should the agent proactively save something?
    # What makes a good topic label vs. what belongs in content?
    {
        "name": "save_note",
        "description": "TODO: your description here",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "TODO: your description here"
                },
                "content": {
                    "type": "string",
                    "description": "TODO: your description here"
                }
            },
            "required": ["topic", "content"]
        }
    },

    # ── Tool 2b: get_notes ────────────────────────────────────────────────────
    # TODO (Part E2): Fill in the two description fields.
    # Key detail: topic is optional — omitting it returns ALL saved notes.
    # Your description should make this clear so the model uses it correctly.
    {
        "name": "get_notes",
        "description": "TODO: your description here",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "TODO: your description here"
                }
            },
            "required": []   # topic is optional — do not add it to required
        }
    },

    # ── Tool 3: search_knowledge_base ─────────────────────────────────────────
    # TODO (Part F): Fill in the three description fields.
    #
    # This is the most interesting schema to write because:
    #   - category must be one of exactly three values — say so explicitly
    #   - query is optional (empty = return everything) — explain when to omit it
    #   - the description should convey WHAT is in the knowledge base
    #     (movies, books, boardgames) so the model knows what to search
    #
    # Think about what questions a user might ask that should trigger this tool:
    #   "What horror movies have I watched?"
    #   "Which books are on my to-read list?"
    #   "Who has won the most board games?"
    {
        "name": "search_knowledge_base",
        "description": "TODO: your description here",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "TODO: your description here — must name the three valid values"
                },
                "query": {
                    "type": "string",
                    "description": "TODO: your description here — explain that empty returns all items"
                }
            },
            "required": ["category"]   # query is optional
        }
    },

    # ── Tool 4: your own tool ─────────────────────────────────────────────────
    # TODO (Part G2): Add your Tool 4 schema here.
    #
    # Copy this skeleton and fill it in:
    #
    # {
    #     "name": "your_function_name",   # must match execute_tool() exactly
    #     "description": "...",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "param_name": {
    #                 "type": "string",
    #                 "description": "..."
    #             }
    #         },
    #         "required": ["param_name"]
    #     }
    # },

]