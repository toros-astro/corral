import sh
from corral import cli, conf, db
import models

class SqliteBrowser(cli.BaseCommand):
    def handle(self):
        if conf.settings.CONNECTION.startswith("sqlite:///"):
            path = conf.settings.CONNECTION.replace("sqlite:///", "")
            sh.sqlitebrowser(path)


class SetupCampaign(cli.BaseCommand):
    def handle(self):

        obsSite = models.Observatory()
        obsSite.name = "Macon Ridge"
        obsSite.latitude = -1.1
        obsSite.longitude = -1.1
        obsSite.description = "Macon Ridge Toritos site"

        telescopeCCD = models.CCD()
        telescopeCCD.name = ""
        telescopeCCD.brand = "Apogee"
        telescopeCCD.model = ""
        telescopeCCD.description = ""
        telescopeCCD.xpixsize = 4096
        telescopeCCD.ypixsize = 4096

        campaign = models.Campaign()
        campaign.name = "LIGO O1"
        campaign.description = "EM Follow-up Counterpart for the O1 LIGO Science Run."
        campaign.observatory = obsSite
        campaign.ccd = telescopeCCD

        with db.session_scope() as session:
            session.add(obsSite)
            session.add(telescopeCCD)
            session.add(campaign)


class SetupStates(cli.BaseCommand):
    def makeStateAndErrorState(self, name, folder, order):
        new_state = models.State()
        new_state.name = name
        new_state.folder = folder
        new_state.order = order
        new_state.is_error = False

        new_state_error = models.State()
        new_state_error.name = name + "_error"
        new_state_error.folder = folder
        new_state_error.order = order
        new_state_error.is_error = True

        return new_state, new_state_error

    def handle(self):
        states = []
        for order, (errorlabel, folder) in enumerate([('raw', 'raw'), 
                                    ('preprocessed', 'preprocessed'), 
                                    ('stacked', 'stacks')]):
            st, st_err = self.makeStateAndErrorState(errorlabel, folder, order)
            states.append(st)
            states.append(st_err)

        with db.session_scope() as session:
            for astate in states:
                session.add(astate)




