#!/usr/bin/env python

# ORIGINAL: https://github.com/msabramo/sqlalchemy_sql_shell

"""
A simple database-agnostic SQL shell that uses SQLAlchemy to abstract out how
to connect to different database engines.

"""

import sys

import six

import sqlalchemy as sa

from texttable import Texttable


def get_query():
    lines = []

    if sys.stdin.isatty():
        prompt = 'SQL> '
    else:
        prompt = ''

    while True:
        try:
            input_line = six.moves.input(prompt).strip()
            if len(input_line) == 0 and len(lines) == 0:
                return None
            lines.append(input_line)
            if input_line.endswith(';'):
                break
            prompt = '...> '
        except KeyboardInterrupt:
            lines = []
            prompt = 'SQL> '
            sys.stdout.write("\n")
            continue

    return '\n'.join(lines)


def process_query(conn, query):
    table = Texttable(max_width=0)
    table.set_deco(Texttable.BORDER | Texttable.HEADER | Texttable.VLINES)

    try:
        result = conn.execute(query)
    except (sa.exc.ProgrammingError, sa.exc.OperationalError) as e:
        print(str(e))
    else:
        if result.returns_rows:
            try:
                for idx, row in enumerate(result.fetchall()):
                    if idx == 0:
                        table.header(row.keys())

                    table.add_row(row)
            except sa.exc.ResourceClosedError as e:
                print(str(e))
            else:
                print(table.draw())
        elif result.rowcount > 0:
            print('result.rowcount = %d' % result.rowcount)


def run(engine):

    conn = engine.connect()
    sys.stdout.write("Type 'exit;' or '<CTRL> + <D>' for exit the shell\n\n")
    while True:
        try:
            query = get_query()
        except EOFError:
            # User hit Ctrl+d; quit
            sys.stdout.write("\n")
            break

        if query == "exit;":
            sys.stdout.write("\n")
            break
        if query:
            process_query(conn, query)
