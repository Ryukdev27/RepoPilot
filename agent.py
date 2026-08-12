import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import run_project_tests
from tools import (
    get_issue,
    get_file,
    create_branch,
    update_file,
    run_project_tests,
    create_pull_request,
    list_files,
)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------------------------------------------------
# Tool declarations
# ---------------------------------------------------------

TOOLS = [
    {
        "name": "get_issue",
        "description": "Get details of a GitHub issue.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "owner": {
                    "type": "STRING",
                    "description": "GitHub repository owner"
                },
                "repo": {
                    "type": "STRING",
                    "description": "GitHub repository name"
                },
                "issue_number": {
                    "type": "INTEGER",
                    "description": "GitHub issue number"
                },
            },
            "required": ["owner", "repo", "issue_number"],
        },
    },
    {
        "name": "get_file",
        "description": "Read the contents of a file from a GitHub repository.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "owner": {
                    "type": "STRING"
                },
                "repo": {
                    "type": "STRING"
                },
                "path": {
                    "type": "STRING",
                    "description": "Path of the file in the repository"
                },
            },
            "required": ["owner", "repo", "path"],
        },
    },
    {
        "name": "create_branch",
        "description": "Create a new GitHub branch from the default branch.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "owner": {
                    "type": "STRING"
                },
                "repo": {
                    "type": "STRING"
                },
                "branch_name": {
                    "type": "STRING"
                },
            },
            "required": ["owner", "repo", "branch_name"],
        },
    },
    {
        "name": "update_file",
        "description": "Update an existing file in a GitHub branch.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "owner": {
                    "type": "STRING"
                },
                "repo": {
                    "type": "STRING"
                },
                "path": {
                    "type": "STRING"
                },
                "content": {
                    "type": "STRING",
                    "description": "Complete new file contents"
                },
                "message": {
                    "type": "STRING"
                },
                "branch": {
                    "type": "STRING"
                },
            },
            "required": [
                "owner",
                "repo",
                "path",
                "content",
                "message",
                "branch",
            ],
        },
    },
    {
    "name": "run_project_tests",
    "description": "Run the project's pytest test suite and return the results.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    },
    },
    {
    "name": "list_files",
    "description": "List files and directories in a GitHub repository.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "owner": {
                "type": "STRING"
            },
            "repo": {
                "type": "STRING"
            },
            "path": {
                "type": "STRING",
                "description": "Directory path. Empty string means repository root."
            },
        },
        "required": ["owner", "repo"],
    },
    },
    {
        "name": "create_pull_request",
        "description": "Create a pull request on GitHub.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "owner": {
                    "type": "STRING"
                },
                "repo": {
                    "type": "STRING"
                },
                "title": {
                    "type": "STRING"
                },
                "body": {
                    "type": "STRING"
                },
                "head": {
                    "type": "STRING"
                },
                "base": {
                    "type": "STRING"
                },
            },
            "required": [
                "owner",
                "repo",
                "title",
                "body",
                "head",
                "base",
            ],
        },
    },
]


# ---------------------------------------------------------
# Tool executor
# ---------------------------------------------------------

def execute_tool(name, args):

    if name == "get_issue":
        return get_issue(**args)

    if name == "get_file":
        return get_file(**args)

    if name == "create_branch":
        return create_branch(**args)

    if name == "update_file":
        return update_file(**args)

    if name == "create_pull_request":
        return create_pull_request(**args)

    if name == "run_project_tests":
        return run_project_tests()

    if name == "list_files":
        return list_files(**args)

    return {
        "error": f"Unknown tool: {name}"
    }


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------

def run_agent(owner: str, repo: str, task: str):

    system_prompt = f"""
You are an autonomous AI software engineering agent.

Repository:
{owner}/{repo}

User request:
{task}

Your workflow:

1. Understand the user's request.
2. If an issue number is provided, retrieve the issue.
3. Inspect relevant source files using get_file.
4. Determine the smallest reasonable code change.
5. Create a feature branch.
6. Update the required file.
7. Run the project's pytest test suite.
8. If tests pass, create a pull request.
9. If tests fail, explain the failure and do not create the PR.
10. Never merge a pull request.
11. Never delete files, branches, repositories, or issues.
12. Never modify a file without first reading it.
13. Never invent repository information.

When modifying code, provide the COMPLETE updated file content
to update_file.

At the end, summarize:
- files changed
- tests executed
- test result
- pull request URL, if created
"""

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=system_prompt
                )
            ],
        )
    ]

    config = types.GenerateContentConfig(
        tools=[
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(**tool)
                    for tool in TOOLS
                ]
            )
        ]
    )

    logs = []

    for step in range(10):

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        parts = candidate.content.parts

        function_calls = [
            part.function_call
            for part in parts
            if part.function_call
        ]

        # Gemini finished without requesting another tool.
        if not function_calls:

            final_text = "".join(
                part.text
                for part in parts
                if part.text
            )

            return {
                "status": "success",
                "message": final_text,
                "logs": logs,
            }

        # Add Gemini response to conversation.
        contents.append(candidate.content)

        # Execute requested tools.
        tool_parts = []

        for function_call in function_calls:

            name = function_call.name
            args = dict(function_call.args)

            logs.append(
                f"🔧 {name}({json.dumps(args)})"
            )

            try:
                result = execute_tool(
                    name,
                    args,
                )

            except Exception as e:
                result = {
                    "error": str(e)
                }

            tool_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response=result,
                )
            )

            logs.append(
                f"✓ {name} completed"
            )

        contents.append(
            types.Content(
                role="tool",
                parts=tool_parts,
            )
        )

    return {
        "status": "failed",
        "message": "Agent reached maximum tool steps.",
        "logs": logs,
    }