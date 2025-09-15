import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2 import factory
from os2datascanner.engine2.model.utilities import sitemap

from ..models.scannerjobs.webscanner import WebScanner
from .shared import Groups, ScannerForm


class WebScannerForm(ScannerForm):
    # By default django.forms validates fields in the order in which they're
    # defined in the model class. If you want to force some fields to be
    # evaluated in a particular order (here, for example, our validation logic
    # needs "download_sitemap" to be validated and available /before/ we check
    # "sitemap_url"), you can do that here
    field_order = ["url", "download_sitemap", "sitemap_url", "sitemap"]

    placeholders = {
        "url": _("e.g. https://example.com/"),
        "sitemap_url": _("e.g. https://example.com/sitemap.xml"),
    }

    patterns = {
        "url": "(http|https)://.*"
    }

    groups = (
        Groups.GENERAL_SETTINGS,
        (
            _("Web crawler settings"),
            [
                "url",
                "download_sitemap",
                "sitemap_url",
                "sitemap",
                "always_crawl",
                (
                    _("Advanced web crawler settings"),
                    ["reduce_communication"]
                )
            ]
        ),
        (
            _("Scan settings"),
            ["do_last_modified_check", "do_ocr", "rule", "exclusion_rule",
                (
                    _("Web scan settings"),
                    ["do_link_check", "exclude_urls"]
                )]
        ),
        Groups.ADVANCED_RESULT_SETTINGS,
        Groups.SCHEDULED_EXECUTION_SETTINGS,
    )

    def clean_sitemap_url(self):
        sitemap_url = self.cleaned_data["sitemap_url"]
        download_sitemap = self.cleaned_data["download_sitemap"]
        if self.has_error("url") or "url" not in self.cleaned_data:
            # We need the URL field to be populated to be able to do validation
            # here, so just give up if it isn't
            return sitemap_url
        else:
            url = self.cleaned_data["url"]

        if sitemap_url:
            try:
                # All we want to do here is to check that process_sitemap_url
                # can yield a single link without raising an exception
                for _k in sitemap.process_sitemap_url(
                        urljoin(url, sitemap_url),
                        context=factory.make_session()):
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

    def clean_sitemap(self):
        sitemap = self.cleaned_data["sitemap"]
        if not sitemap:
            return sitemap
        try:
            ET.parse(sitemap)
        except Exception as e:
            self.add_error(
                "sitemap",
                [_("Error parsing sitemap: {0}").format(e)]
            )
        return sitemap

    class Meta:
        model = WebScanner
        exclude = ("pk", "dtstart", "validation_method",)
        widgets = {
            # "name": widgets.PasswordInput(),
        }
