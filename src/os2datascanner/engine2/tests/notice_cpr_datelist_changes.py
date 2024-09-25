import lxml.html
import datetime
import requests
import re

from os2datascanner.engine2.rules.utilities.cpr_probability import CPR_EXCEPTION_DATES


class TestNoticeCPRChanges:
    def test_is_exception_dates_up_to_date(self):
        """
        Compare our list of exception dates to the official list from the
        CPR Office.
        Last updated: 2024/09/23
        """
        def parsedate(s: str) -> datetime.date:
            """
            Quick-and-dirty parser for turning a year into a date, ie "1991" -> 1991 January 1st
            """
            year = s.strip()

            return datetime.date(int(year), 1, 1)

        r = requests.get(
            "https://cpr.dk/cpr-systemet/"
            "personnumre-uden-kontrolciffer-modulus-11-kontrol/"
        )

        r.raise_for_status()

        doc = lxml.html.document_fromstring(r.text)

        dates = {
            parsedate(cell.text_content())
            for cell in doc.findall('*//*[@class="web-page"]//td')
            if cell.text.strip() and re.fullmatch(r"\d{4}", cell.text.strip())
        }

        assert dates == CPR_EXCEPTION_DATES
