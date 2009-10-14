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
    label = u"Create a Publication (PDF) from this document"
    description = u"""With this form you can create a Publication (plus translations) from a Document. Set the
    correct metadata and choose a destination folder where the Publication should be created.
    A PDF document will be generated for all translations of the document and saved as a Publication in the
    specified folder. The file name will be generated from the document's short name.
    If you change the original document or want to set other metadata via this form, you can always submit this form again.
    All existing publications (listed below) will be updated. NOTE: depending on the number of translations and the
    text length, it may take some until all actions are performed - be patient..."""
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
            path = data['path']
            settings.publication_date = data['publication_date']
            settings.issue = data['issue']
            settings.subject = data['subject']
            
            msg = self.handlePDFCreation(settings, path)
            self.status = "\n".join(msg)


    def handlePDFCreation(self, settings, path):
        status = list()
        transUIDs = list()
        
        path_has_changed = False
        if path!=settings.path:
            path_has_changed = True
        
        relpath = path
        if relpath.startswith('/'):
            relpath = relpath[1:]
        dest = self.context.restrictedTraverse(relpath, None)
        if not dest:
            status.append(u"ERROR: destination folder not found!")
            return status

        canLang = self.context.Language()

        msg, baseFile = self.createPDF(settings, dest, self.context, path_has_changed)
        status.append(msg)
        if not baseFile:
            status.append(u"ERROR: publication could not be created")
            return status
        # creating the canonical version went ok, so now we can persist the path
        settings.path = path
        
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


    def createPDF(self, settings, dest, context, path_has_changed):
        asPDF = context.restrictedTraverse('asPDF', None)
        if not asPDF:
            # sth bad has happened
            return (u"ERROR: could not find BrowserView for creating a PDF", None)
        rawPDF = asPDF(number=settings.issue, plainfile=True)

        filename = "%s.pdf" %context.getId()
        verb ="Updated"
        if not settings.existing_publication or path_has_changed:
            if getattr(Acquisition.aq_base(dest), filename, None):
                obj = getattr(dest, filename)
                return (u"ERROR: an object of type %(type)s already exists at %(path)s, but is not connected " \
                 "to this document. Please remove it first or change the document's short name (id)" %dict(
                    type=type(Acquisition.aq_base(obj)), path=obj.absolute_url()), None)
            dest.invokeFactory(type_name="File", id=filename)
            transaction.commit()
            verb="Added"
            newFile = getattr(dest, filename)
            newFile.unmarkCreationFlag()
            settings.existing_publication = newFile.UID()
        else:
            catalog = getToolByName(context, 'portal_catalog')
            brains = catalog(UID=settings.existing_publication)
            if not len(brains):
                return (u"ERROR: existing Publication could not be retrieved", None)
            newFile = brains[0].getObject()
            if not newFile:
                return (u"ERROR: reference to exiting Publication is broken", None)
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
  