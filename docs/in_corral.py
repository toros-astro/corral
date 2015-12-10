#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at 2015-12-09T16:33:40.827063 by corral 0.0.1


if __name__ == "__main__":
    import os

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", "pipeline.settings")

    from corral import cli
    cli.run_from_command_line()
