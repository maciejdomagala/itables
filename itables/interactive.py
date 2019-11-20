"""Activate the representation of Pandas dataframes as interactive tables"""
import pandas as pd
from .aggrid import _aggrid_repr_

pd.DataFrame._repr_html_ = _aggrid_repr_
pd.Series._repr_html_ = _aggrid_repr_
