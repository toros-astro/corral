#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at ${timestamp} by corral ${version}


if __name__ == "__main__":
    import os

    os.environ.setdefault("CORRAL_SETTINGS_MODULE", "${project_name}.settings")

    from corral import cli
    cli.run_from_command_line()
