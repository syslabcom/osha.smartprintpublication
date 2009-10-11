from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable, IAnnotatable
from zope.interface import Interface, implements
from zope.component import adapts
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.formlib import form
from persistent import Persistent
from zope.annotation import factory
from Products.ATContentTypes.interface.document import IATDocument
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
import Acquisition
import transaction

from osha.smartprintpublication.interfaces import IOshaSmartprintSettings
from osha.smartprintpublication.browser.widget import ReferenceURLWidget
from osha.theme import OSHAMessageFactory as _


class OshaSmartprintSettings(Persistent):
    implements(IOshaSmartprintSettings)
    adapts(IATDocument)

    @property
    def portal_catalog(self):        
        """ make the adapter penetratable for the vocabulary to find the cat"""
        return getToolByName(getSite(), 'portal_catalog')

    @property
    def portal_url(self):        
        """ make the adapter penetratable for the vocabulary to find the cat"""
        return getToolByName(getSite(), 'portal_url')

    path = ''
    issue = ''
    existing_publication = ''
    subject = tuple()

smartprint_adapter_document = factory(OshaSmartprintSettings)

class OshaSmartprintSettingsForm(form.PageEditForm):
    form_fields = form.Fields(IOshaSmartprintSettings)
    label = u"Please specify the details for the publication"
    form_fields['path'].custom_widget = UberSelectionWidget
    form_fields['existing_publication'].custom_widget = ReferenceURLWidget

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        
        settings = IOshaSmartprintSettings(self.context)
        settings.path = data['path']
        settings.issue = data['issue']
        settings.subject = data['subject']
        
        asPDF = self.context.restrictedTraverse('asPDF', None)
        if not asPDF:
            # sth bad has happened
            print "view asPDF not found"
            return
        rawPDF = asPDF(number=data['issue'], plainfile=True)

        path = data['path']
        if path.startswith('/'):
            path = path[1:]
        dest = self.context.restrictedTraverse(path, None)
        filename = "%s.pdf" %self.context.getId()
        if not dest:
            print "destination folder not found!"
            return

        verb ="Updated"
        if not getattr(Acquisition.aq_base(dest), filename, None):
            dest.invokeFactory(type_name="File", id=filename)
            transaction.savepoint()
            verb="Added"
        newFile = getattr(dest, filename)
        newFile.unmarkCreationFlag()

        newFile.processForm(values=dict(id=filename, title=self.context.Title()))
        newFile.setFile(rawPDF)
        newFile.setSubject(data['subject'])
        
        self.status = u"%(verb)s publication at %(url)s" %dict(verb=verb, url=newFile.absolute_url())
        settings.existing_publication = newFile.UID()
        # del newFile
        
        