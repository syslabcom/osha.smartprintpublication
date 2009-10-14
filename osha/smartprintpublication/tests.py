import unittest
import interlude
import zope.testing
import zope.component
from zope.app.testing import setup

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ptc.setupPloneSite(extension_profiles=['osha.smartprintpublication:default'],)

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(test):
            pass

        @classmethod
        def tearDown(test):
            setup.placefulTearDown()

optionflags = (zope.testing.doctest.REPORT_ONLY_FIRST_FAILURE |
               zope.testing.doctest.ELLIPSIS | 
               zope.testing.doctest.NORMALIZE_WHITESPACE
               )

def test_suite():
    return unittest.TestSuite((
        ztc.FunctionalDocFileSuite(
            'README.txt', 
            package='osha.smartprintpublication',
            test_class=TestCase, 
            globs=dict(interact=interlude.interact),
            optionflags=optionflags
            ),

        ))

