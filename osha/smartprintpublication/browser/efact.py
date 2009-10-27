
import os

from Globals import InitializeClass
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zopyx.smartprintng.plone.browser.pdf import PDFView
#from transformation import Transformer

cwd = os.path.dirname(os.path.abspath(__file__))

class EfactView(PDFView):
    """ Integration for E-facts """

    template = ViewPageTemplateFile('resources/efact_template.pt')
    local_resources = os.path.join(cwd, 'resources')
    transformations = ('makeImagesLocal',
                        'removeEmptyElements',
                        'removeInternalLinks',
                        'cleanupTables',
                      )

    def __call__(self, *args, **kw):
        self.kw = kw
        pdf_file = super(EfactView, self).__call__(*args, **kw)
        return file(pdf_file, 'rb').read()


    def getNumber(self):
        """ An external method / BrowserView might be hooked in here in the future.
            For now, we just look into the passed-in kw."""
        number = self.kw.get('number', '42')
        return number

InitializeClass(EfactView)


