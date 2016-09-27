#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOCS
# =============================================================================

"""Integration with Jupyter notebook

"""


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_ipython_extension(ipython):
    from corral import core
    core.setup_environment()