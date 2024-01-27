#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    Copyright (C) 2023  C2-EX-MACHINA

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##################

"""
This script stores a new OrderTemplate in C2-EX-MACHINA database.
"""

from argparse import ArgumentParser, Namespace
from collections import namedtuple
from sys import exit, argv, stdin
from base64 import b64decode
from sqlite3 import connect
from time import strftime
from os.path import join
from json import loads
from typing import Set
from os import environ

OrderTemplate = namedtuple(
    "OrderTemplate",
    [
        "type",
        "user",
        "data",
        "readpermission",
        "executepermission",
        "after",
        "name",
        "description",
        "filename",
        "timeout",
    ],
)


def insert_order_template(order_template: OrderTemplate, id_: int) -> None:
    """
    This function inserts an OrderTemplate into the database.
    """

    connection = connect(
        join(environ["WEBSCRIPTS_DATA_PATH"], "c2_ex_machina.db")
    )
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO "User" ("name", "user") VALUES (?, ?) ON CONFLICT DO NOTHING;',
        (
            order_template.user,
            id_,
        ),
    )
    cursor.execute(
        'INSERT INTO "OrderTemplate" ("type","user","data","readPermission","executePermission","after","name","description","filename","timeout") VALUES ((SELECT "id" FROM "OrderType" WHERE "name" = ?),(SELECT "id" FROM "User" WHERE "name" = ?),?,?,?,(SELECT "id" FROM "OrderTemplate" WHERE "name" = ?),?,?,?,?);',
        order_template,
    )
    connection.commit()
    cursor.close()
    connection.close()


def get_order_types() -> Set[str]:
    """
    This function returns orders types.
    """

    connection = connect(
        join(environ["WEBSCRIPTS_DATA_PATH"], "c2_ex_machina.db")
    )
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM OrderType;")
    order_types = {x[0] for x in cursor.fetchall()}
    cursor.close()
    connection.close()

    return order_types


def parse_args() -> Namespace:
    """
    This function parses the variables passed as arguments
    """

    order_types = get_order_types()

    max_privilege_level = max(loads(environ["USER"])["groups"])

    parser = ArgumentParser(
        description=(
            "This script stores a new OrderTemplate in C2-EX-MACHINA database."
        )
    )
    add_argument = parser.add_argument
    add_argument("name", type=str, help="The new order template name.")
    add_argument(
        "description",
        type=str,
        help="The new order template description.",
    )
    add_argument(
        "type",
        choices=order_types,
        help="Operation type name (like: 'COMMAND', 'DOWNLOAD', 'UPLOAD', ...)",
    )
    add_argument(
        "--read-permission",
        default=max_privilege_level,
        type=int,
        help="Minimum privilege level (group level) to read task output.",
    )
    add_argument(
        "--execute-permission",
        default=max_privilege_level,
        type=int,
        help="Minimum privilege level (group level) to start task execution.",
    )
    add_argument(
        "--after",
        type=str,
        help=(
            "Order Id or null, to execute this order after any precedent order"
        ),
    )
    add_argument(
        "--filename",
        type=str,
        help="Filename for UPLOAD file destination path.",
    )
    add_argument(
        "--timeout", type=int, help="Timeout to stop the task if is blocked."
    )

    return parser.parse_args()


def main() -> int:
    """
    This is the main function to starts the script from the command line.
    """

    if "--list" in argv:
        types = get_order_types()
        print("Types:", "\n\t" + "\n\t".join(repr(type_) for type_ in types))
        return 2

    arguments = parse_args()
    data = (
        b64decode(stdin.buffer.read())
        if environ.get("HTTP_COOKIE") is not None
        else stdin.buffer.read()
    )

    if len(data) > 255:
        filename = (
            "filename_" + strftime("%Y_%m_%d_%H_%M_%S") + ".file.c2_ex_machina"
        )
        with open(
            join(environ["WEBSCRIPTS_DATA_PATH"], "c2_data_files", filename),
            "wb",
        ) as file:
            file.write(data)
        data = filename
    else:
        data = data.decode("latin1")

    user = loads(environ["USER"])
    order = OrderTemplate(
        arguments.type,
        user["name"],
        data,
        arguments.read_permission,
        arguments.execute_permission,
        arguments.after,
        arguments.name,
        arguments.description,
        arguments.filename,
        arguments.timeout,
    )

    insert_order_template(order, user["id"])
    print("Done.")
    return 0


if __name__ == "__main__":
    exit(main())
