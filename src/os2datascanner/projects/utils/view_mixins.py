import csv
from enum import Enum

from django.http import StreamingHttpResponse

from os2datascanner.utils.system_utilities import time_now


class CSVExportMixin:
    """View mixin for exporting a queryset normally delivered to a template
    as a CSV-file instead. Intended use: Define a new view, which inherits
    from the view, which normally delivers context to a template, and this
    mixin. It is important, that the new view inherits from this mixin first!"""
    paginator_class = None  # We never want to paginate results
    # A list of dicts describing each column
    # - 'name': A string for identifying the column.
    #           For a FIELD column, this should be the name of the field
    # - 'label': A string for the header of the csv. Should be translated
    # - 'type': Of type ColumnType, describing how this column should get its value
    # - 'function': A function used to generate the values of this column.
    #               Takes a single object as argument. Only needed for functional columns
    columns = []
    exported_filename = "exported_file"

    class CSVBuffer:
        def write(self, value):
            return value

    class ColumnType(Enum):
        """Enum for the two types of columns.
        The type of a column describes how the values of the column is determined.
        A FIELD column simply takes the values from the queryset.
        A FUNCTION column uses a given function to calculate a value for each object."""
        FIELD = 1
        FUNCTION = 2

    def prepare_stream(self):
        """Writes to a virtual buffer, so there is only ever one row of the CSV
        in memory."""
        pseudo_buffer = self.CSVBuffer()
        self.writer = csv.writer(pseudo_buffer)

    def stream_queryset(self, rows):
        """Writes in csv-format, with self.exported_fields.keys() used as fields,
        and each line containing the values of one row from rows."""
        self.prepare_stream()

        yield self.writer.writerow([c['label'] for c in self.columns])

        for row in rows:
            yield self.writer.writerow([row[c['name']] for c in self.columns])

    def get_rows(self):
        """Takes a queryset and returns a list of rows,
        each row containing values for each field in export_fields"""
        qs = self.get_queryset().order_by('pk')

        field_columns = [c for c in self.columns if c['type'] == self.ColumnType.FIELD]
        rows = list(qs.values(*[c['name'] for c in field_columns]))

        function_columns = [c for c in self.columns if c['type'] == self.ColumnType.FUNCTION]
        for obj, row in zip(qs, rows):
            for col in function_columns:
                row[col['name']] = col['function'](obj)

        return rows

    def get(self, request, *args, **kwargs):
        self.add_conditional_colums(request)

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

    def add_conditional_colums(self, request):
        """If any columns only need to be added conditionally,
        make a method doing it overwriting this one."""
        # self.columns = <class>.columns
        # if <condition>:
        #   self.columns = self.columns + [{<dict describing column>}]
        pass
