from os2datascanner.engine2.model import smbc
from os2datascanner.engine2.model.core import SourceManager


class TestSMBC:
    def test_normal_exploration(self):
        with SourceManager() as sm:
            source = smbc.SMBCSource(
                    "//samba/general/smb-metadata",
                    "os2", "swordfish",
                    skip_super_hidden=False)

            source_handles = set(source.handles(sm))
            expected_handles = {
                smbc.SMBCHandle(source, "~hidden.attr-override"),
                smbc.SMBCHandle(source, "~normal/test-vector"),
                smbc.SMBCHandle(source, "normal/test-vector"),
                smbc.SMBCHandle(source, "normal/test-vector-2"),
                smbc.SMBCHandle(source, "normal/test-vector-2.attr-override"),
                smbc.SMBCHandle(source, "normal/test-vector-3"),
                smbc.SMBCHandle(source, "normal/test-vector-3.attr-override"),
                smbc.SMBCHandle(source, "hidden.attr-override"),
                smbc.SMBCHandle(source, "system-hidden/test-vector"),
                smbc.SMBCHandle(source, "~hidden/test-vector"),
                smbc.SMBCHandle(source, "hidden/test-vector"),
                smbc.SMBCHandle(source, "system-hidden.attr-override"),
                smbc.SMBCHandle(source, "~system-hidden/test-vector"),
                smbc.SMBCHandle(source, "~system-hidden.attr-override"),
            }
            assert source_handles == expected_handles

    def test_super_hidden_exploration(self):
        smbc.SMBCSource.allow_fake_attr = True
        try:
            with SourceManager() as sm:
                source = smbc.SMBCSource(
                        "//samba/general/smb-metadata",
                        "os2", "swordfish",
                        skip_super_hidden=True)

                source_handles = set(source.handles(sm))
                expected_handles = {
                    smbc.SMBCHandle(source, "~hidden.attr-override"),
                    smbc.SMBCHandle(source, "~normal/test-vector"),
                    smbc.SMBCHandle(source, "normal/test-vector"),
                    smbc.SMBCHandle(source, "normal/test-vector-2"),
                    smbc.SMBCHandle(source, "normal/test-vector-2.attr-override"),
                    smbc.SMBCHandle(source, "normal/test-vector-3"),
                    smbc.SMBCHandle(source, "normal/test-vector-3.attr-override"),
                    smbc.SMBCHandle(source, "hidden.attr-override"),
                    smbc.SMBCHandle(source, "hidden/test-vector"),
                    smbc.SMBCHandle(source, "system-hidden.attr-override"),
                    smbc.SMBCHandle(source, "~system-hidden.attr-override"),

                    # Hidden by overridden SYSTEM attribute plus leading ~
                    # smbc.SMBCHandle(source, "~hidden/test-vector"),
                    # Hidden by overridden HIDDEN | SYSTEM attributes
                    # smbc.SMBCHandle(source, "system-hidden/test-vector"),
                    # Hidden by overridden HIDDEN | SYSTEM attributes (the
                    # leading ~ is just the cherry on the top)
                    # smbc.SMBCHandle(source, "~system-hidden/test-vector"),
                }
                assert source_handles == expected_handles
        finally:
            smbc.SMBCSource.allow_fake_attr = False
