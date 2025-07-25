# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView

from ..validate import get_validation_str
from .scanner_views import (
    ScannerBase,
    ScannerUpdate,
    ScannerCopy,
    ScannerCreate,
    ScannerList,
    ScannerViewType)
from ..forms.webscanner import WebScannerForm
from ..models.scannerjobs.webscanner import WebScanner


def url_contains_spaces(form):
    return form['url'].value() and ' ' in form['url'].value()


class WebScannerList(ScannerList):
    """Displays list of web scanners."""

    model = WebScanner
    type = 'web'


web_scanner_fields = [
    'url',
    'download_sitemap',
    'sitemap_url',
    'sitemap',
    'do_link_check',
    'exclude_urls',
    'reduce_communication',
    'always_crawl',
]


class WebScannerCreateDF(CreateView):
    scanner_view_type = ScannerViewType.CREATE

    model = WebScanner
    form_class = WebScannerForm
    template_name = "components/forms/grouping_model_form_wrapper.html"


class WebScannerCreate(ScannerCreate):
    """Web scanner create form."""

    model = WebScanner
    type = 'web'
    fields = ScannerBase.fields + web_scanner_fields

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)

        form.fields['url'].widget.attrs['placeholder'] = \
            _('e.g. https://example.com')
        form.fields['exclude_urls'].widget.attrs['placeholder'] = \
            _('e.g. https://example.com/exclude1, https://example.com/exclude2')

        return form

    def form_valid(self, form):
        if url_contains_spaces(form):
            form.add_error('url', _(u'Space is not allowed in the web-domain name.'))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        """The URL to redirect to after successful creation."""
        return '/webscanners/%s/created/' % self.object.pk


class WebScannerCopy(ScannerCopy):
    """Create a new copy of an existing WebScanner"""

    model = WebScanner
    type = 'web'
    fields = ScannerBase.fields + web_scanner_fields


class WebScannerUpdate(ScannerUpdate):
    """Update a scanner view."""

    model = WebScanner
    type = 'web'
    fields = ScannerBase.fields + web_scanner_fields

    def form_valid(self, form):
        if url_contains_spaces(form):
            form.add_error('url', _(u'Space is not allowed in the web-domain name.'))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Get the context used when rendering the template."""
        context = super().get_context_data(**kwargs)
        for value, _desc in WebScanner.validation_method_choices:
            key = 'valid_txt_' + str(value)
            context[key] = get_validation_str(self.object, value)
        return context

    def get_success_url(self):
        """The URL to redirect to after successful updating.

        Will redirect the user to the validate view if the form was submitted
        with the 'save_and_validate' button.
        """
        if 'save_and_validate' in self.request.POST:
            return 'validate/'
        else:
            return '/webscanners/%s/saved/' % self.object.pk
