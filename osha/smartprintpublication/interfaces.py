from zope import schema
from zope.interface import Interface
from plone.app.vocabularies.catalog import SearchableTextSource, SearchableTextSourceBinder
from slc.publications.interfaces import IPublicationContainerEnhanced

from osha.theme import OSHAMessageFactory as _


class IOshaSmartprintSettings(Interface):
    """Settings needed to turn a document into a publication"""
    path = schema.Choice(title=_(u'Path'),
                        description=_(u'Specify the path where the file should be created / updated'),
                        required=True,
                        #value_type=schema.Choice(
                         #   title=u"Add documents for referencing",
                            source=SearchableTextSourceBinder
                            (
                                query={'object_provides':IPublicationContainerEnhanced.__identifier__},
                                default_query='path:/en/publications'
                            )
                        #)
                    )

    issue = schema.ASCIILine(title=_(u'Issue'),
                        description=_(u"State the publication's issue or number"),
                        default='',
                        required=True)

