from os2datascanner.projects.admin.adminapp.views.miniscanner_views import *
from random import choice


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

def testCprRuleFixed():
    file = None

    req = buildRequest(cpr_rule, file, "hello")
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def testCprRuleRandom():
    file = None
    req = buildRequest(cpr_rule, file, generateDummyContent())
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def testCprRuleReal():
    file = None
    req = buildRequest(cpr_rule, file, "1111111118")
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def testRegexRuleNegative():
    file = None

    req = buildRequest(customRegexRule, file, "This should produce false / nothing found")
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def testRegexRulePositive():
    file = None

    req = buildRequest(customRegexRule, file, "SEDRTCTVYCBUYNIOM__doesthiswordexist__FSDBNIGOFDFDÆM")
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res
