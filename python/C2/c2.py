#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This tool is a secure C2 working in WebScripts
#    environment for SOC and Blue Team automations
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
###################

"""
This WebScripts module is used to send order to C2-EX-MACHINA client/agent.
"""

__version__ = "0.0.1"
__author__ = "KrysCat-KitKat, C2-EX-MACHINA"
__author_email__ = "c2-ex-machina@proton.me"
__maintainer__ = "KrysCat-KitKat, C2-EX-MACHINA"
__maintainer_email__ = "c2-ex-machina@proton.me"
__description__ = """
This tool is a secure C2 working in WebScripts environment
for SOC and Blue Team automations
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/C2-EX-MACHINA/C2/"

copyright = """
C2  Copyright (C) 2023  C2-EX-MACHINA
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["order"]

print(copyright)

from json import dumps
from os import _Environ
from os.path import join
from sqlite3 import connect
from datetime import datetime
from collections import namedtuple
from time import time, mktime, strptime
from typing import Dict, Union, TypeVar, List, Tuple, Iterable

Server = TypeVar("Server")
User = TypeVar("User")
Logs = TypeVar("Logs")
Task = namedtuple(
    "Task",
    [
        "type",
        "user",
        "name",
        "description",
        "data",
        "filename",
        "timestamp",
        "timeout",
        "id",
        "after",
    ],
)


