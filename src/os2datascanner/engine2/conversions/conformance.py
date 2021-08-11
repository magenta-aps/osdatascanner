import requests

from .types import OutputType
from .registry import conversion


@conversion(OutputType.ConformanceProblems, "text/html")
def conformance_processor(r, **kwargs):
    try:
        k = requests.post(
                "http://172.17.0.1:8110/axe",
                json={"url": r.handle.presentation_url},
                auth=("test", "testpassword"))
        if k.status_code == 200:
            body = k.json()
            return [
                    violation["help"]
                    for violation in body["data"]["violations"]]
    except OSError:
        return None
