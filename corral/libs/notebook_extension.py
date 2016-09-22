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
    from corral.cli.commands import Shell

    core.setup_environment()

    ns = Shell().get_locals()
    ipython.push(ns, interactive=True)