def save_orders_results(
    environ: _Environ,
    results: Dict[str, List[Dict[str, Union[str, int]]]],
    hostname: str,
    key: str,
) -> None:
    """
    This function performs SQL requests to store
    order results in C2 database.
    """

    connection = connect(
        join(environ["WEBSCRIPTS_DATA_PATH"], "c2_ex_machina.db")
    )
    cursor = connection.cursor()
    for result in results["Tasks"]:
        cursor.execute(
            'UPDATE "OrderResult" SET "data" = ?, "error" = ?, "exitcode" = ?, "responseDate" = ?, "startDate" = ?, "endDate" = ? WHERE ("instance" = ? AND "agent" = (SELECT "id" FROM "Agent" WHERE "name" = ? AND "key" = ?) AND "responseDate" IS NULL);',
            (
                result["Stdout"],
                result["Stderr"],
                result["Status"],
                datetime.now(),
                datetime.fromtimestamp(result["StartTime"]),
                datetime.fromtimestamp(result["EndTime"]),
                result["Id"],
                hostname,
                key,
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()


def get_tasks_by_agent(
    environ: _Environ,
    logger: Logs,
    key: str,
    hostname: str,
    system: str,
    user: User,
) -> List[Task]:
    """
    This function performs SQL requests to check
    agent key/hostname and to get tasks for the agent.
    """

    connection = connect(
        join(environ["WEBSCRIPTS_DATA_PATH"], "c2_ex_machina.db")
    )
    cursor = connection.cursor()
    cursor.execute(
        'SELECT "id" FROM "Agent" WHERE "name" = ? AND "key" = ?;',
        (
            hostname,
            key,
        ),
    )

    if not cursor.fetchone():
        cursor.execute(
            'SELECT "id" FROM "Agent" WHERE "name" = ?', (hostname,)
        )
        if cursor.fetchone():
            logger.warning(
                f"Authentication error with agent {hostname!r} and {key!r}."
            )
            return None
        logger.warning(f"Create new agent {hostname!r}.")
        cursor.execute(
            'INSERT INTO "OS" ("name") VALUES (?) ON CONFLICT DO NOTHING;',
            (system,),
        )
        cursor.execute(
            'INSERT INTO "Agent" ("name", "key", "ips", "os") VALUES (?, ?, ?, (SELECT "id" FROM "OS" WHERE "name" = ?)) ON CONFLICT ("name") DO NOTHING;',
            (
                hostname,
                key,
                environ["REMOTE_IP"],
                system,
            ),
        )
        cursor.execute(
            'INSERT INTO "User" ("name", "user") VALUES (?, ?) ON CONFLICT DO NOTHING;',
            (
                user.name,
                user.id,
            ),
        )
        cursor.execute(
            'INSERT INTO "AgentsGroup" ("name", "description") VALUES (?, ?) ON CONFLICT DO NOTHING;',
            (
                system,
                "All " + repr(system) + " agents",
            ),
        )
        cursor.execute(
            'INSERT INTO "UnionGroupAgent" ("agent", "group", "user") VALUES ((SELECT "id" FROM "Agent" WHERE "name" = ?), (SELECT "id" FROM "AgentsGroup" WHERE "name" = ?), (SELECT "id" FROM "User" WHERE "name" = ?));',
            (
                hostname,
                system,
                user["name"],
            ),
        )
        cursor.execute(
            'SELECT "id" FROM "GroupOrders" WHERE "group" = ? AND "add_to_new_agent";',
            (system,),
        )
        tasks = cursor.fetchall()
        for task in tasks:
            cursor.execute(
                'INSERT INTO "OrderResult" ("agent", "instance") VALUES (?, (SELECT "id" FROM "Agent" WHERE "name" = ?), ?);',
                (hostname, task[0]),
            )

    cursor.execute(
        'SELECT * FROM TasksToExecute WHERE "agent" = ?;', (hostname,)
    )
    orders = cursor.fetchall()

    for order in orders:
        cursor.execute(
            'UPDATE "OrderResult" SET "requestDate" = ? WHERE ("instance" = ? AND "agent" = (SELECT "id" FROM "Agent" WHERE "name" = ? AND "key" = ?) AND "requestDate" IS NULL);',
            (datetime.now(), order[8], hostname, key),
        )

    connection.commit()
    cursor.close()
    connection.close()
    return [Task(*order[:10]) for order in orders]


def malware_encode(data: Dict[str, Union[str, Dict[str, str]]]) -> str:
    """
    This function encodes response object for Malware Order API.
    """

    raise NotImplementedError


def malware_decode(data: Dict[str, Union[str, Dict[str, str]]]) -> str:
    """
    This function decodes results data for Malware Order API.
    """

    raise NotImplementedError


def get_orders(
    environ: _Environ,
    logger: Logs,
    next_request_time: int,
    key: str,
    hostname: str,
    system: str,
    user: User,
) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    This function returns formatted orders for an agent.
    """

    logger.debug("Get tasks for " + hostname + " (" + system + ")")
    tasks = get_tasks_by_agent(environ, logger, key, hostname, system, user)

    if tasks is None:
        return None

    api_webscript = {
        "NextRequestTime": int(time() + next_request_time) + 1,
        "Tasks": [
            {
                "Type": task.type,
                "User": task.user,
                "Name": task.name,
                "Description": task.description,
                "Data": task.data,
                "Filename": task.filename,
                "Timestamp": int(
                    mktime(strptime(task.timestamp, "%Y-%m-%d %H:%M:%S"))
                )
                if task.timestamp
                else task.timestamp,
                "Timeout": task.timeout,
                "Id": task.id,
                "After": task.after,
            }
            for task in tasks
        ],
    }

    return api_webscript


def order(
    environ: _Environ,
    user: User,
    server: Server,
    agent_id: str,
    arguments: Dict[str, Dict[str, str]],
    inputs: None,
    csrf_token: str = None,
) -> Tuple[str, Dict[str, str], Union[str, Iterable[bytes]]]:
    """
    This function generates and returns response for Agent Order API.
    """

    logger = server.logs
    user_agent = environ["HTTP_USER_AGENT"]
    user_agent_split = user_agent.split()
    is_agent = user_agent.startswith("Agent-C2-EX-MACHINA ")
    if not is_agent or len(user_agent_split) != 4:
        logger.info("Invalid user agent for C2-EX-MACHINA agent.")
        return (
            "403",
            {},
            b"",
        )

    hostname = user_agent_split[-1]

    if arguments:
        results = arguments if is_agent else malware_decode(arguments)
        for task in results.get("Tasks", []):
            for key in (
                "Id",
                "Stdout",
                "Stderr",
                "Status",
                "StartTime",
                "EndTime",
            ):
                if task.get(key) is None:
                    logger.error(
                        "There is a key missing in the agent response: " + key
                    )
                    return (
                        "400",
                        {},
                        (),
                    )
        logger.debug("Save new order(s) result for agent " + hostname)
        save_orders_results(environ, results, hostname, agent_id)

    data = get_orders(
        environ,
        logger,
        getattr(server.configuration, "c2_next_request_time", 300),
        agent_id,
        hostname,
        user_agent_split[2].strip("()").title(),
        user,
    )
    if data is None:
        return (
            "403",
            {},
            b"",
        )

    return (
        "200 OK",
        {},
        (dumps if is_agent else malware_encode)(data),
    )
