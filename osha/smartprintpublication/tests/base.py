from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import quickInstallProduct
from plone.testing import z2


class OshaSmartPrintPublication(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import osha.smartprintpublication
        self.loadZCML('configure.zcml', package=osha.smartprintpublication)

        z2.installProduct(app, 'osha.smartprintpublication')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'osha.smartprintpublication:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'osha.smartprintpublication')


OSHA_SMARTPRINTPUBLICATION_FIXTURE = OshaSmartPrintPublication()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(OSHA_SMARTPRINTPUBLICATION_FIXTURE,),
    name="OshaSmartPrintPublication:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OSHA_SMARTPRINTPUBLICATION_FIXTURE,),
    name="OshaSmartPrintPublication:Functional")
