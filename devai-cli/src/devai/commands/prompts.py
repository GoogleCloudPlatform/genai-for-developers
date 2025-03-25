import os
import yaml
import click
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from vertexai.generative_models import GenerativeModel
from google.cloud.aiplatform import telemetry
from google.api_core.gapic_v1.client_info import ClientInfo
from .constants import USER_AGENT, MODEL_NAME
import pkg_resources

# User configuration file path
CONFIG_DIR = Path.home() / '.devai'
CONFIG_FILE = CONFIG_DIR / 'config.json'

def get_package_prompts_dir() -> Path:
    """Get the path to the package's prompts directory."""
    # Get the package directory (where devai/commands/prompts.py is)
    package_dir = Path(__file__).parent.parent.parent
    # Go up one level to src
    return package_dir / 'prompts'

def get_user_prompts_dir() -> Optional[Path]:
    """Get the user's custom prompts directory if configured."""
    # First check if user has set a custom path in config
    config = get_config()
    prompts_dir = config.get('prompts_dir')
    if prompts_dir and prompts_dir.strip():
        return Path(prompts_dir)
    
    # If no custom path, check if user has initialized prompts directory
    default_dir = Path.home() / '.devai' / 'prompts'
    if default_dir.exists():
        return default_dir
    
    return None

def get_prompts_dir() -> Path:
    """Get the prompts directory path from config or default."""
    # Check for user's custom prompts directory first
    user_dir = get_user_prompts_dir()
    if user_dir:
        return user_dir
    
    # Default to package prompts directory
    return get_package_prompts_dir()

def find_prompt_file(path: str) -> Tuple[Path, bool]:
    """Find a prompt file, checking user directory first, then package directory.
    Returns (path, is_user_override)"""
    # Check user's custom directory first
    user_dir = get_user_prompts_dir()
    if user_dir:
        user_file = user_dir / path
        if user_file.exists():
            return user_file, True
    
    # Fall back to package directory
    package_file = get_package_prompts_dir() / path
    return package_file, False

def get_config():
    """Get user configuration."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    """Save user configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def set_prompts_dir(path: str):
    """Set the prompts directory path in config."""
    config = get_config()
    config['prompts_dir'] = str(path)
    save_config(config)
    return Path(path)

@click.group()
def prompts():
    """Manage DevAI prompt templates."""
    pass

@prompts.command(name='config')
@click.option('--set-path', help='Set the prompts directory path')
@click.option('--show', is_flag=True, help='Show current prompts directory path')
@click.option('--reset', is_flag=True, help='Reset to use package prompts')
def config_prompts(set_path: Optional[str], show: bool, reset: bool):
    """Configure prompts directory settings."""
    if reset:
        config = get_config()
        if 'prompts_dir' in config:
            del config['prompts_dir']
            save_config(config)
        click.echo("Reset to use package prompts")
        return
    
    if show:
        user_dir = get_user_prompts_dir()
        if user_dir:
            click.echo(f"Using custom prompts directory: {user_dir}")
        else:
            click.echo(f"Using package prompts directory: {get_package_prompts_dir()}")
        return
    
    if set_path:
        try:
            new_path = set_prompts_dir(set_path)
            click.echo(f"Custom prompts directory set to: {new_path}")
            click.echo("You can override package prompts by creating files with the same names in this directory")
        except Exception as e:
            click.echo(f"Error setting prompts directory: {str(e)}", err=True)
        return
    
    click.echo("Please specify either --set-path, --show, or --reset")

@prompts.command(name='list')
@click.option('--category', '-c', help='Filter prompts by category')
@click.option('--subcategory', '-s', help='Filter prompts by subcategory')
@click.option('--tag', '-t', multiple=True, help='Filter prompts by tags')
def list_prompts(category: Optional[str], subcategory: Optional[str], tag: Optional[List[str]]):
    """List available prompt templates."""
    # Get all yaml files from both package and user directories
    package_files = []
    user_files = []
    
    # Add package prompts
    package_dir = get_package_prompts_dir()
    if package_dir.exists():
        package_files.extend(package_dir.rglob('*.yaml'))
    
    # Add user prompts (these will override package prompts)
    user_dir = get_user_prompts_dir()
    if user_dir and user_dir.exists():
        user_files.extend(user_dir.rglob('*.yaml'))
    
    if not package_files and not user_files:
        click.echo("No prompt templates found")
        return
    
    # Track which files we've shown to avoid duplicates
    shown_files = set()
    
    def print_prompt_info(prompt_file: Path, is_user_override: bool = False):
        try:
            with open(prompt_file, 'r') as f:
                data = yaml.safe_load(f)
                metadata = data.get('metadata', {})
                
                # Apply filters
                if category and metadata.get('category') != category:
                    return
                if subcategory and metadata.get('subcategory') != subcategory:
                    return
                if tag and not all(t in metadata.get('tags', []) for t in tag):
                    return
                
                # Print prompt info
                click.echo(f"\n{click.style(metadata.get('name', 'Unnamed'), fg='green')}")
                click.echo(f"  Category: {metadata.get('category', 'N/A')}")
                click.echo(f"  Subcategory: {metadata.get('subcategory', 'N/A')}")
                click.echo(f"  Description: {metadata.get('description', 'No description')}")
                click.echo(f"  Tags: {', '.join(metadata.get('tags', []))}")
                if is_user_override:
                    click.echo(f"  Path: {prompt_file.absolute()}")
                    click.echo("  (User override)")
                else:
                    click.echo(f"  Path: {prompt_file.relative_to(prompt_file.parent.parent)}")
                
                shown_files.add(prompt_file.name)
                
        except Exception as e:
            click.echo(f"Error reading {prompt_file}: {str(e)}", err=True)
    
    # First show package prompts (default)
    if package_files:
        click.echo("\n=== Default Prompts ===")
        for prompt_file in package_files:
            # Skip if this file is overridden by a user file
            if prompt_file.name in [f.name for f in user_files]:
                continue
            print_prompt_info(prompt_file)
    
    # Then show user prompts (custom)
    if user_files:
        click.echo("\n=== Custom Prompts ===")
        for prompt_file in user_files:
            print_prompt_info(prompt_file, is_user_override=True)

