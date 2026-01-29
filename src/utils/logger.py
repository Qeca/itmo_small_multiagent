from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.json import JSON
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
import sys


class AgentLogger:
    def __init__(self):
        self.console = Console()
        self.current_stream = []
        self.live = None
    
    def header(self, text: str):
        self.console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        self.console.print(f"[bold cyan]{text}[/bold cyan]")
        self.console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
    
    def agent_start(self, agent_name: str, task: str = ""):
        emoji = {
            "Orchestrator": "🎯",
            "Analyst": "🔍",
            "Command Agent": "⚙️",
            "CLI Agent": "💻"
        }.get(agent_name, "🤖")
        
        panel = Panel(
            f"[yellow]{task}[/yellow]" if task else "[dim]Starting...[/dim]",
            title=f"{emoji} [bold green]{agent_name}[/bold green]",
            border_style="green"
        )
        self.console.print(panel)
    
    def agent_decision(self, decision: dict):
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[cyan]Agent:[/cyan]", f"[yellow]{decision.get('agent', 'N/A')}[/yellow]")
        table.add_row("[cyan]Reasoning:[/cyan]", decision.get('reasoning', 'N/A'))
        
        panel = Panel(
            table,
            title="📋 [bold]Decision[/bold]",
            border_style="blue"
        )
        self.console.print(panel)
    
    def code_generated(self, code: str):
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        panel = Panel(
            syntax,
            title="📝 [bold]Generated Code[/bold]",
            border_style="magenta"
        )
        self.console.print(panel)
    
    def code_result(self, result: dict):
        status = result.get("status", "unknown")
        color = "green" if status == "success" else "red"
        emoji = "✅" if status == "success" else "❌"
        
        output = result.get("output", result.get("traceback", "No output"))
        
        title = f"{emoji} Execution Result ({status})"
        
        panel = Panel(
            f"[{color}]{output}[/{color}]",
            title=f"[bold]{title}[/bold]",
            border_style=color
        )
        self.console.print(panel)
    
    def code_review(self, review: str):
        panel = Panel(
            f"[dim]{review}[/dim]",
            title="📊 [bold]Code Review[/bold]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def cli_commands(self, commands: list[str]):
        text = "\n".join([f"$ {cmd}" for cmd in commands])
        panel = Panel(
            f"[yellow]{text}[/yellow]",
            title="💻 [bold]Commands[/bold]",
            border_style="yellow"
        )
        self.console.print(panel)
    
    def cli_result(self, result: dict):
        cmd = result.get("command", "")
        res = result.get("result", {})
        status = res.get("status", "unknown")
        
        color = "green" if status == "success" else "red"
        emoji = "✅" if status == "success" else "❌"
        
        output = res.get("output", "") or res.get("stdout", "") or res.get("stderr", "")
        
        self.console.print(f"\n[bold]$ {cmd}[/bold]")
        panel = Panel(
            f"[{color}]{output}[/{color}]" if output else "[dim]Команда выполнена (нет вывода)[/dim]",
            title=f"{emoji} [bold]Result[/bold]",
            border_style=color
        )
        self.console.print(panel)
    
    def final_answer(self, answer: str):
        self.console.print("\n")
        self.console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
        self.console.print("[bold cyan]🎉 ИТОГОВЫЙ РЕЗУЛЬТАТ[/bold cyan]")
        self.console.print("[bold cyan]" + "=" * 80 + "[/bold cyan]")
        self.console.print()
        
        panel = Panel(
            f"{answer}",
            border_style="green"
        )
        self.console.print(panel)
        self.console.print()
    
    def step(self, message: str):
        self.console.print(f"  [dim]→ {message}[/dim]")
    
    def error(self, message: str):
        self.console.print(f"[bold red]❌ Error:[/bold red] {message}")
    
    def memory_saved(self, agent: str, action: str):
        self.console.print(f"  [dim]💾 Saved to memory: [{agent}] {action}[/dim]")
    
    def memory_found(self, count: int):
        if count > 0:
            self.console.print(f"  [dim]🧠 Found {count} similar tasks in memory[/dim]")
        else:
            self.console.print(f"  [dim]🧠 No similar tasks found (first time)[/dim]")
    
    def thinking(self, agent: str):
        emoji = {
            "Analyst": "🔍",
            "Command Agent": "⚙️",
            "CLI Agent": "💻"
        }.get(agent, "🤖")
        self.console.print(f"  {emoji} [dim italic]Thinking...[/dim italic]")
    
    def stream_start(self, title: str = "Response"):
        self.current_stream = []
        self.console.print(f"\n[bold cyan]💭 {title}:[/bold cyan]")
    
    def stream_token(self, token: str):
        self.console.print(token, end="")
        sys.stdout.flush()
    
    def stream_end(self):
        self.console.print("\n")
    
    def tool_start(self, tool_name: str, args: dict = None):
        tool_emoji = {
            "execute_python_code": "🐍",
            "execute_shell_command": "💻",
            "search_web": "🌐",
            "search_memory": "🧠",
            "add_to_memory": "💾"
        }.get(tool_name, "🔧")
        
        args_str = ""
        if args:
            if "code" in args:
                args_str = f"[dim](code: {len(args['code'])} chars)[/dim]"
            elif "command" in args:
                args_str = f"[dim]({args['command']})[/dim]"
            elif "query" in args:
                args_str = f"[dim]({args['query'][:50]}...)[/dim]"
        
        self.console.print(f"  {tool_emoji} [yellow]Executing {tool_name}[/yellow] {args_str}")
    
    def tool_end(self, tool_name: str, success: bool = True, result: str = None):
        emoji = "✅" if success else "❌"
        self.console.print(f"  {emoji} [dim]{tool_name} completed[/dim]")
        
        if result and tool_name in ["search_memory", "search_web"]:
            truncated = result[:500] + "..." if len(result) > 500 else result
            self.console.print(Panel(
                f"[dim]{truncated}[/dim]",
                title=f"🔍 [bold]{tool_name} result[/bold]",
                border_style="dim"
            ))
    
    def progress(self, message: str):
        self.console.print(f"  [dim cyan]⏳ {message}[/dim cyan]")
    
    def debug_attempt(self, attempt: int, max_attempts: int = 3):
        self.console.print(f"\n  [bold yellow]🔧 Auto-debug attempt {attempt}/{max_attempts}[/bold yellow]")
