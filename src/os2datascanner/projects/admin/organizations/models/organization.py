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
from django import forms
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from os2datascanner.core_organizational_structure.models import \
    OrganizationSerializer as Core_OrganizationSerializer
from .broadcasted_mixin import Broadcasted
from os2datascanner.projects.admin.adminapp.models.rules import Rule


from os2datascanner.core_organizational_structure.models import Organization as Core_Organization

# Codes sourced from https://www.thesauruslex.com/typo/eng/enghtml.htm
char_dict = {
        "Æ": "&AElig;",
        "Ø": "&Oslash;",
        "Å": "&Aring;",
        "æ": "&aelig;",
        "ø": "&oslash;",
        "å": "&aring;",
        }


def replace_nordics(name: str):
    """ Replaces 'æ', 'ø' and 'å' with '&aelig', '&oslash' and '&aring.'"""
    global char_dict
    for char in char_dict:
        name = name.replace(char, char_dict[char])
    return name


class HourField(models.TimeField):
    """ Allow the user to pick time of day in the format HH:MM. """

    def formfield(self, **kwargs):
        kwargs['widget'] = forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'step': '3600'})
        return super().formfield(**kwargs)


@Broadcasted.register
class Organization(Core_Organization):
    """ Core logic lives in the core_organizational_structure app.
        Additional specific logic can be implemented here. """

    client = models.ForeignKey(
        'core.Client',
        on_delete=models.CASCADE,
        related_name='organizations',
        verbose_name=_('client'),
    )
    slug = models.SlugField(
        max_length=256,
        allow_unicode=True,
        unique=True,
        verbose_name=_('slug'),
    )
    system_rules = models.ManyToManyField(
        Rule,
        related_name='organizations',
        verbose_name=_('system rules'),
    )
    synchronization_time = HourField(
        default="17:00",
        verbose_name=_('synchronization time'),
    )

    @staticmethod
    def convert_name_to_slug(name: str) -> str:
        """Converts Organization name to slug"""
        encoded_name = replace_nordics(name)
        return slugify(encoded_name, allow_unicode=True)

    def save(self, *args, **kwargs):
        self.slug = self.convert_name_to_slug(self.name)
        return super().save(*args, **kwargs)

    @property
    def scanners_running(self) -> bool:
        from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import ScanStatus
        org_scanners = self.scannerjobs.all()
        scanners_running = ScanStatus.objects.exclude(
                ScanStatus._completed_or_cancelled_Q).filter(
                    scanner_id__in=org_scanners)
        return scanners_running.exists()


class OrganizationSerializer(Core_OrganizationSerializer):
    class Meta(Core_OrganizationSerializer.Meta):
        model = Organization


Organization.serializer_class = OrganizationSerializer
