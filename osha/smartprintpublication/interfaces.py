from zope import schema
from zope.interface import Interface
from plone.app.vocabularies.catalog import SearchableTextSource, SearchableTextSourceBinder
from slc.publications.interfaces import IPublicationContainerEnhanced

from osha.theme import OSHAMessageFactory as _


class IOshaSmartprintSettings(Interface):
    """Settings needed to turn a document into a publication"""

    issue = schema.ASCIILine(title=_(u'Issue'),
                        description=_(u"State the publication's issue or number. It will appear as part of the Publication's header."),
                        default='',
                        required=True)

    publication_date = schema.Date(title=_(u'Publication date'),
                        description=_(u'Set the official publication date here'),
                        required=False,
            )

    existing_publication = schema.ASCIILine(title=_(u'Existing publication'),
                        description=_(u"If present, shows the path of the Publication associated with this document. "
                          "If you submit this form again and don't change the destination folder below, this existing "
                          "Publication will be overwritten with the current version of the documents and the metadata settings done here"),
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

    path = schema.Choice(title=_(u'Destination'),
                        description=_(u'Specify the destination folder where the Publication should be created / updated. \n'
                        'WARNING: if a Publication is alreay conncted to this document and you change the destination, the existing Publication will to longer be connected. It will be replaced by a newly created Publication in the new location.'),
                        required=True,
                            source=SearchableTextSourceBinder
                            (
                                query={'object_provides':IPublicationContainerEnhanced.__identifier__},
                                default_query='path:/en/publications'
                            )
                    )

    subject = schema.Tuple(title=_(u'Keywords'),
                            description=_('Select one or more keywords applicbale to this Publication'),
                            default=tuple(),
                            required=False,
                            value_type=schema.Choice(
                                vocabulary="osha.policy.vocabularies.categories",
                            )
            )

