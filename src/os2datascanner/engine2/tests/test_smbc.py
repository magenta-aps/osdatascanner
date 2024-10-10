from os2datascanner.engine2.model import smbc
from os2datascanner.engine2.model.core import SourceManager


class TestSMBC:
    def test_normal_exploration(self):
        with SourceManager() as sm:
            source = smbc.SMBCSource(
                    "//samba/general/smb-metadata",
                    "os2", "swordfish",
                    skip_super_hidden=False)
            assert set(source.handles(sm)) == set([
                    smbc.SMBCHandle(source, "~hidden.mode-override"),
                    smbc.SMBCHandle(source, "~normal/test-vector"),
                    smbc.SMBCHandle(source, "normal/test-vector"),
                    smbc.SMBCHandle(source, "hidden.mode-override"),
                    smbc.SMBCHandle(source, "system-hidden/test-vector"),
                    smbc.SMBCHandle(source, "~hidden/test-vector"),
                    smbc.SMBCHandle(source, "hidden/test-vector"),
                    smbc.SMBCHandle(source, "system-hidden.mode-override"),
                    smbc.SMBCHandle(source, "~system-hidden/test-vector"),
                    smbc.SMBCHandle(source, "~system-hidden.mode-override"),
                    ])

    def test_super_hidden_exploration(self):
        smbc.SMBCSource.allow_fake_mode = True
        try:
            with SourceManager() as sm:
                source = smbc.SMBCSource(
                        "//samba/general/smb-metadata",
                        "os2", "swordfish",
                        skip_super_hidden=True)
                assert set(source.handles(sm)) == set([
                    smbc.SMBCHandle(source, "~hidden.mode-override"),
                    smbc.SMBCHandle(source, "~normal/test-vector"),
                    smbc.SMBCHandle(source, "normal/test-vector"),
                    smbc.SMBCHandle(source, "hidden.mode-override"),
                    # smbc.SMBCHandle(source, "system-hidden/test-vector"),
                    # smbc.SMBCHandle(source, "~hidden/test-vector"),
                    smbc.SMBCHandle(source, "hidden/test-vector"),
                    smbc.SMBCHandle(source, "system-hidden.mode-override"),
                    # smbc.SMBCHandle(source, "~system-hidden/test-vector"),
                    smbc.SMBCHandle(source, "~system-hidden.mode-override"),
                    ])
        finally:
            smbc.SMBCSource.allow_fake_mode = False
