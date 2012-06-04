Introduction
============

This product makes use of zopyx.smartprintng.server to create a PDF file from a
normal Document. This file is then saved in Plone again as a Publication (slc.publications).

Translations of a document are created as translations of the publication.

The main element is a form (BrowserView) that sends the necessary parameters to the PDF
generation and stores them per Annotations on the document.


Test browser boilerplate
========================

First, we must perform some setup.

    >>> from plone.testing.z2 import Browser
    >>> browser = Browser(layer['app'])
    >>> portal = layer['portal']
    >>> portal_url = portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in.

    >>> browser.open(portal_url  + '/login_form')

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = 'admin'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True

    >>> browser.open(portal_url)


Actual testing
==============

    First we add a folder for our documents
    >>> browser.getLink(url='createObject?type_name=Folder').click()
    >>> browser.getControl(name='title').value = 'Documents'
    >>> browser.getControl('Save').click()
    >>> "Changes saved" in browser.contents
    True

    Now let's add our first document
    >>> browser.getLink(url='createObject?type_name=Document').click()
    >>> browser.getControl(name='title').value = 'My doc'
    >>> browser.getControl(name='text').value = 'This is the text'
    >>> browser.getControl('Save').click()
    >>> "Changes saved" in browser.contents
    True

    >>> browser.url == portal_url + '/documents/my-doc'
    True

    >>> browser.open(browser.url + '/@@publishAsPDF')
    >>> 'Create a Publication (PDF) from this document' in browser.contents
    True


    Ok, we got the form...
    For the moment we're happy, because we cannot test the connection to the SmartPrintNG server.


    This is how we can take a look at the actual browser contents:
    >>> # file('/tmp/bla.html', 'w').write(browser.contents);import webbrowser;webbrowser.open('file:///tmp/bla.html')
