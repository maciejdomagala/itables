"""Load the datatables library from the internet, instead of embedding it in the notebook"""
from .javascript import load_datatables

load_datatables(connected=True)
