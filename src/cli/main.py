# src/cli/main.py
import click

@click.group()
def cli():
    """Ekko v0.1 - Reality Forge"""

@cli.command()
@click.argument('project')
def init(project):
    """Scaffold new project"""
    click.echo(f"Initializing {project} with Ekko rules...")

if __name__ == "__main__":
    cli()
