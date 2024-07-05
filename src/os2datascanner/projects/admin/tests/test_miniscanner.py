
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
    def __init__(self, file_objs_dict, post_objs_dict, meta_objs_dict) -> None:
        self.FILES = FilesObj(file_objs_dict)
        self.POST = Post(post_objs_dict)
        self.META = Meta(meta_objs_dict)

def generate_dummy_content(n=10):
    CHARACTERS = "abcdefghijklmnopqrstuvwxyzæøå"
    return '\n'.join([''.join(choices(CHARACTERS, k=25)) for _ in range(n)]) # Generates a block of random characters


cpr_rule = json.dumps(CPRRule().to_json_object())
custom_regex_rule = json.dumps(RegexRule("doesthiswordexist").to_json_object())


def build_request(rule, file, text):
    """
    Simulate a request to the miniscanner. Does not support file
    scanning, as it requires to pass a file_obj as a parameter.
    """
    request = Request({"file": file}, {"rule": rule, "text": text}, {"REMOTE_ADDR": "localhost:8020"}) 
    # REMOTE_ADDR value is not important, but its value is called and used in the execute_mini_scan, so it needs to be present
    return request

def test_text_cpr_rule_fixed():
    file = None
    text = "hello"

    req = build_request(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_text_cpr_rule_random():
    file = None
    text = generate_dummy_content()

    req = build_request(cpr_rule, file, text)
    # In the absurd case where generate_dummy_content() generates 'mycprisxxxxxxxxxx', it won't trigger so this should stay false
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_text_cpr_rule_real():
    file = None
    text = "1111111118"

    req = build_request(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_text_regex_rule_negative():
    file = None
    text = "This should produce false / nothing found"

    req = build_request(custom_regex_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_text_regex_rule_positive():
    file = None
    text = "SEDRTCTVYCBUYNIOM__doesthiswordexist__FSDBNIGOFDFDÆM"

    req = build_request(custom_regex_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_file_cpr_rulefixed():
    file = dj_file.SimpleUploadedFile("file", "hello".encode())
    text = None

    req = build_request(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file_cpr_rule_random():
    file = dj_file.SimpleUploadedFile("file", generate_dummy_content().encode())
    text = None

    req = build_request(cpr_rule, file, text)
    # In the absurd case where generate_dummy_content() generates 'mycprisxxxxxxxxxx', it won't trigger so this should stay false
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file__cpr_rule_real():
    file = dj_file.SimpleUploadedFile("file", "1111111118".encode())
    text = None

    req = build_request(cpr_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res


def test_file__regex_rule_negative():
    file = dj_file.SimpleUploadedFile("file", "This should produce false".encode())
    text = None

    req = build_request(custom_regex_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" in res

def test_file__regex_rule_positive():
    file = dj_file.SimpleUploadedFile("file", "SEDRTCTVYCBUYNIOM__doesthiswordexist__FSDBNIGOFDFDÆM".encode())
    text = None

    req = build_request(custom_regex_rule, file, text)
    res = execute_mini_scan(req).content.decode()
    assert "Ingen resultater fundet" not in res
