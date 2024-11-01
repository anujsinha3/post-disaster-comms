import typer
from support_sphere.scripts.execute_sql_statement import execute_sql_app

# The parent app that will contain all future child apps for different script types
app = typer.Typer()

app.add_typer(execute_sql_app, name="execute_sql")

if __name__ == "__main__":
    app()
