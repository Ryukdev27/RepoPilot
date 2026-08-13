import os
from pathlib import Path

from code_executor import clone_repository


def create_workspace(owner: str, repo: str):
    return clone_repository(owner, repo)


def read_file(workspace, path):
    file_path = Path(workspace) / path

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding="utf-16")
        except UnicodeDecodeError:
            return file_path.read_text(encoding="latin-1")


def write_file(
    workspace: str,
    path: str,
    content: str,
    ):
    workspace_path = Path(workspace).resolve()
    file_path = (workspace_path / path).resolve()

    if workspace_path not in file_path.parents:
        raise ValueError(
            f"Cannot write outside workspace: {path}"
        )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return str(file_path)


def list_workspace_files(
    workspace: str,
    limit: int = 100,
):
    ignored = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
    }

    files = []

    for root, directories, filenames in os.walk(workspace):

        directories[:] = [
            d for d in directories
            if d not in ignored
        ]

        for filename in filenames:

            relative = os.path.relpath(
                os.path.join(root, filename),
                workspace,
            )

            files.append(relative)

            if len(files) >= limit:
                return files

    return files