import click

from gcloudai.commands import cmd,  prompt, review, release


@click.group()
def cli():
    pass

@click.command()
def echo():
    click.echo('Command echo')




# Empty Test Commands
cli.add_command(echo)
cli.add_command(cmd.sub)


cli.add_command(prompt.prompt)
cli.add_command(review.review)
cli.add_command(release.release)


if __name__ == '__main__':
    cli()