import sh
from corral import cli, conf

class SqliteBrowser(cli.BaseCommand):
    def handle(self):
        if conf.settings.CONNECTION.startswith("sqlite:///"):
            path = conf.settings.CONNECTION.replace("sqlite:///", "")
            sh.sqlitebrowser(path)

