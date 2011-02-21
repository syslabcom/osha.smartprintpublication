from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '0.5.2dev'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )


setup(name='osha.smartprintpublication',
      version=version,
      description="Integrationn of zopyx.smartprintng.plone with OSHA portal and slc.publications",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        ],
      keywords='web zope plone smartprintng publications osha',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='http://www.syslab.com/',
      license='GPL + EUPL',
      packages = ['osha', 'osha/smartprintpublication'],
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'slc.publications',
          'zopyx.smartprintng.plone',
          'osha.policy',
          'osha.theme',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
