import click

from commands import cmd,  prompt, review, release


@click.group()
def devai():
    pass

@click.command()
def echo():
    click.echo('Command echo')


# Empty Test Commands
devai.add_command(echo)
devai.add_command(cmd.sub)


devai.add_command(prompt.prompt)
devai.add_command(review.review)
devai.add_command(release.release)


if __name__ == '__main__':
    devai()
