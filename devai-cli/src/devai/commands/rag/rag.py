import click
from devai.commands.rag import load, query

@click.group()
def rag():
    pass


rag.add_command(load.load)
rag.add_command(load.testdb)
rag.add_command(query.query)
