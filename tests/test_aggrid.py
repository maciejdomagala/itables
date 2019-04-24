"""Test that the code in all the test notebooks work, including README.md"""

import pandas as pd
import pytest
from testfixtures import compare
from itables.sample import sample_dfs
from itables.aggrid import columns_as_ag_header, _aggrid_repr_


def test_ag_header():
    compare(columns_as_ag_header(pd.DataFrame(columns=['A', 'B']), showIndex=False),
            [{'headerName': 'A', 'field': '0', 'type': 'numberColumn'},
             {'headerName': 'B', 'field': '1', 'type': 'numberColumn'}])

    compare(columns_as_ag_header(
        pd.DataFrame(columns=pd.MultiIndex.from_product((['A', 'B'], ['C', 'D']))), showIndex=False),
        [{'headerName': 'A',
          'groupId': 'A',
          'children': [{'headerName': 'C', 'field': '0', 'type': 'numberColumn'},
                       {'headerName': 'D', 'field': '1', 'type': 'numberColumn'}]},
         {'headerName': 'B',
          'groupId': 'B',
          'children': [{'headerName': 'C', 'field': '2', 'type': 'numberColumn'},
                       {'headerName': 'D', 'field': '3', 'type': 'numberColumn'}]}])


@pytest.mark.parametrize('df', sample_dfs())
def test_sample_dfs(df):
    _aggrid_repr_(df)
