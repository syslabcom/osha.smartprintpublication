from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName

from osha.smartprintpublication.config import PUBLICATION_DOCUMENT_REFERENCE

class AdditionalPublicationInfo(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, *arg, **kw):
        ann = IAnnotations(self.context)
        uid = ann.get(PUBLICATION_DOCUMENT_REFERENCE, None)
        if uid:
            cat = getToolByName(self.context, 'portal_catalog')
            res = cat(UID=uid)
            if res:
                ob = res[0].getObject()
                if ob:
                    return "<div class='publicationLanguageBox'><a href='%(url)s'>" \
                        "Also available as HTML</a></div>" %dict(url=ob.absolute_url())
        return u""

