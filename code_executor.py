import os
import shutil
import subprocess
import tempfile
import sys

from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

def clone_repository(owner: str, repo: str):
    """
    Clone a GitHub repository into a temporary workspace
    using a GitHub personal access token.
    """

    import base64

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not configured."
        )

    print("DEBUG: GitHub token loaded:", True)

    workspace = tempfile.mkdtemp(
        prefix="github-agent-"
    )

    url = f"https://github.com/{owner}/{repo}.git"

    # GitHub HTTPS authentication:
    # username can be your GitHub username;
    # token is used as the password.
    github_username = os.getenv("GITHUB_USERNAME")

    if not github_username:
        raise RuntimeError(
        "GITHUB_USERNAME is not configured."
       )

    credentials = f"{github_username}:{token}"

    encoded_credentials = base64.b64encode(
        credentials.encode("utf-8")
    ).decode("ascii")

    env = os.environ.copy()

    # Never allow Git to open a browser or ask
    # for credentials during autonomous execution.
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "Never"

    try:

        result = subprocess.run(
            [
                "git",

                # Disable credential helpers for this operation.
                "-c",
                "credential.helper=",

                # Send Basic authentication.
                "-c",
                f"http.extraheader=Authorization: Basic {encoded_credentials}",

                "clone",
                url,
                workspace,
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )

    except subprocess.TimeoutExpired:

        shutil.rmtree(
            workspace,
            ignore_errors=True,
        )

        raise RuntimeError(
            "Repository clone timed out after 120 seconds."
        )

    if result.returncode != 0:

        shutil.rmtree(
            workspace,
            ignore_errors=True,
        )

        raise RuntimeError(
            "Repository clone failed:\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"Return code: {result.returncode}"
        )

    return workspace


def run_tests(workspace: str):
    """
    Run pytest inside the cloned repository.

    Uses the same Python interpreter that is
    running the AI engineering agent.
    """

    try:

        env = os.environ.copy()

        # Make the cloned repository importable.
        existing_pythonpath = env.get(
            "PYTHONPATH",
            "",
        )

        if existing_pythonpath:

            env["PYTHONPATH"] = (
                workspace
                + os.pathsep
                + existing_pythonpath
            )

        else:

            env["PYTHONPATH"] = workspace

        # Use the current Python interpreter.
        python_executable = sys.executable

        result = subprocess.run(
            [
                python_executable,
                "-m",
                "pytest",
                "-q",
            ],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout[-5000:],
            "stderr": result.stderr[-5000:],
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": (
                "Tests timed out after 60 seconds."
            ),
        }


def cleanup_workspace(workspace: str):
    """
    Remove the temporary repository workspace.
    """

    shutil.rmtree(
        workspace,
        ignore_errors=True,
    )