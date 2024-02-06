import csv

from django.http import StreamingHttpResponse

from os2datascanner.utils.system_utilities import time_now


class CSVExportMixin:
    """View mixin for exporting a queryset normally delivered to a template
    as a CSV-file instead. Intended use: Define a new view, which inherits
    from the view, which normally delivers context to a template, and this
    mixin. It is important, that the new view inherits from this mixin first!"""
    paginator_class = None  # We never want to paginate results
    exported_fields = {}  # Structure: {"<label>": "<field_name>", ...}
    exported_filename = "exported_file"

    class CSVBuffer:
        def write(self, value):
            return value

    def prepare_stream(self):
        """Writes to a virtual buffer, so there is only ever one row of the CSV
        in memory."""
        pseudo_buffer = self.CSVBuffer()
        self.writer = csv.writer(pseudo_buffer)

    def stream_queryset(self, rows):
        """Writes in csv-format, with self.exported_fields.keys() used as fields,
        and each line containing the values of one row from rows."""
        self.prepare_stream()

        yield self.writer.writerow(self.exported_fields.keys())

        for row in rows:
            yield self.writer.writerow(row.values())

    def get_rows(self):
        """Takes a queryset and returns a list of rows,
        each row containing values for each field in export_fields"""
        return list(self.get_queryset().values(*self.exported_fields.values()))

    def get(self, request, *args, **kwargs):
        # Since we are streaming, we need to select the entire queryset, and
        # stream it from memory. We are not able to make further queries after
        # streaming has begun.
        rows = self.get_rows()

        response = StreamingHttpResponse(
            self.stream_queryset(rows),
            content_type="text/csv",
            headers={
                "Content-Disposition":
                f'attachment; filename="{time_now()}-{self.exported_filename}.csv"'})

        return response
