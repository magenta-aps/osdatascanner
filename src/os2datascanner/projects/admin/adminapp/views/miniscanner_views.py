import json
import structlog

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F

from ..models.rules import CustomRule

from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.model.utilities.temp_resource import (
        NamedTemporaryResource)
from os2datascanner.engine2.pipeline import messages, worker
from os2datascanner.projects.admin import settings


logger = structlog.get_logger("adminapp")


class MiniScanner(TemplateView, LoginRequiredMixin):
    template_name = "miniscan.html"

    def dispatch(self, request, *args, **kwargs):
        if (settings.MINISCAN_REQUIRES_LOGIN
                and not request.user.is_authenticated):
            return self.handle_no_permission()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        context = super().get_context_data()
        context["customrule_list"] = CustomRule.objects.annotate(rule_field=F("_rule"))

        return context

def mini_scan(scan_item, rule):
    """
    This function will take a scanItem arg as well as a rule arg. It checks
    the nature of scanItem (i.e. file or text), and performs the scan with
    the required rule, given as parameter/arg. It yields each result into
    the replies list in the execute_mini_scan() function.
    """

    try:
        item_name = scan_item.name
    except AttributeError:
        # It's not a file does not possess a name attribute.
        # Therefore, it's text.
        item_name = "text"

    with NamedTemporaryResource(item_name) as ntr:
        try:
            binary_scan_contents = scan_item.read()
        except AttributeError:
            # It's not a file and can't be read. Therefore, it's text.
            binary_scan_contents = scan_item.encode()
        except Exception as e:
            # In case of a second unknown error
            logger.warning(
                "Miniscanner -"
                " Got an unexpected error : {}".format(str(e))
            )

        with ntr.open("wb") as fp:
            fp.write(binary_scan_contents)

        if ntr.size() <= settings.MINISCAN_FILE_SIZE_LIMIT:
            # XXX: it'd be nice to run this with timeout protection, but
            # that isn't possible in a gunicorn worker
            handle = FilesystemHandle.make_handle(ntr.get_path())

            conv = messages.ConversionMessage(
                scan_spec=messages.ScanSpecMessage(
                    scan_tag=messages.ScanTagFragment.make_dummy(),
                    source=handle.source,
                    rule=rule,
                    filter_rule=None,
                    configuration={},
                    progress=None),
                handle=handle,
                progress=messages.ProgressFragment(
                    rule=rule,
                    matches=[]),
                ).to_json_object()

            for channel, message_ in worker.process(SourceManager(), conv):
                if channel in ("os2ds_matches",):
                    message = messages.MatchesMessage.from_json_object(
                        message_)

                    if not message.matched:
                        continue

                    yield message
        else:
            logger.warning(
                    "miniscanner rejected too large object",
                    item_name=item_name)


def execute_mini_scan(request):  # noqa:CCR001
    context = {
        "file_obj": (file_obj := request.FILES.get("file")),
        "text": (text := request.POST.get("text")),
        "raw_rule": (raw_rule := request.POST.get("rule")),
        "halfbaked_rule": (halfbaked_rule := json.loads(raw_rule or "null")),

        "replies": (replies := []),
    }

    rule = None
    if halfbaked_rule:
        rule = Rule.from_json_object(halfbaked_rule)

    if file_obj:
        for m in mini_scan(file_obj, rule):
            replies.append(m)
    if text:
        for m in mini_scan(text, rule):
            replies.append(m)

    return render(request, "components/miniscanner/miniscan_results.html", context)