from zope.component import getMultiAdapter
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from types import StringType, UnicodeType
import datetime
import time
from Products.CMFPlone.i18nl10n import monthname_english

class ReferenceURLWidget(SimpleInputWidget):

    __call__ = ViewPageTemplateFile('referenceurlwidget.pt')


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


class DatePickerWidget(SimpleInputWidget):

    __call__ = ViewPageTemplateFile('datepickerwidget.pt')

    def _getFormInput(self):
        year = self.request.get(self.name + '_year')
        try:
            year = int(year)
        except:
            return None
        month = self.request.get(self.name + '_month')
        try:
            month = int(month)
        except:
            return None
        day = self.request.get(self.name + '_day')
        try:
            day = int(day)
        except:
            return None
        #import pdb; pdb.set_trace()
        return datetime.date(year, month, day)

    def getYearRange(self):
        year = datetime.date.fromtimestamp(time.time()).year
        return range(year-7, year+2)

    def getMonthRange(self):
        return [dict(val=i, name=monthname_english(i)) for i in range(1,13)]

    def getYear(self):
        #return ""
        return isinstance(self._data, datetime.date) and self._data.year or ''
    
    def getMonth(self):
        #return ""
        return isinstance(self._data, datetime.date) and self._data.month or ''
    
    def getDay(self):
        #return ""
        return isinstance(self._data, datetime.date) and self._data.day or ''


    def hasInput(self):
        return (self.name + '.marker') in self.request.form