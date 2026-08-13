import time
from github_client import GitHubClient
from code_executor import (
    cleanup_workspace,
    run_tests,
)

from git_operations import (
    create_branch,
    commit_changes,
    push_branch,
)

from workspace import (
    create_workspace,
    write_file,
)


def execute_engineering_change(
    owner: str,
    repo: str,
    file_path: str,
    new_content: str,
    commit_message: str,
    branch_name: str | None = None,
):

    logs = []

    workspace = create_workspace(
        owner,
        repo,
    )

    logs.append(
        "✓ Repository cloned"
    )

    try:

        if branch_name is None:
            branch_name = (
                f"ai-agent-{int(time.time())}"
            )

        # Create branch
        create_branch(
            workspace,
            branch_name,
        )

        logs.append(
            f"✓ Created branch `{branch_name}`"
        )

        write_file(
            workspace,
            file_path,
            new_content,
        )

        logs.append(
            f"✓ Modified `{file_path}`"
        )

        # Run tests
        test_result = run_tests(
            workspace
        )

        if not test_result["success"]:

            logs.append(
                "❌ Tests failed"
            )

            return {
                "success": False,
                "branch": branch_name,
                "logs": logs,
                "tests": test_result,
            }

        logs.append(
            "✓ Tests passed"
        )

        # Commit
        commit_changes(
            workspace,
            commit_message,
        )

        logs.append(
            "✓ Changes committed"
        )

        # Push
        push_branch(
            workspace,
            branch_name,
        )

        logs.append(
            "✓ Branch pushed to GitHub"
        )

        # Create Pull Request
        pull_request = create_pull_request(
            owner=owner,
            repo=repo,
            title=commit_message,
            body=(
                "## GitHub AI Engineering Agent\n\n"
                "This pull request was generated "
                "automatically by the AI Engineering Agent.\n\n"
                "### Validation\n"
                "- Repository cloned successfully\n"
                "- Code modification completed\n"
                "- Tests passed\n"
                f"- Branch: `{branch_name}`\n"
                f"- Test result: `{test_result['success']}`\n"
            ),
            head=branch_name,
            base="master",
        )

        logs.append(
            f"✓ Pull request created: #{pull_request['number']}"
        )

        return {
            "success": True,
            "branch": branch_name,
            "logs": logs,
            "tests": test_result,
            "pull_request": pull_request,
        }

    finally:

        cleanup_workspace(
            workspace
        )