import os

from Globals import InitializeClass
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zopyx.smartprintng.plone.browser.pdf import ProducePublishView
#from transformation import Transformer

cwd = os.path.dirname(os.path.abspath(__file__))


class EfactView(ProducePublishView):
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
        return pdf_file

    def getNumber(self):
        """ An external method / BrowserView might be hooked in here in
        the future. For now, we just look into the passed-in kw.
        """
        number = self.kw.get('number', '42')
        return number

InitializeClass(EfactView)


class EfactDownloadView(EfactView):
    """ Direct PDF download """

    def __call__(self, *args, **kw):
        pdf_file = super(EfactDownloadView, self).__call__(*args, **kw)

        # return PDF over HTTP
        R = self.request.response
        R.setHeader('content-type', 'application/pdf')
        R.setHeader('content-disposition',
                    'attachment; filename=%s.pdf' % self.context.getId())
        R.setHeader('content-length', os.stat(pdf_file)[6])
        R.setHeader('pragma', 'no-cache')
        R.setHeader('cache-control', 'no-cache')
        R.setHeader('Expires', 'Fri, 30 Oct 1998 14:19:41 GMT')
        R.setHeader('content-length', os.stat(pdf_file)[6])
        return file(pdf_file, 'rb').read()

InitializeClass(EfactDownloadView)
