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
from osha.smartprintpublication.browser.widget import ReferenceURLWidget, DatePickerWidget
from datetime import date
from DateTime import DateTime
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
    publication_date = None
    existing_publication = ''
    subject = tuple()
    existing_translations = list()

smartprint_adapter_document = factory(OshaSmartprintSettings)

class OshaSmartprintSettingsForm(form.PageEditForm):
    form_fields = form.Fields(IOshaSmartprintSettings)
    label = u"Please specify the details for the publication"
    form_fields['path'].custom_widget = UberSelectionWidget
    form_fields['existing_publication'].custom_widget = ReferenceURLWidget
    form_fields['existing_translations'].custom_widget = ReferenceURLWidget
    form_fields['publication_date'].custom_widget = DatePickerWidget

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        if not self.context.isCanonical():
            can = self.context.getCanonical()
            self.status = u"ERROR: You are not working on the canonical version. Please go to the '%s' " \
                u"version at \n%s" %(can.Language(), can.absolute_url())
        else:
            settings = IOshaSmartprintSettings(self.context)
            settings.path = data['path']
            settings.publication_date = data['publication_date']
            settings.issue = data['issue']
            settings.subject = data['subject']
            
            msg = self.handlePDFCreation(settings)
            self.status = "\n".join(msg)


    def handlePDFCreation(self, settings):
        status = list()
        transUIDs = list()
        
        path = settings.path
        if path.startswith('/'):
            path = path[1:]
        dest = self.context.restrictedTraverse(path, None)
        if not dest:
            status.append(u"ERROR: destination folder not found!")
            return status

        canLang = self.context.Language()

        msg, baseFile = self.createPDF(settings, dest, self.context)
        status.append(msg)
        if not baseFile:
            status.append(u"ERROR: publication could not be created")
            return status
        settings.existing_publication = baseFile.UID()

        #import pdb; pdb.set_trace()
        translations = self.context.getTranslations()
        if len(translations)>1 and baseFile.Language()!=canLang:
            baseFile.setLanguage(canLang)

        transaction.commit()
        for lang in translations.keys():
            if lang == canLang:
                continue
            msg, uid = self.createTranslatedPDF(settings, translations[lang][0], lang, baseFile)
            status.append(msg)
            if not uid:
                status.append(u"ERROR: translated version of the publication could not be created")
                return status
            transUIDs.append(uid)
            transaction.commit()
        settings.existing_translations = transUIDs
        
        return status


    def createPDF(self, settings, dest, context):
        asPDF = context.restrictedTraverse('asPDF', None)
        if not asPDF:
            # sth bad has happened
            return (u"ERROR: could not find BrowserView for creating a PDF", None)
        rawPDF = asPDF(number=settings.issue, plainfile=True)

        filename = "%s.pdf" %context.getId()
        verb ="Updated"
        if not getattr(Acquisition.aq_base(dest), filename, None):
            dest.invokeFactory(type_name="File", id=filename)
            transaction.commit()
            verb="Added"
        newFile = getattr(dest, filename)
        newFile.unmarkCreationFlag()
        newFile.processForm(values=dict(id=filename, title=context.Title()))
        newFile.setFile(rawPDF)
        newFile.setSubject(settings.subject)
        if isinstance(settings.publication_date, date):
            newFile.setEffectiveDate(DateTime(settings.publication_date.isoformat()))
        return (u"%(verb)s publication at %(url)s" %dict(verb=verb, url=newFile.absolute_url()), newFile)


    def createTranslatedPDF(self, settings, context, lang, baseFile):
        asPDF = context.restrictedTraverse('asPDF', None)
        if not asPDF:
            # sth bad has happened
            return (u"ERROR: could not find BrowserView for creating a PDF", None)
        rawPDF = asPDF(number=settings.issue, plainfile=True)

        verb = "Updated"
        if not baseFile.getTranslation(lang):
            baseFile.addTranslation(lang)
            transaction.commit()
            verb="Added"
        transFile = baseFile.getTranslation(lang)
        transFile.unmarkCreationFlag()
        filename = transFile.getId()
        transFile.processForm(values=dict(id=filename, title=context.Title()))
        transFile.setFile(rawPDF)
        if isinstance(settings.publication_date, date):
            transFile.setEffectiveDate(DateTime(settings.publication_date.isoformat()))

        return (u"%(verb)s translated publication in language '%(lang)s' at %(path)s" %dict(verb=verb, lang=lang, path=transFile.absolute_url()),
            transFile.UID())
  