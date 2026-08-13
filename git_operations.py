import os
import subprocess
from click import command
from click import command
import subprocess


def run_git(
    workspace: str,
    *args,
):
    result = subprocess.run(
        ["git", *args],
        cwd=workspace,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed:\n"
            f"Command: git {' '.join(args)}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"Return code: {result.returncode}"
        )

    return result.stdout.strip()

def create_branch(
    workspace: str,
    branch: str,
):
    return run_git(
        workspace,
        "checkout",
        "-b",
        branch,
    )


def commit_changes(
    workspace: str,
    message: str,
):
    run_git(
        workspace,
        "add",
        ".",
    )

    run_git(
        workspace,
        "config",
        "user.name",
        "GitHub AI Engineer",
    )

    run_git(
        workspace,
        "config",
        "user.email",
        "ai-agent@example.com",
    )

    # Check whether anything actually changed
    status = run_git(
        workspace,
        "status",
        "--porcelain",
    )

    if not status:
        return {
            "committed": False,
            "message": "No changes to commit",
        }

    output = run_git(
        workspace,
        "commit",
        "-m",
        message,
    )

    return {
        "committed": True,
        "message": output,
    }


def push_branch(
    workspace: str,
    branch: str,
):
    token = os.getenv("GITHUB_TOKEN")

    remote_url = run_git(
        workspace,
        "remote",
        "get-url",
        "origin",
    )

    if token and remote_url.startswith(
        "https://github.com/"
    ):
        result = subprocess.run(
            [
                "git",
                "-c",
                f"http.extraheader=Authorization: Bearer {token}",
                "push",
                "-u",
                "origin",
                branch,
            ],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Git push failed:\n{result.stderr}"
            )

        return result.stdout.strip()

    return run_git(
        workspace,
        "push",
        "-u",
        "origin",
        branch,
    )