from zope.component import getMultiAdapter
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from types import StringType, UnicodeType

class ReferenceURLWidget(SimpleInputWidget):

    __call__ = ViewPageTemplateFile('widget.pt')


    def _getFormValue(self):
        """Returns a value suitable for use in an HTML form.

        Detects the status of the widget and selects either the input value
        that came from the request, the value from the _data attribute or the
        default value.
        """
        input_value = list()
        pc = getToolByName(self.context.context, 'portal_catalog')
        data = self._data
        if not data:
            return input_value
        if isinstance(data, StringType) or isinstance(data, UnicodeType):
            data = [data]
        for uid in data:
            brains = pc(UID=uid)

            if len(brains):
                b = brains[0]
                if b is not None:
                    input_value.append((b.getURL(), getattr(b, 'Language', '')))

        return input_value


    def hasInput(self):
        return (self.name + '.marker') in self.request.form

