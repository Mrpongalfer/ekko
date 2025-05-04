#!/usr/bin/env python3
File: src/ekko/tui/main.py
Ekko TUI Block 1 - Basic Layout & System Monitor

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
--- Dependency Imports ---

try:
import psutil # For system stats
except ImportError:
logging.basicConfig(level=logging.CRITICAL)
logging.critical("psutil library not found!")
print("ERROR: psutil library not found. Please activate venv and run 'pip install psutil'", file=sys.stderr)
sys.exit("Dependency Error: psutil missing")

try:
import asyncio # Needed for sleep in example action
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, 1  Vertical, Horizontal # Added Horizontal
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Label, LoadingIndicator, Placeholder, Log # Added Log/Placeholder
from textual.binding import Binding
except ImportError as e:
logging.basicConfig(level=logging.CRITICAL)
logging.critical(f"Textual import failed: {e}")
print("ERROR: Textual library not found or failed import.", file=sys.stderr)
print("Ensure setup script ran and venv is active.", file=sys.stderr)
sys.exit(f"Dependency Error: {e}")
 1. github.com

github.com
--- Logging Setup ---

LOG_FILE = Path(file).parent.parent.parent / "ekko_tui_debug.log"
logging.basicConfig(
level=logging.DEBUG, filename=LOG_FILE, filemode='a',
format='%(asctime)s-%(levelname)s-%(name)s-%(module)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger("EkkoTUI")
--- Custom Widgets ---

class SystemMonitor(Static):
"""A widget to display basic system stats."""
cpu_usage = reactive(0.0, layout=True)
mem_usage = reactive(0.0, layout=True)
disk_usage = reactive(0.0, layout=True)
net_io = reactive(cast(Optional[Dict[str, float]], None), layout=True)

def __init__(self, update_interval: float = 2.0, **kwargs):
    super().__init__(**kwargs)
    self._update_interval = update_interval
    # Store previous net counters for rate calculation (optional enhancement)
    self._net_counters_prev: Optional[psutil._common.snetio] = None
    self._last_net_update_time: Optional[float] = None


def on_mount(self) -> None:
    """Start the update timer when the widget is mounted."""
    logger.info("SystemMonitor mounted. Starting update timer.")
    # Store initial net counters for rate calculation start
    try: self._net_counters_prev = psutil.net_io_counters(); self._last_net_update_time = time.monotonic()
    except Exception: logger.warning("Could not get initial net counters."); pass
    self.update_stats() # Initial update
    self.set_interval(self._update_interval, self.update_stats)

def update_stats(self) -> None:
    """Fetch and update system statistics."""
    try:
        self.cpu_usage = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory(); self.mem_usage = mem.percent
        disk = psutil.disk_usage('/'); self.disk_usage = disk.percent
        net_now = psutil.net_io_counters()
        self.net_io = {"sent_gb": net_now.bytes_sent/(1024**3), "recv_gb": net_now.bytes_recv/(1024**3)}
        # Basic Rate Calculation Example (Bytes/sec) - Optional
        # current_time = time.monotonic()
        # if self._net_counters_prev and self._last_net_update_time:
        #     interval = current_time - self._last_net_update_time
        #     if interval > 0:
        #          bytes_sent_rate = (net_now.bytes_sent - self._net_counters_prev.bytes_sent) / interval
        #          bytes_recv_rate = (net_now.bytes_recv - self._net_counters_prev.bytes_recv) / interval
        #          # Store rate in self.net_io if needed for display
        # self._net_counters_prev = net_now; self._last_net_update_time = current_time

        logger.debug(f"Stats updated: CPU={self.cpu_usage:.1f}%, Mem={self.mem_usage:.1f}%")
    except psutil.Error as e: logger.error(f"psutil error updating stats: {e}", exc_info=False) # Catch psutil specific errors
    except Exception as e: logger.error(f"Failed update stats: {e}", exc_info=False)

def render(self) -> Text:
    """Render the system statistics."""
    cpu_style = "bold green" if self.cpu_usage < 70 else ("bold yellow" if self.cpu_usage < 90 else "bold red")
    mem_style = "bold green" if self.mem_usage < 70 else ("bold yellow" if self.mem_usage < 90 else "bold red")
    disk_style = "bold green" if self.disk_usage < 70 else ("bold yellow" if self.disk_usage < 90 else "bold red")
    net_str = "[dim]Net IO: N/A[/]"
    if self.net_io: net_str = f"Net IO: Sent=[bold green]{self.net_io['sent_gb']:.2f} GB[/] Recv=[bold cyan]{self.net_io['recv_gb']:.2f} GB[/]"

    # Using Text.assemble for easier styling composition
    return Text.assemble(
        ("CPU: ", "default"), (f"{self.cpu_usage:>5.1f}%", cpu_style), (" | ", "default"),
        ("MEM: ", "default"), (f"{self.mem_usage:>5.1f}%", mem_style), (" | ", "default"),
        ("DISK(/): ", "default"), (f"{self.disk_usage:>5.1f}%", disk_style), ("\n", "default"), # Newline
        (net_str, "default") # Already styled
    )

--- Main TUI Application ---

class EkkoTUI(App[None]):
"""Project Ekko Textual User Interface."""
TITLE = "Project Ekko Control Plane v0.1"
# Load CSS from file (optional)
# CSS_PATH = "main.css"
CSS = """
Screen { layout: grid; grid-size: 2; grid-columns: auto 1fr; grid-rows: auto 1fr auto; }
Header { grid-column: 1 / 3; grid-row: 1; }
Footer { grid-column: 1 / 3; grid-row: 3; }
#sidebar { grid-column: 1; grid-row: 2; width: 30; border-right: thick $accent; padding: 1; overflow-y: auto;}
#main-area { grid-column: 2; grid-row: 2; padding: 0 1; display: block; } /* Use block layout /
#system-monitor { height: 3; margin-bottom: 1; border: round $accent; padding: 0 1;} / Adjusted height/padding /
#main-content-scroll { height: 1fr; / Takes remaining space / }
#main-content { padding: 1; border: round $accent; } / Scrollable main content /
#log-pane { height: 10; border: round $accent; margin-top: 1; }
#loading { width: 100%; height: 1; display: none; margin-top: 1; text-align: center; }
.view { display: none; padding: 1; border: round $primary-lighten-2; margin-top: 1; } / Basic view styling */
.view.visible { display: block; }
"""
BINDINGS = [
Binding("d", "toggle_dark", "Toggle Dark"), ("q", "request_quit", "Quit"),
Binding("ctrl+l", "clear_log", "Clear Log"),
Binding("1", "show_view('status-view')", "Status/Monitor"),
Binding("2", "show_view('git-view')", "Git Control (NYI)"),
Binding("3", "show_view('scribe-view')", "Scribe Agent (NYI)"),
Binding("4", "show_view('ansible-view')", "Ansible Control (NYI)"),
Binding("l", "toggle_log", "Toggle Log"),
]
show_log_pane = reactive(True)

def compose(self) -> ComposeResult:
    logger.info("Composing Ekko TUI...")
    yield Header()
    with Container(id="sidebar"):
        yield Label("[b u]Ekko Control[/b u]")
        yield Static("1: [green]Status & Monitor[/green]")
        yield Static("2: [dim]Git Control[/dim]")
        yield Static("3: [dim]Scribe Agent[/dim]")
        yield Static("4: [dim]Ansible Control[/dim]")
        yield Static("---"); yield Static("L: Toggle Log"); yield Static("D: Dark Mode"); yield Static("Q: Quit")
    with Container(id="main-area"):
        yield SystemMonitor(id="system-monitor") # System monitor at the top
        with VerticalScroll(id="main-content-scroll"): # Scroll view for main content
            # Add views inside the scrollable container
            yield Static("Welcome! System monitoring active above. Select view using 1-4.", id="status-view", classes="view visible")
            yield Static("[bold yellow]Git Operations Panel[/]\n\n(Placeholder for `lazygit` integration or custom Git commands)", id="git-view", classes="view")
            yield Static("[bold cyan]Scribe Agent Panel[/]\n\n(Placeholder for invoking `scribe_agent.py` and displaying JSON report)", id="scribe-view", classes="view")
            yield Static("[bold magenta]Ansible Control Panel[/]\n\n(Placeholder for running playbooks via `ansible-runner`)", id="ansible-view", classes="view")
        yield LoadingIndicator(id="loading") # Loading indicator below content
        yield Log(id="log-pane", auto_scroll=True, max_lines=1000, markup=True) # Log pane below loading
    yield Footer()

def on_mount(self) -> None:
    log_widget = self.query_one(Log); log_widget.write_line("[bold green]Ekko TUI Initialized.[/]"); log_widget.write_line(f"[dim]Debug Log: {LOG_FILE}[/]"); logger.info("Ekko TUI Mounted.")
    self.action_toggle_log() # Start with log hidden initially? Or shown? Let's start shown.

def watch_show_log_pane(self, show: bool) -> None: self.set_class(show, "show-log"); self.query_one(Log).display = show

def action_toggle_dark(self) -> None: self.dark = not self.dark; logger.debug("Toggled dark.")
def action_request_quit(self) -> None: logger.info("Quit requested."); self.exit("User quit.")
def action_clear_log(self) -> None: self.query_one(Log).clear(); logger.info("Log cleared."); self.query_one(Log).write_line("[dim]Log Cleared.[/]")
def action_toggle_log(self) -> None: self.show_log_pane = not self.show_log_pane; logger.info(f"Log toggled: {self.show_log_pane}")

def action_show_view(self, view_id: str) -> None:
    logger.info(f"Switching view to: {view_id}")
    # Use query to get all view elements, hide them, then show the target one
    for view in self.query(".view"): view.display = False
    try: self.query_one(f"#{view_id}").display = True
    except Exception: logger.error(f"View ID not found: {view_id}")
    # Example of using loader
    async def simulate_load():
        loader = self.query_one(LoadingIndicator); loader.display = True
        self.query_one(Log).write_line(f"Loading view '{view_id}'...")
        await asyncio.sleep(0.5) # Simulate loading time
        loader.display = False
    self.run_worker(simulate_load(), exclusive=True)

if name == "main":
logger.info("--- Starting Ekko TUI Application ---")
app = EkkoTUI(); app.run()
logger.info("--- Ekko TUI Application Exited ---")
