# -*- coding: UTF-8 -*-
# encoding: utf-8
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
# OS2Webscanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (http://www.os2web.dk/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( http://www.os2web.dk/ )

from django.db import models


from os2datascanner.engine2.rules.cpr import CPRRule as CPRTwule
from os2datascanner.engine2.rules.experimental.cpr import TurboCPRRule as TurboCPRTwule
from .rule import Rule


class CPRRule(Rule):
    do_modulus11 = models.BooleanField(
            default=False, verbose_name='Tjek modulus-11')
    ignore_irrelevant = models.BooleanField(
            default=False, verbose_name='Ignorer ugyldige fødselsdatoer')
    examine_context = models.BooleanField(
            default=False, verbose_name='Tjek kontekst omkring match')

    def make_engine2_rule(self):
        return CPRTwule(
                modulus_11=self.do_modulus11,
                ignore_irrelevant=self.ignore_irrelevant,
                examine_context=self.examine_context,
                name=self.name,
                sensitivity=self.make_engine2_sensitivity())

    whitelist = models.TextField(blank=True,
                                 default="",
                                 verbose_name='Godkendte CPR-numre')


class TurboCPRRule(Rule):
    do_modulus11 = models.BooleanField(
            default=False, verbose_name='Tjek modulus-11')
    examine_context = models.BooleanField(
            default=False, verbose_name='Tjek kontekst omkring match')

    def make_engine2_rule(self):
        return TurboCPRTwule(
            modulus_11=self.do_modulus11,
            examine_context=self.examine_context,
            name=self.name,
            sensitivity=self.make_engine2_sensitivity())
