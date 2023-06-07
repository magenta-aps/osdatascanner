import json

from django.http.response import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle
from os2datascanner.engine2.model.utilities.temp_resource import (
        NamedTemporaryResource)
from os2datascanner.engine2.pipeline import messages, worker
from os2datascanner.projects.admin import settings


class MiniScanner(TemplateView, LoginRequiredMixin):
    template_name = "os2datascanner/miniscan.html"

    def dispatch(self, request, *args, **kwargs):
        if (settings.MINISCAN_REQUIRES_LOGIN
                and not request.user.is_authenticated):
            return self.handle_no_permission()
        else:
            return super().dispatch(request, *args, **kwargs)


def execute_mini_scan(request):  # noqa:CCR001
    print(request)

    file_obj = request.FILES.get("file")
    raw_rule = request.POST.get("rule")
    halfbaked_rule = json.loads(raw_rule or "null")

    if not file_obj:
        return HttpResponse("""
<div id="response" class="error">
No file uploaded.
</div>""")
    elif file_obj.size > (limit := settings.MINISCAN_FILE_SIZE_LIMIT):
        return HttpResponse(f"""
<div id="response" class="error">
File too big ({file_obj.size} bytes > {limit} bytes).
</div>""")
    elif not halfbaked_rule:
        return HttpResponse("""
<div id="response" class="error">
No rule specified.
</div>""")

    rule = Rule.from_json_object(halfbaked_rule)

    with NamedTemporaryResource(file_obj.name) as ntr:
        with ntr.open("wb") as fp:
            fp.write(file_obj.read())

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
                        matches=[])).to_json_object()

        print(conv)

        def _execute_mini_scan():
            yield "<table id=\"response\">"
            yield "<thead><tr>"
            yield "<th>Location</th><th>Match</th><th>Match context</th>"
            yield "</tr></thead>"
            yield "<tbody>"
            count = 0
            for channel, message_ in worker.process(SourceManager(), conv):
                if channel in ("os2ds_matches",):
                    message = messages.MatchesMessage.from_json_object(
                            message_)

                    print(message)
                    if not message.matched:
                        continue
                    count += 1

                    for fragment in message.matches:
                        for match in fragment.matches:
                            yield "<tr>"
                            yield f"<td>{message.handle.presentation}</td>"
                            yield f"<td>{match['match']}</td>"
                            yield f"<td>{match['context']}</td>"
                            yield "</tr>"
            if count == 0:
                yield "<tr><td colspan=\"3\" style=\"text-align: center\">"
                yield "No matches found"
                yield "</td></tr>"
            yield "</tbody>"
            yield "</table>"

        # XXX: it might have been nice to use StreamingHttpResponse here, but
        # then we leave the context in which the uploaded file actually exists
        return HttpResponse("\n".join(_execute_mini_scan()))
