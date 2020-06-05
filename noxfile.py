import tempfile

import nox

locations = "src", "noxfile.py"
nox.options.sessions = "lint", "mypy"


def install_with_constraints(session, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session
def black(session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session
def lint(session):
    args = session.posargs or locations
    install_with_constraints(
        session, "flake8", "flake8-bandit", "flake8-black", "flake8-import-order"
    )
    session.run("flake8", *args)


@nox.session
def mypy(session):
    args = session.posargs or locations
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)
