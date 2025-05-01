import pytest

from os2datascanner.engine2.commands.utils import DemoSourceUtility as TestSourceUtility
from os2datascanner.engine2.model.data import DataSource
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.model.http import SecureWebSource, WebSource
from os2datascanner.engine2.model.smbc import SMBCSource


class TestURL:
    @pytest.mark.parametrize("source,url", [
        (FilesystemSource("/usr"), "file:///usr"),
        (
            SMBCSource("//10.0.0.30/Share$/Documents"),
            "smbc://10.0.0.30/Share%24/Documents",
        ),
        (
            SMBCSource("//10.0.0.30/Share$/Documents", "FaithfullA"),
            "smbc://FaithfullA@10.0.0.30/Share%24/Documents",
        ),
        (
            SMBCSource(
                "//10.0.0.30/Share$/Documents",
                "FaithfullA",
                "secretpassword",
            ),
            "smbc://FaithfullA:secretpassword@10.0.0.30/Share%24/Documents",
        ),
        (
            SMBCSource(
                "//10.0.0.30/Share$/Documents",
                "FaithfullA",
                "secretpassword",
                "SYSGRP",
            ),
            "smbc://SYSGRP;FaithfullA:secretpassword@10.0.0.30/Share%24"
            "/Documents",
        ),
        (
            SMBCSource(
                "//10.0.0.30/Share$/Documents",
                "FaithfullA",
                None,
                "SYSGRP",
            ),
            "smbc://SYSGRP;FaithfullA@10.0.0.30/Share%24/Documents",
        ),
        (
            SMBCSource(
                "//INT-SRV-01/Q$",
                "FaithfullA",
                None,
                "SYSGRP",
            ),
            "smbc://SYSGRP;FaithfullA@INT-SRV-01/Q%24",
        ),
        (
            SMBCSource(
                "//INT-SRV-01.intern.vstkom.dk/Q$",
                "FaithfullA",
                "secretpassword",
                None,
            ),
            "smbc://intern.vstkom.dk;FaithfullA:secretpassword@INT-SRV-01.intern.vstkom.dk/Q%24",  # noqa
        ),
        (
            SMBCSource(
                "//INT-SRV-01.intern.vstkom.dk/Q$",
                "FaithfullA",
                "secretpassword",
                "SYSGRP",
            ),
            "smbc://SYSGRP;FaithfullA:secretpassword@INT-SRV-01.intern.vstkom.dk/Q%24",
        ),
        (
            SMBCSource(
                "//INT-SRV-01.intern.vstkom.dk/Q$",
                "FaithfullA",
                None,
                "",
            ),
            "smbc://FaithfullA@INT-SRV-01.intern.vstkom.dk/Q%24",
        ),
        # Remove trailing / on base url if present. / should be part of the path
        (WebSource("http://www.example.com/"), "http://www.example.com"),
        (
            SecureWebSource("https://www.example.com"),
            "https://www.example.com",
        ),
        (
            DataSource(b"This is a test", "text/plain"),
            "data:text/plain;base64,VGhpcyBpcyBhIHRlc3Q=",
        ),
    ])
    def test_sources(self, source, url):
        generated_url = TestSourceUtility.to_url(source)
        assert url == generated_url
