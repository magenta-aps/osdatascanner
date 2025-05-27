from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.model.utilities import sitemap
from os2datascanner.projects.shared.forms import GroupingModelForm

from ..models.scannerjobs.webscanner import WebScanner


class WebScannerForm(GroupingModelForm):
    # By default django.forms validates fields in the order in which they're
    # defined in the model class. If you want to force some fields to be
    # evaluated in a particular order (here, for example, our validation logic
    # needs "download_sitemap" to be validated and available /before/ we check
    # "sitemap_url"), you can do that here
    field_order = ["download_sitemap", "sitemap_url", "sitemap"]

    placeholders = {
        "url": _("e.g. https://example.com/"),
        "sitemap_url": _("e.g. https://example.com/sitemap.xml"),
    }

    patterns = {
        "url": "(http|https)://.*"
    }

    groups = (
        (
            _("General settings"),
            ["name", "organization", "validation_status", "contacts"]
        ),
        (
            _("Web crawler settings"),
            ["url", "download_sitemap", "sitemap_url", "sitemap",
             "always_crawl"]
        ),
        (
            _("Advanced web crawler settings"),
            ["extended_hints", "reduce_communication"]
        ),
        (
            _("Scan settings"),
            ["do_last_modified_check", "do_ocr", "rule", "exclusion_rule"]
        ),
        (
            _("Result settings"),
            ["contacts", "only_notify_superadmin", "keep_false_positives"]
        ),
        (
            _("Scheduled execution settings"),
            ["schedule"],
        ),
    )

    def clean_sitemap_url(self):
        sitemap_url = self.cleaned_data["sitemap_url"]
        download_sitemap = self.cleaned_data["download_sitemap"]
        if sitemap_url:
            try:
                # All we want to do here is to check that process_sitemap_url
                # can yield a single link without raising an exception
                for _k in sitemap.process_sitemap_url(sitemap_url):
                    break
            except sitemap.SitemapMissingError:
                self.add_error(
                        "sitemap_url",
                        [_("Couldn't find a sitemap here")])
            except sitemap.SitemapMalformedError:
                self.add_error(
                        "sitemap_url",
                        [_("This appears not to be a sitemap")])
        elif download_sitemap:
            self.add_error(
                    "sitemap_url",
                    [_("Sitemap download requested, but no URL was given")])
        return sitemap_url

    class Meta:
        model = WebScanner
        exclude = ("pk", "dtstart", "validation_method",)
        widgets = {
            # "name": widgets.PasswordInput(),
        }
