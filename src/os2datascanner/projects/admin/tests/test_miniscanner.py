
from random import choices
import django.core.files.uploadedfile as dj_file
import json
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.projects.admin.adminapp.views.miniscanner_views import *

class DummyObject():
    def __init__(self, objs) -> None:
        self.files = objs
    def get(self, obj):
        return self.files[obj]


class FilesObj(DummyObject):
    pass


class Post(DummyObject):
    pass


class Meta(DummyObject):
    pass


class Request():
    def __init__(self, fileObjsDict, postObjsDict, metaObjsDict) -> None:
        self.FILES = FilesObj(fileObjsDict)
        self.POST = Post(postObjsDict)
        self.META = Meta(metaObjsDict)

def generateDummyContent(n=10):
    CHARACTERS = "abcdefghijklmnopqrstuvwxyzæøå"
    return '\n'.join([''.join(choices(CHARACTERS, k=25)) for _ in range(n)]) # Generates a block of random characters


cpr_rule = json.dumps(CPRRule().to_json_object())
customRegexRule = json.dumps(RegexRule("doesthiswordexist").to_json_object())


def buildRequest(rule, file, text):
    """
    Simulate a request to the miniscanner. Does not support file
    scanning, as it requires to pass a file_obj as a parameter.
    """
    request = Request({"file": file}, {"rule": rule, "text": text}, {"REMOTE_ADDR": "localhost:8020"}) 
    # REMOTE_ADDR value is not important, but its value is called and used in the execute_mini_scan, so it needs to be present
    return request

def test_text_CprRuleFixed():
    file = None
    text = "hello"

    req = buildRequest(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_text_CprRuleRandom():
    file = None
    text = generateDummyContent()

    req = buildRequest(cpr_rule, file, text)
    # In the absurd case where generateDummyContent() generates 'mycprisxxxxxxxxxx', it won't trigger so this should stay false
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_text_CprRuleReal():
    file = None
    text = "1111111118"

    req = buildRequest(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_text_RegexRuleNegative():
    file = None
    text = "This should produce false / nothing found"

    req = buildRequest(customRegexRule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_text_RegexRulePositive():
    file = None
    text = "SEDRTCTVYCBUYNIOM__doesthiswordexist__FSDBNIGOFDFDÆM"

    req = buildRequest(customRegexRule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_file_CprRuleFixed():
    file = dj_file.SimpleUploadedFile("file", "hello".encode())
    text = None

    req = buildRequest(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_CprRuleRandom():
    file = dj_file.SimpleUploadedFile("file", generateDummyContent().encode())
    text = None

    req = buildRequest(cpr_rule, file, text)
    # In the absurd case where generateDummyContent() generates 'mycprisxxxxxxxxxx', it won't trigger so this should stay false
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_CprRuleReal():
    file = dj_file.SimpleUploadedFile("file", "1111111118".encode())
    text = None

    req = buildRequest(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_file_RegexRuleNegative():
    file = dj_file.SimpleUploadedFile("file", "This should produce false".encode())
    text = None

    req = buildRequest(customRegexRule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_RegexRulePositive():
    file = dj_file.SimpleUploadedFile("file", "SEDRTCTVYCBUYNIOM__doesthiswordexist__FSDBNIGOFDFDÆM".encode())
    text = None

    req = buildRequest(customRegexRule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res
