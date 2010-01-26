from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from Products.PlacelessTranslationService import getTranslationService

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
                    portal_languages = getToolByName(self.context, 'portal_languages')
                    preflang = portal_languages.getPreferredLanguage()
                    ali = portal_languages.getAvailableLanguageInformation()
                    
                    translations = ob.getTranslations()
                    lang_codes = translations.keys()
                    lang_codes.sort()
                    links = list()
                    for lang in lang_codes:
                        trans = translations[lang][0]
                        url = trans.absolute_url()
                        # treat neutral as the site's default language
                        if lang == '':
                            lang = portal_languages.getDefaultLanguage()
                        name = ali.get(lang, {'native': lang})['native']
                        links.append( (name, url) )
                    
                    pts = getTranslationService()
                    label = pts.translate(domain="osha",
                        msgid=u'label_also_online',
                        context=self.context,
                        target_language=preflang,
                        default=u'Also available online')
                    text = """<div class='publicationLanguageBox'>%(label)s: """ %dict(label=label)
                    for link in links:
                        text +="""[<a href="%(url)s">%(name)s</a>] """ %dict(name=link[0], url=link[1])
                    text += "</div>"
                    return text
        return u""

