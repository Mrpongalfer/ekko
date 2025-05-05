#!/usr/bin/env python3
# File: src/ekko/cli/main.py
"""
Project Ekko - CLI Interface (using Typer) - Placeholder v1.2
Basic structure with correct syntax and imports. Functionality TBD.
"""

import logging
from typing import Annotated

import typer

# Basic logger setup (configure properly in main entry point or config loader)
logger = logging.getLogger(__name__)
# Avoid basicConfig here; let the main application configure logging.

# Create the Typer application instance
app = typer.Typer(
    name="ekko",
    help="Project Ekko: AI Development Platform CLI (v0.1 - Placeholder)",
    rich_markup_mode="markdown",
    add_completion=False,
)


@app.callback()
def main_callback(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose output.")
    ] = False,
):
    """
    Ekko CLI Root Callback. Placeholder for global options.
    """
    # Logging level should ideally be set globally based on this flag
    # For now, just log the invocation.
    logger.info(f"Ekko CLI invoked. Verbose flag: {verbose}")


@app.command()
def init(
    project_type: Annotated[
        str, typer.Option(help="Type of project (e.g., python, node)")
    ] = "python",
    project_name: Annotated[
        str | None, typer.Argument(help="Optional name for the new project.")
    ] = None,
):
    """
    Initializes a new project scaffold. [Placeholder]
    """
    print(
        f"Initializing Ekko project '{project_name or 'default'}' (Type: {project_type})... [Placeholder]"
    )
    logger.info(f"Command: init, Type: {project_type}, Name: {project_name}")
    # TODO: Implement scaffolding logic using core modules


@app.command()
def validate(
    file: Annotated[
        str | None,
        typer.Argument(
            help="Specific file path to validate. Validates project if omitted."
        ),
    ] = None,
    profile: Annotated[
        str, typer.Option(help="Validation profile (e.g., 'quick', 'full', 'security')")
    ] = "full",
):
    """
    Runs validation checks on a file or the entire project. [Placeholder]
    """
    target = file if file else "project"
    print(f"Validating '{target}' using profile '{profile}'... [Placeholder]")
    logger.info(f"Command: validate, Target: {target}, Profile: {profile}")
    # TODO: Implement validation engine calls


@app.command()
def deploy(
    env: Annotated[
        str, typer.Option(help="Target environment (e.g., staging, prod)")
    ] = "staging",
    skip_validation: Annotated[
        bool,
        typer.Option("--skip-validation", help="Skip validation checks before deploy."),
    ] = False,
):
    """
    Deploys the validated project to the target environment. [Placeholder]
    """
    print(f"Deploying to '{env}' (Skip Validation: {skip_validation})... [Placeholder]")
    logger.info(f"Command: deploy, Env: {env}, Skip Validation: {skip_validation}")
    # TODO: Implement validation (unless skipped) and Ansible/Terraform integration


# Entry point guard
if __name__ == "__main__":
    # This allows running the CLI module directly for testing if needed,
    # but the primary entry point is via the 'ekko' script installed by pip/poetry
    app()
