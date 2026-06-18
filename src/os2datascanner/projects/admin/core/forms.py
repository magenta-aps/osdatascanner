# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from typing import override

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Client
from .models.client import Scan
from .utils import clear_import_services


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        # `scans` is rendered through the custom activated_scan_types field below.
        exclude = ('scans',)

    activated_scan_types = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=Scan.choices(),
        label=_('activated scan types').capitalize(),
        help_text=_('Select a scan type to activate it for this client.'),
        required=False,  # Allow none selected to 'deactivate' a client
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs.update(
                initial={'activated_scan_types': instance.activated_scan_types.selected_list}
            )
        super().__init__(*args, **kwargs)

    def clean_activated_scan_types(self):
        selected = self.cleaned_data['activated_scan_types']
        self.instance.scans = sum([int(x) for x in selected])
        return selected

    @override
    def save(self, commit=True):
        # Switching import source invalidates any existing per-organization import
        # configuration, so clear it before persisting the new source.
        if self.instance.pk:
            old_source = Client.objects.get(pk=self.instance.pk).import_source
            if old_source != self.cleaned_data['import_source']:
                clear_import_services(self.instance)
        return super().save(commit=commit)
