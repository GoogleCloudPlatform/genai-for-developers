import click
from vertexai.generative_models import GenerativeModel
from devai.util.constants import GEMINI_PRO_MODEL

@click.command()
def healthcheck():
    """Test connectivity to Vertex AI using Gemini."""
    click.echo("Testing Vertex AI connectivity...")
    
    try:
        # Initialize Gemini
        model = GenerativeModel(GEMINI_PRO_MODEL)
        
        # Simple test prompt
        response = model.generate_content("Say 'Hello World!'")
        
        click.echo(f"Success! Response: {response.text}")
        click.echo("\nEnvironment Info:")
        click.echo(f"- Model: {GEMINI_PRO_MODEL}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()  # This will set exit code to 1 