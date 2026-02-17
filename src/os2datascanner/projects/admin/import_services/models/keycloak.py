# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from ...adminapp.aescipher import encrypt, decrypt  # Suggestion: move to core?


class KeycloakServer(models.Model):
    """TODO:"""
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )
    url = models.URLField(
        verbose_name=_('server URL'),
    )

    # TODO: Consider need for specific clients (we currently use one universally)?
    #        if so: add requests for client settings AND retrieval of secret
    #       NB! client refers to a client in Keycloak, NOT a core.Client instance
    #        in the datascanner system
    # Initialization vector for decryption
    _iv = models.BinaryField(
        db_column='iv',
        max_length=32,
        blank=True,
        null=False,
        verbose_name='initialization vector',
    )

    # Encrypted secret
    _ciphertext = models.BinaryField(
        db_column='ciphertext',
        max_length=1024,
        blank=True,
        null=False,
        verbose_name='cipher text',
    )

    @property
    def secret(self):
        return decrypt(self._iv, bytes(self._ciphertext))

    @secret.setter
    def secret(self, value):
        self._iv, self._ciphertext = encrypt(value)

    class Meta:
        verbose_name = _('Keycloak server')
        verbose_name_plural = _('Keycloak servers')
