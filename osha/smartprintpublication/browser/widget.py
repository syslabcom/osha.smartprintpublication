from zope.component import getMultiAdapter
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class ReferenceURLWidget(SimpleInputWidget):

    __call__ = ViewPageTemplateFile('widget.pt')


    def _getFormValue(self):
        """Returns a value suitable for use in an HTML form.

        Detects the status of the widget and selects either the input value
        that came from the request, the value from the _data attribute or the
        default value.
        """
        input_value = ''
        if not self._data:
            return input_value
        pc = getToolByName(self.context.context, 'portal_catalog')
        brains = pc(UID=self._data)

        for b in brains:
            if b is not None:
                return b.getURL()

        return input_value


    def hasInput(self):
        return (self.name + '.marker') in self.request.form

