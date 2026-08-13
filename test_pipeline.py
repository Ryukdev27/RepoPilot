from engineering_pipeline import execute_engineering_change
import os
result = execute_engineering_change(
    owner=os.getenv("GITHUB_TEST_OWNER"),
    repo=os.getenv("GITHUB_TEST_REPO"),
    file_path="app/text_processor.py",
    new_content='''def count_words(text: str) -> int:
    """Return the number of words in a text."""

    if not text:
        return 0

    return len(text.split())


def extract_title(text: str) -> str:
    """Extract the first non-empty line as a document title."""

    if not text:
        return ""

    for line in text.splitlines():
        title = line.strip()

        if title:
            return title

    return ""
''',
    commit_message="fix: improve document title extraction",
)

print()
print("SUCCESS:", result["success"])
print("BRANCH:", result.get("branch"))

print()
print("LOGS:")

for log in result["logs"]:
    print(log)

print()
print("========== TEST STDOUT ==========")
print(result["tests"]["stdout"])

print()
print("========== TEST STDERR ==========")
print(result["tests"]["stderr"])

print()
print("TEST RETURN CODE:", result["tests"]["return_code"])