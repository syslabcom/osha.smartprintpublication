from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface, implements
from zope.component import adapts
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.formlib import form
from persistent import Persistent
from zope.annotation import factory
from Products.ATContentTypes.interface.document import IATDocument
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from Products.statusmessages.interfaces import IStatusMessage
import Acquisition
import transaction

from osha.smartprintpublication.interfaces import IOshaSmartprintSettings
from osha.smartprintpublication.browser.widget import ReferenceURLWidget, DatePickerWidget
from datetime import date
from DateTime import DateTime
from osha.theme import OSHAMessageFactory as _

from osha.smartprintpublication.config import PUBLICATION_DOCUMENT_REFERENCE

class OshaSmartprintSettings(Persistent):
    """ stores its properties via Annotaions on the context """
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
        # only allow the action on a canonical object
        status = IStatusMessage(self.request)
        if not self.context.isCanonical():
            can = self.context.getCanonical()
            status.addStatusMessage(u"ERROR: You are not working on the canonical version. Please go to the '%s' " \
                u"version at \n%s" %(can.Language(), can.absolute_url()), type="error")
        else:
            settings = IOshaSmartprintSettings(self.context)
            path = data['path']
            settings.publication_date = data['publication_date']
            settings.issue = data['issue']
            
            self.handlePDFCreation(settings, path, status)
            #self.status = "\n".join(msg)


    def handlePDFCreation(self, settings, path, status):
        #status = list()
        transUIDs = list()
        
        # flag that indicates whether the path to the destination folder has changed
        path_has_changed = False
        if path!=settings.path:
            path_has_changed = True
        
        relpath = path
        if relpath.startswith('/'):
            relpath = relpath[1:]
        dest = self.context.restrictedTraverse(relpath, None)
        if not dest:
            status.addStatusMessage(u"Destination folder not found!", type="error")
            return

        # create the canonical publication
        setattr(settings, 'subject', self.context.Subject())
        # setattr(settings, 'subcategory', self.context.getSubcategory())
        setattr(settings, 'nace', self.context.getNace())
        setattr(settings, 'multilingual_thesaurus', self.context.getMultilingual_thesaurus())
        baseFile = self.createPDF(settings, dest, self.context, path_has_changed, status)
        #status.append(msg)
        if not baseFile:
            status.addStatusMessage(u"Publication could not be created", type="error")
            return
        # creating the canonical version went ok, so now we can persist the path
        settings.path = path
        
        # if the document has translations, make sure the canonical publication has a language
        canLang = self.context.Language()
        translations = self.context.getTranslations()
        if len(translations)>1 and baseFile.Language()!=canLang:
            baseFile.setLanguage(canLang)

        transaction.commit()

        # create a publication for every translation
        for lang in translations.keys():
            if lang == canLang:
                continue
            uid = self.createTranslatedPDF(settings, translations[lang][0], lang, baseFile, status)
            #status.append(msg)
            if not uid:
                status.addStatusMessage(u"Translated version of the publication could not be created", type="error")
                return
            transUIDs.append(uid)
            transaction.commit()
        # persist the UIDs of all translations
        settings.existing_translations = transUIDs
        
        return


    def createPDF(self, settings, dest, context, path_has_changed, status):
        asPDF = context.restrictedTraverse('asEfact', None)
        if not asPDF:
            # sth bad has happened
            status.addStatusMessage(u"Could not find BrowserView for creating a PDF", type="error")
            return None
        try:
            rawPDF = asPDF(number=settings.issue)
            rawPDF = file(rawPDF, 'rb').read()
        except:
            status.addStatusMessage(u"Creating a PDF file failed. Please check connection to SmartPrintNG server", type="error")
            return None


        filename = "%s.pdf" %settings.issue
        # If no UID of a publication exists yet, or if the destination folder has changed, create a new file
        if not settings.existing_publication or path_has_changed:
            # If an object with the given filename already exists at the destination folder, return an error
            if getattr(Acquisition.aq_base(dest), filename, None):
                obj = getattr(dest, filename)
                status.addStatusMessage(u"An object of type %(type)s already exists at %(path)s, but is not connected " \
                 "to this document. Please remove it first or change the document's short name (id)" %dict(
                    type=type(Acquisition.aq_base(obj)), path=obj.absolute_url()), type="warning")
                return None
            dest.invokeFactory(type_name="File", id=filename)
            transaction.commit()
            newFile = getattr(dest, filename)
            newFile.unmarkCreationFlag()
            settings.existing_publication = newFile.UID()
            isNew=True

        # Retrieve the publication from the catalog by its UID
        else:
            catalog = getToolByName(context, 'portal_catalog')
            brains = catalog(UID=settings.existing_publication)
            if not len(brains):
                status.addStatusMessage(u"Existing Publication could not be retrieved", type="error")
                return None
            newFile = brains[0].getObject()
            if not newFile:
                status.addStatusMessage(u"Reference to exiting Publication is broken", type="error")
                return None
            isNew=False
        newFile.processForm(values=dict(id=filename, title=context.Title(),
            description=context.Description()))
        newFile.setFile(rawPDF)
        # setting Subject AND Subcategory shouldn't be necessary
        # But we don't know yet what the client prefers
        newFile.setSubject(settings.subject)
        # newFile.setSubcategory(settings.subcategory)
        newFile.setNace(settings.nace)
        newFile.setMultilingual_thesaurus(settings.multilingual_thesaurus)
        # set a link to the original document on the publication
        ann = IAnnotations(newFile)
        ann[PUBLICATION_DOCUMENT_REFERENCE] = context.UID()
        if isinstance(settings.publication_date, date):
            newFile.setEffectiveDate(DateTime(settings.publication_date.isoformat()))
        status.addStatusMessage(u"%(verb)s publication at %(url)s" %dict(
            verb=isNew and 'Added' or 'Updated', url=newFile.absolute_url()), type="info")
        return newFile


    def createTranslatedPDF(self, settings, context, lang, baseFile, status):
        asPDF = context.restrictedTraverse('asEfact', None)
        if not asPDF:
            # sth bad has happened
            status.addStatusMessage(u"Could not find BrowserView for creating a PDF", type="error")
            return None
        try:
            rawPDF = asPDF(number=settings.issue)
            rawPDF = file(rawPDF, 'rb').read()
        except:
            status.addStatusMessage(u"Creating a PDF file failed. Please check connection to SmartPrintNG server", type="error")
            return None

        isNew=False
        # Create a translation if not present
        if not baseFile.getTranslation(lang):
            baseFile.addTranslation(lang)
            transaction.commit()
            isNew=True
        transFile = baseFile.getTranslation(lang)
        if isNew:
            transFile.unmarkCreationFlag()
        filename = transFile.getId()
        # Update the translation
        transFile.processForm(values=dict(id=filename, title=context.Title(),
            description=context.Description()))
        transFile.setFile(rawPDF)
        if isinstance(settings.publication_date, date):
            transFile.setEffectiveDate(DateTime(settings.publication_date.isoformat()))

        # set a link to the original translated document on the publication
        ann = IAnnotations(transFile)
        ann[PUBLICATION_DOCUMENT_REFERENCE] = context.UID()
        status.addStatusMessage(u"%(verb)s translated publication in language '%(lang)s' at %(path)s" %dict(
            verb=isNew and 'Added' or 'Updated', lang=lang, path=transFile.absolute_url()), type="info")
        return transFile.UID()
  