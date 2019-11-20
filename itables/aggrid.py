"""HTML/js representation of Pandas dataframes, using ag-grid"""

import os
import re
import uuid
import json
import warnings
import numpy as np
import pandas as pd
import pandas.io.formats.format as fmt
from IPython.core.display import display, Javascript, HTML
import itables.options as opt

try:
    unicode  # Python 2
except NameError:
    unicode = str  # Python 3


def load_aggrid():
    """Load the datatables.net library, and the corresponding css"""
    display(Javascript("""require.config({
        paths: {
            ag: 'https://unpkg.com/ag-grid-community/dist/ag-grid-community.min.noStyle',
        }
    });
    $('head').append('<link rel="stylesheet" type="text/css" \
                    href = "https://unpkg.com/ag-grid-community/dist/styles/ag-grid.css" > ');
    $('head').append('<link rel="stylesheet" type="text/css" \
                    href = "https://unpkg.com/ag-grid-community/dist/styles/ag-theme-balham.css" > ');

    """))


def dtype_to_ag_column_type(dtype):
    if dtype.kind in ['i', 'f']:
        return 'numberColumn'
    if dtype.kind == 'M':
        return 'dateColumn'
    return None


def columns_as_ag_header(df, showIndex):
    def _ag_header(df_with_col_number):
        if isinstance(df_with_col_number.columns, pd.MultiIndex):
            return [{
                "headerName": level,
                "groupId": level,
                "children": _ag_header(df_with_col_number[level])}
                for level in df_with_col_number.columns.get_level_values(0).unique()]

        return [{"headerName": col,
                 "type": dtype_to_ag_column_type(df_with_col_number[col].dtype),
                 "field": '{}'.format(df_with_col_number[col].iloc[0])}
                if dtype_to_ag_column_type(df_with_col_number[col].dtype)
                else
                {"headerName": col,
                 "field": '{}'.format(df_with_col_number[col].iloc[0])}
                for col in df_with_col_number.columns]

    header = [{'headerName': idx_name, "field": i} for i, idx_name in enumerate(df.index)] if showIndex else []
    shift = len(header)
    df_with_col_number = pd.DataFrame([shift + np.arange(len(df.columns))], index=[0], columns=df.columns)
    return header + _ag_header(df_with_col_number)


def _aggrid_repr_(df=None, tableId=None, **kwargs):
    """Return the HTML/javascript representation of the table"""

    # Default options
    for option in dir(opt):
        if not option in kwargs and not option.startswith("__"):
            kwargs[option] = getattr(opt, option)

    # These options are used here, not in ag-grid
    showIndex = kwargs.pop('showIndex')
    maxBytes = kwargs.pop('maxBytes')
    classes = kwargs.pop('classes')
    height = kwargs.pop('height')

    if isinstance(df, (np.ndarray, np.generic)):
        df = pd.DataFrame(df)

    if isinstance(df, pd.Series):
        df = df.to_frame()

    if df.values.nbytes > maxBytes > 0:
        raise ValueError('The dataframe has size {}, larger than the limit {}\n'.format(df.values.nbytes, maxBytes) +
                         'Please print a smaller dataframe, or enlarge or remove the limit:\n'
                         'import itables.options as opt; opt.maxBytes=0')

    tableId = tableId or 'id-' + str(uuid.uuid4())
    if showIndex == 'auto':
        showIndex = df.index.name is not None or not isinstance(df.index, pd.RangeIndex)

    if not showIndex:
        df = df.set_index(pd.RangeIndex(len(df.index)))

    # Generate table div
    if isinstance(classes, list):
        classes = ' '.join(classes)
    div_args = {'id': tableId, 'class': classes}
    if kwargs.get('domLayout') != 'autoHeight':
        div_args['style'] = "height: {}".format(height)
    table_div = '<div {}></div>'.format(' '.join(['{}="{}"'.format(key, div_args[key]) for key in div_args]))

    # Table columns
    kwargs['columnDefs'] = columns_as_ag_header(df, showIndex)
    kwargs['defaultColDef'] = {
                                  'resizable': True,
                                  'sortable': True,
                                  'filter': True
                              },

    # Table content as 'data' for DataTable
    formatted_df = df.reset_index() if showIndex else df.copy()
    for col in formatted_df:
        x = formatted_df[col]
        if x.dtype.kind in ['b', 'i', 's']:
            continue

        if x.dtype.kind == 'O':
            formatted_df[col] = formatted_df[col].astype(unicode)
            continue

        formatted_df[col] = np.array(fmt.format_array(x.values, None))
        if x.dtype.kind == 'f':
            try:
                formatted_df[col] = formatted_df[col].astype(np.float)
            except ValueError:
                pass

    fields = ['{}'.format(i) for i, col in enumerate(formatted_df.columns)]

    kwargs['rowData'] = [dict(zip(fields, row)) for row in formatted_df.values.tolist()]

    return """<div>""" + table_div + """
<script type="text/javascript">
require(["ag"], function (agGrid) {
    $(document).ready(function () {
        var gridOptions = """ + json.dumps(kwargs) + """;
        var eGridDiv = document.querySelector('#""" + tableId + """');
        new agGrid.Grid(eGridDiv, gridOptions);
    });
})
</script>
</div>
"""


def show(df=None, **kwargs):
    """Show a dataframe"""
    html = _aggrid_repr_(df, **kwargs)
    display(HTML(html))
