import click
from vertexai.generative_models import GenerativeModel

@click.command()
def healthcheck():
    """Test connectivity to Vertex AI using Gemini."""
    click.echo("Testing Vertex AI connectivity...")
    
    try:
        # Initialize Gemini
        model = GenerativeModel("gemini-pro")
        
        # Simple test prompt
        response = model.generate_content("Say 'Hello World!'")
        
        click.echo(f"Success! Response: {response.text}")
        click.echo("\nEnvironment Info:")
        click.echo("- Model: gemini-pro")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()  # This will set exit code to 1 