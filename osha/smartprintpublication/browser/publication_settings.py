from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable, IAnnotatable
from zope.interface import Interface, implements
from zope.component import adapts
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.formlib import form
from DateTime import DateTime
from persistent import Persistent
from zope.annotation import factory
from Products.ATContentTypes.interface.document import IATDocument
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from osha.smartprintpublication.interfaces import IOshaSmartprintSettings
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

smartprint_adapter_document = factory(OshaSmartprintSettings)

class OshaSmartprintSettingsForm(form.PageEditForm):
    form_fields = form.Fields(IOshaSmartprintSettings)
    label = u"Please specify the details for the publication"
    form_fields['path'].custom_widget = UberSelectionWidget

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        print "data:", data
        settings = IOshaSmartprintSettings(self.context)
        settings.path = data['path']
        settings.issue = data['issue']

        status = _("Updated on ${date_time}",
                   mapping={'date_time': DateTime()}
                   )
        self.status = status