import sys
import traceback
from io import StringIO


class CodeExecutor:
    def run(self, code: str) -> dict:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        try:
            exec(code, {"__builtins__": __builtins__}, {})
            
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            output = stdout_output
            if stderr_output:
                output += f"\n[stderr]: {stderr_output}"
            
            return {
                "status": "success",
                "output": output.strip() if output.strip() else "Код выполнен успешно (нет вывода)"
            }
        except Exception as e:
            return {
                "status": "error",
                "traceback": traceback.format_exc()
            }
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
