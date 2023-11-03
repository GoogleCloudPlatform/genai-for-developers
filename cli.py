import click


from gcloudai.commands import cmd,  prompt


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



if __name__ == '__main__':
    cli()