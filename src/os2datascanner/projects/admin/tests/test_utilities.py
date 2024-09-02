from ..adminapp.models.usererrorlog import UserErrorLog
from ..adminapp.models.scannerjobs.scanner_helpers import ScanStatus
from ..organizations.models.organization import Organization

dummy_rule_dict = {
    "name": "dummy rule",
    "description": "this is a dumb dumb dummy rule",
    "_rule": {"type": "regex", "expression": "dummy"}
}


def create_errors(num, organization=None,
                  scan_status=None, path="pathypathy",
                  error_message="UnknownError: This is definitely an error",
                  is_new=False, is_removed=False):
    UserErrorLog.objects.bulk_create([
        UserErrorLog(
            organization=organization if organization else Organization.objects.first(),
            scan_status=scan_status if scan_status else ScanStatus.objects.last(),
            path=path,
            error_message=error_message,
            is_new=is_new,
            is_removed=is_removed
        ) for _ in range(num)
    ])
