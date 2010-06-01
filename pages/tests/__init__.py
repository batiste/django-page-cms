"""Django page CMS test suite module"""
from djangox.test.depth import alltests

def suite():
    return alltests(__file__, __name__)
