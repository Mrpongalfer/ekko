#!/usr/bin/env python3
# File: src/ekko/main.py
"""
Project Ekko - Main Entry Point (Placeholder v1.2)
Delegates based on simple logic. Corrected syntax and imports.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path  # Added missing import

# Basic logging setup (Consider moving to a central config loader later)
logging.basicConfig(level=os.environ.get("EKKO_LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("ekko.main")


def run_cli_via_entrypoint():
    """Attempts to run the CLI using the installed 'ekko' command."""
    logger.info("Attempting to run CLI via 'ekko' entry point...")
    try:
        # Ensure arguments are sanitized or trusted
        trusted_args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
        result = subprocess.run(["ekko"] + trusted_args, check=False, text=True)
        return result.returncode
    except FileNotFoundError:
        logger.error(
            "'ekko' command not found. Is venv active and project installed ('pip install -e .')?"
        )
        print("ERROR: 'ekko' command not found.", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Error running CLI via entry point: {e}", exc_info=True)
        print(f"ERROR: Could not run CLI: {e}", file=sys.stderr)
        return 1


def run_tui_directly():
    """Runs the TUI script directly using the current Python interpreter."""
    logger.info("Attempting to run TUI directly...")
    tui_script = Path(__file__).parent / "tui" / "main.py"
    if not tui_script.is_file():
        logger.error(f"TUI script not found at expected location: {tui_script}")
        print("ERROR: TUI script missing.", file=sys.stderr)
        return 1
    try:
        # Ensure arguments are sanitized or trusted
        trusted_args = [str(tui_script)]
        result = subprocess.run([sys.executable] + trusted_args, check=False, text=True)
        return result.returncode
    except Exception as e:
        logger.error(f"Error running TUI directly: {e}", exc_info=True)
        print(f"ERROR: Could not run TUI: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    run_mode = (
        "cli" if len(sys.argv) > 1 else os.environ.get("EKKO_RUN_MODE", "tui").lower()
    )
    logger.info(f"Ekko main entry point executed. Detected Mode: {run_mode}")

    exit_code = 1  # Default error code
    if run_mode == "cli":
        exit_code = run_cli_via_entrypoint()
    elif run_mode == "tui":
        exit_code = run_tui_directly()
    else:
        print(
            f"Unknown run mode: {run_mode}. Try 'ekko --help' or 'python src/ekko/tui/main.py'.",
            file=sys.stderr,
        )
        exit_code = 2

    sys.exit(exit_code)
