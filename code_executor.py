import subprocess
def run_tests(test_command="pytest -q"):
    """Run the project's test suite safely."""

    try:
        result = subprocess.run(
            test_command,
            shell=True,
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
            "stderr": "Tests timed out after 60 seconds.",
        }