@prompts.command(name='show')
@click.argument('path')
def show_prompt(path: str):
    """Show details of a specific prompt template."""
    prompt_file, is_user_override = find_prompt_file(path)
    
    if not prompt_file.exists():
        click.echo(f"Error: Prompt template not found at {path}", err=True)
        return
    
    try:
        with open(prompt_file, 'r') as f:
            data = yaml.safe_load(f)
            
            # Print metadata
            metadata = data.get('metadata', {})
            click.echo(f"\n{click.style(metadata.get('name', 'Unnamed'), fg='green')}")
            if is_user_override:
                click.echo("(User override)")
            click.echo(f"Category: {metadata.get('category', 'N/A')}")
            click.echo(f"Subcategory: {metadata.get('subcategory', 'N/A')}")
            click.echo(f"Description: {metadata.get('description', 'No description')}")
            click.echo(f"Tags: {', '.join(metadata.get('tags', []))}")
            
            # Print configuration
            config = data.get('configuration', {})
            click.echo("\nConfiguration:")
            click.echo(f"  Temperature: {config.get('temperature', 'N/A')}")
            click.echo(f"  Max Tokens: {config.get('max_tokens', 'N/A')}")
            click.echo(f"  Output Format: {config.get('output_format', 'N/A')}")
            
            # Print prompt sections
            prompt = data.get('prompt', {})
            click.echo("\nSystem Context:")
            click.echo(prompt.get('system_context', 'N/A'))
            
            click.echo("\nInstruction:")
            click.echo(prompt.get('instruction', 'N/A'))
            
            if 'examples' in prompt:
                click.echo("\nExamples:")
                for i, example in enumerate(prompt['examples'], 1):
                    click.echo(f"\nExample {i}:")
                    click.echo("Input:")
                    click.echo(example.get('input', 'N/A'))
                    click.echo("Output:")
                    click.echo(example.get('output', 'N/A'))
            
            # Print validation
            validation = data.get('validation', {})
            if validation:
                click.echo("\nValidation:")
                click.echo(f"  Required Sections: {', '.join(validation.get('required_sections', []))}")
                click.echo(f"  Quality Checks: {', '.join(validation.get('quality_checks', []))}")
                
    except Exception as e:
        click.echo(f"Error reading prompt template: {str(e)}", err=True)

@prompts.command(name='create')
@click.option('--name', prompt='Template name')
@click.option('--category', prompt='Category')
@click.option('--subcategory', prompt='Subcategory')
@click.option('--description', prompt='Description')
@click.option('--tags', prompt='Tags (comma-separated)')
def create_prompt(name: str, category: str, subcategory: str, description: str, tags: str):
    """Create a new prompt template."""
    # Always create in user's custom directory
    user_dir = get_user_prompts_dir()
    if not user_dir:
        click.echo("Error: Please set a custom prompts directory first using 'devai prompts config --set-path'")
        return
    
    category_dir = user_dir / category.lower()
    
    # Create category directory if it doesn't exist
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # Create template file
    template_file = category_dir / f"{subcategory.lower()}.yaml"
    
    if template_file.exists():
        if not click.confirm(f"Template already exists at {template_file}. Overwrite?"):
            return
    
    template = {
        'metadata': {
            'name': name,
            'description': description,
            'version': '1.0',
            'category': category,
            'subcategory': subcategory,
            'author': 'DevAI',
            'last_updated': '2024-03-25',
            'tags': [tag.strip() for tag in tags.split(',')]
        },
        'configuration': {
            'temperature': 0.7,
            'max_tokens': 1024,
            'output_format': 'markdown'
        },
        'prompt': {
            'system_context': f"You are an expert in {category} with extensive experience in {subcategory}.",
            'instruction': "### Task Description ###\n\n### Focus Areas ###\n\n### Analysis Requirements ###\n\n### Output Format ###\n",
            'examples': [
                {
                    'input': 'Example input',
                    'output': 'Example output'
                }
            ]
        },
        'validation': {
            'required_sections': [],
            'output_schema': {},
            'quality_checks': []
        }
    }
    
    try:
        with open(template_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False)
        click.echo(f"Created new template at {template_file}")
    except Exception as e:
        click.echo(f"Error creating template: {str(e)}", err=True)

