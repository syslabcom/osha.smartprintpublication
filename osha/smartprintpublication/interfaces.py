from zope import schema
from zope.interface import Interface
from plone.app.vocabularies.catalog import SearchableTextSource, SearchableTextSourceBinder
from slc.publications.interfaces import IPublicationContainerEnhanced

from osha.theme import OSHAMessageFactory as _


class IOshaSmartprintSettings(Interface):
    """Settings needed to turn a document into a publication"""

    issue = schema.ASCIILine(title=_(u'Issue'),
                        description=_(u"State the publication's issue or number"),
                        default='',
                        required=True)

    existing_publication = schema.ASCIILine(title=_(u'Existing publication'),
                        description=_(u'If present, shows the path of the Publication associated with this document. '
                          'It will be overwritten'),
                          required=False,
                          readonly=True,
            )
    existing_translations = schema.List(title=_('Existing translations'),
                                        description=_(u'If present, shows the paths of all translations of the '
                                        'Publication associated with this document.'),
                                        required=False,
                                        readonly=True,
                                        default=list(),
                                        value_type=schema.ASCIILine(),
            )

    path = schema.Choice(title=_(u'Path'),
                        description=_(u'Specify the path where the file should be created / updated'),
                        required=True,
                            source=SearchableTextSourceBinder
                            (
                                query={'object_provides':IPublicationContainerEnhanced.__identifier__},
                                default_query='path:/en/publications'
                            )
                    )

    subject = schema.Tuple(title=_(u'Keywords'),
                            description=_('Select one or more keywords applicbale to this publication'),
                            default=tuple(),
                            required=False,
                            value_type=schema.Choice(
                                vocabulary="osha.policy.vocabularies.categories",
                            )
            )

