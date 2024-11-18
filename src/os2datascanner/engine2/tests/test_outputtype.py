import pytest

from datetime import datetime, timezone, timedelta
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.conversions.types import Link, OutputType


DITTO = object()


class TestOutputSerialisation:
    @pytest.mark.parametrize(
            "type_, original_value, serialised_value",
            [
                (
                    OutputType.Text,
                    "4",
                    DITTO),
                (
                    OutputType.LastModified,
                    timestamp := datetime(
                            2024, 11, 27, 14, 4, 51,
                            tzinfo=timezone(timedelta(seconds=3600))),
                    timestamp_str := "2024-11-27T14:04:51+0100"),
                (
                    OutputType.ImageDimensions,
                    (1024, 768),
                    [1024, 768]),
                (
                    OutputType.Links,
                    [
                        Link(
                                "https://www.example.com/",
                                "Visit our partner Example Corp"),
                        Link(
                                "https://www.example.net/",
                                "Or our other partner Example Networks")
                    ],
                    [
                        [
                            "https://www.example.com/",
                            "Visit our partner Example Corp"
                        ],
                        [
                            "https://www.example.net/",
                            "Or our other partner Example Networks"
                        ]
                    ]),
                (
                    OutputType.Manifest,
                    [
                        FilesystemHandle.make_handle(
                                "/home/jens/faktura.pdf"),
                        FilesystemHandle.make_handle(
                                "/home/jens/images/scanner/0001.TIF")
                    ],
                    [
                        {
                            "type": "file",
                            "source": {
                                "type": "file",
                                "path": "/home/jens"
                            },
                            "path": "faktura.pdf",
                            "hints": None
                        },
                        {
                            "type": "file",
                            "source": {
                                "type": "file",
                                "path": "/home/jens/images/scanner"
                            },
                            "path": "0001.TIF",
                            "hints": None
                        }
                    ]),
                (
                    OutputType.EmailHeaders,
                    {
                        "from": "af@magenta-aps.dk",
                        "subject": "Now where did I leave my keys?",
                    },
                    DITTO),
                (
                    OutputType.MRZ,
                    "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<\n"
                    "L898902C36UT07408122F1204159ZE184226B<<<<<10",
                    DITTO),
                (
                    OutputType.DatabaseRow,
                    {
                        "ID": 479,
                        "User.ID": 20,
                        "User.Height": 1.79,
                        "User.Name": "Jens Testsen",
                        "User.Active": True,
                        "User.EmployedSince": timestamp,
                        "User.Manager": None,
                    },
                    {
                        "ID": ["int", 479],
                        "User.ID": ["int", 20],
                        "User.Height": ["float", 1.79],
                        "User.Name": ["str", "Jens Testsen"],
                        "User.Active": ["bool", True],
                        "User.EmployedSince": ["datetime", timestamp_str],
                        "User.Manager": [None, None],
                    }),
            ])
    def test_outputtype(self, type_, original_value, serialised_value):
        if serialised_value == DITTO:
            serialised_value = original_value

        assert type_.encode_json_object(original_value) == serialised_value
        assert type_.decode_json_object(serialised_value) == original_value
