import subprocess


class CLIExecutor:
    def run(self, command: str) -> dict:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "stdout": "",
                "stderr": "Command timeout (30s)",
                "returncode": -1
            }
        except Exception as e:
            return {
                "status": "error",
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
