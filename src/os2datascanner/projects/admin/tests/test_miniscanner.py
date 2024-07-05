from os2datascanner.projects.admin.adminapp.views.miniscanner_views import *
from random import choice

class DummyFile():
    def __init__(self, name, fileContents) -> None:
        self.contents = fileContents
        self.name = name

    def read(self):
        return self.contents.encode()

class FilesObj():
    def __init__(self, objs) -> None:
        self.files = objs
    def get(self, obj):
        return self.files[obj]
    
class Post():
    def __init__(self, objs) -> None:
        self.items = objs
    def get(self, obj):
        return self.items[obj]
    
class Meta():
    def __init__(self, objs) -> None:
        self.items = objs
    def get(self, obj):
        return self.items[obj]

class Request():
    def __init__(self, fileObjsDict, postObjsDict, metaObjsDict) -> None:
        self.FILES = FilesObj(fileObjsDict)
        self.POST = Post(postObjsDict)
        self.META = Meta(metaObjsDict)

def generateDummyContent(n=10):
    CHARACTERS = "abcdefghijklmnopqrstuvwxyzæøå"
    return '\n'.join([''.join([choice(CHARACTERS) for _ in range(25)]) for _ in range(n)]) # Generates a block of random characters

cpr_rule = '{"name": null, "type": "cpr", "blacklist": ["p-nummer", "p.nr", "p-nr", "customer no", "tullstatistisk", "dhk:tx", "test report no", "tullstatistik", "faknr", "order number", "fakturanummer", "protocol no.", "ordrenummer", "customer-no", "fak-nr", "pnr", "bilagsnummer"], "whitelist": ["cpr"], "exceptions": "", "modulus_11": true, "sensitivity": null, "examine_context": true, "ignore_irrelevant": true}'
customRegexRule = '{"type":"regex","expression":".*doesthiswordexist"}'

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
    file = DummyFile("file", "hello")
    text = None

    req = buildRequest(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_CprRuleRandom():
    file = DummyFile("file", generateDummyContent())
    text = None

    req = buildRequest(cpr_rule, file, text)
    # In the absurd case where generateDummyContent() generates 'mycprisxxxxxxxxxx', it won't trigger so this should stay false
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_CprRuleReal():
    file = DummyFile("file", "1111111118")
    text = None

    req = buildRequest(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_file_RegexRuleNegative():
    file = DummyFile("file", "This should produce false")
    text = None

    req = buildRequest(customRegexRule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_RegexRulePositive():
    file = DummyFile("file", "SEDRTCTVYCBUYNIOM__doesthiswordexist__FSDBNIGOFDFDÆM")
    text = None

    req = buildRequest(customRegexRule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res
