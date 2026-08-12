from github_client import GitHubClient
from code_executor import run_tests

github = GitHubClient()


def get_issue(owner: str, repo: str, issue_number: int):
    """Get details of a GitHub issue."""
    return github.get_issue(owner, repo, issue_number)


def get_file(owner: str, repo: str, path: str):
    """Read a file from a GitHub repository."""
    return github.get_file(owner, repo, path)


def create_branch(owner: str, repo: str, branch_name: str):
    """Create a new branch from the default branch."""
    return github.create_branch(owner, repo, branch_name)


def update_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
):
    """Update a file in a GitHub branch."""
    return github.update_file(
        owner,
        repo,
        path,
        content,
        message,
        branch,
    )


def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "main",
):
    """Create a GitHub pull request."""
    return github.create_pull_request(
        owner,
        repo,
        title,
        body,
        head,
        base,
    )
def run_project_tests():
    """Run the project's pytest test suite."""
    return run_tests("pytest -q")

def list_files(owner: str, repo: str, path: str = ""):
    """List files and directories in a GitHub repository."""
    return github.list_files(owner, repo, path)