from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunserverCommand,
)


class Command(RunserverCommand):
    """Development server that does not inspect Django migration state.

    The existing MySQL schema is managed outside Django, so migration checks
    are intentionally skipped for this project.
    """

    def check_migrations(self):
        return None