@prompts.command(name='execute')
@click.argument('path')
@click.option('--input', '-i', help='Input text to send with the prompt')
@click.option('--output-format', '-f', type=click.Choice(['markdown', 'json', 'text']), help='Override the output format')
def execute_prompt(path: str, input: Optional[str], output_format: Optional[str]):
    """Execute a prompt template with Gemini."""
    prompt_file, is_user_override = find_prompt_file(path)
    
    if not prompt_file.exists():
        click.echo(f"Error: Prompt template not found at {path}", err=True)
        return
    
    try:
        # Load the prompt template
        with open(prompt_file, 'r') as f:
            template = yaml.safe_load(f)
        
        # Get configuration
        config = template.get('configuration', {})
        if output_format:
            config['output_format'] = output_format
            
        # Get the prompt sections
        prompt_data = template.get('prompt', {})
        system_context = prompt_data.get('system_context', '')
        instruction = prompt_data.get('instruction', '')
        
        # Build the full prompt
        full_prompt = f"{system_context}\n\n{instruction}"
        if input:
            full_prompt += f"\n\nInput:\n{input}"
            
        # Initialize Gemini with telemetry
        client_info = ClientInfo(user_agent=USER_AGENT)
        with telemetry.tool_context_manager(USER_AGENT):
            model = GenerativeModel(MODEL_NAME)
            
            # Generate response
            response = model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': config.get('temperature', 0.7),
                    'max_output_tokens': config.get('max_tokens', 1024),
                }
            )
        
        # Format and display the response
        if config.get('output_format') == 'json':
            try:
                import json
                # Try to parse the response as JSON if it looks like JSON
                if response.text.strip().startswith('{') or response.text.strip().startswith('['):
                    json_response = json.loads(response.text)
                    click.echo(json.dumps(json_response, indent=2))
                else:
                    click.echo(response.text)
            except json.JSONDecodeError:
                click.echo(response.text)
        else:
            click.echo(response.text)
            
    except Exception as e:
        click.echo(f"Error executing prompt: {str(e)}", err=True)

@prompts.command(name='init')
@click.option('--force', is_flag=True, help='Force initialization even if directory exists')
def init_prompts(force: bool):
    """Initialize a prompts directory with sample templates."""
    # Get the prompts directory from config or default
    prompts_dir = get_prompts_dir()
    
    # Check if directory exists
    if prompts_dir.exists():
        if not force:
            if not click.confirm(f"Directory {prompts_dir} already exists. Initialize anyway?"):
                return
        click.echo(f"Initializing existing directory: {prompts_dir}")
    else:
        click.echo(f"Creating new prompts directory: {prompts_dir}")
        prompts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create basic directory structure
    categories = ['security', 'testing', 'performance', 'documentation']
    for category in categories:
        (prompts_dir / category).mkdir(exist_ok=True)
    
    # Create a sample template
    sample_template = {
        'metadata': {
            'name': 'Web Security Review',
            'description': 'Review web application security best practices',
            'version': '1.0',
            'category': 'security',
            'subcategory': 'web-security',
            'author': 'DevAI',
            'last_updated': '2024-03-25',
            'tags': ['security', 'web', 'review']
        },
        'configuration': {
            'temperature': 0.7,
            'max_tokens': 1024,
            'output_format': 'markdown'
        },
        'prompt': {
            'system_context': 'You are a security expert reviewing web applications.',
            'instruction': 'Review the following web application code for security vulnerabilities and best practices.',
            'examples': [
                {
                    'input': 'Check this login form for security issues',
                    'output': '1. Missing CSRF token\n2. Password field lacks minimum length requirement\n3. No rate limiting on login attempts'
                }
            ]
        },
        'validation': {
            'required_sections': ['vulnerabilities', 'recommendations'],
            'output_schema': {},
            'quality_checks': []
        }
    }
    
    # Save the sample template
    sample_file = prompts_dir / 'security' / 'web-security.yaml'
    with open(sample_file, 'w') as f:
        yaml.dump(sample_template, f, default_flow_style=False)
    
    click.echo(f"Initialized prompts directory")
    click.echo(f"Created sample template: security/web-security.yaml")
    click.echo("\nYou can now:")
    click.echo("1. Add your own prompt templates to this directory")
    click.echo("2. Override package prompts by creating files with the same names")
    click.echo("3. Use 'devai prompts list' to see all available templates") 