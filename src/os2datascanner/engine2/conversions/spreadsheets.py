from .types import OutputType
from .registry import conversion
from ..model.core import Resource

# ROW_TYPE = "application/x.os2datascanner.spreadsheet.row"
SHEET_TYPE = "application/x.os2datascanner.spreadsheet"


@conversion(OutputType.Text, SHEET_TYPE)
def pandas_dataframe_processor(r: Resource, **kwargs):
    """
    Converts Sheets from Excel-like files to text using efficient pandas.Dataframes.
    """
    sheet_name = r.handle.relative_path
    # By default, pandas tries to be clever and will make sure all values in a
    # column have the same type. This is good for data analysis but bad for our
    # purposes, where we care about the visual representation, so we switch
    # that behaviour off by specifying "dtype=object"
    df = r._sm.open(r.handle.source).parse(sheet_name=sheet_name, dtype=object)
    return df.to_csv(sep="\t", index=False)
