# !/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    Copyright (C) 2023  Black-pearl2498

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
This module implements the ldap authentication
"""

from ldap import (
    SCOPE_BASE,
    SCOPE_SUBTREE,
    LDAPError,
    LDAPException,
    initialize,
    VERSION3,
    INVALID_CREDENTIALS,
)
from ldap.ldapobject import LDAPObject
from argparse import ArgumentParser
from typing import List, Dict, Tuple
from sys import stderr, exit
from os import environ
from json import dumps


def get_user_groups(
    ldap_client: LDAPObject, user_attributes: Dict[str, List[str]]
) -> List[str]:
    """
    Gets the groups the user is a member of, and their ids
    """
    groups_dns = user_attributes.get("memberOf", [])
    groups_ids = []
    for group_dn in groups_dns:
        group_attributes = ldap_client.search_s(group_dn, SCOPE_BASE)
        if not group_attributes:
            continue
        _, group_attributes = group_attributes[0]
        group_id = group_attributes.get("cn", [None])[0]
        if group_id:
            groups_ids.append(group_id)
    return groups_ids


def user_authentication(
    ldap_client: LDAPObject, username: str
) -> Dict[str, str]:
    """
    Recovers the user's id and attributes by specifiying the search base,
    based on the ldap tree
    dc=example,dc=com
      |
      ou=users
        |
       uid=jdoe
        |...
    """
    # Specify the search base
    search_base = "dc=C2-EX-MACHINA, dc=com, ou=users"
    # Specify the filter
    search_filter = f"(uid={username})"
    # Search fo the user
    try:
        result: List[Tuple[str, Dict[str, List[str]]]] = ldap_client.search_s(
            search_base, SCOPE_SUBTREE, search_filter
        )
    except LDAPError as error:
        print(f"LDAP error: {error}")
        result = None

    if result:
        # get the first result (there should only be one)
        _, user_attributes = result[0]
        # get the user ip
        user_ip = user_attributes.get("ip", [None])[0]
        # get the user id
        user_id = user_attributes.get("uid", [None])[0]
        groups_id = get_user_groups(ldap_client, user_attributes)
        # get the user permissions
        categories = user_attributes.get("categories", [])
        scripts = user_attributes.get("scripts", [])

        return {
            "ip": user_ip,
            "id": user_id,
            "name": username,
            "groups": ",".join(groups_id),
            "categories": ",".join(categories),
            "scripts": ",".join(scripts),
        }

    return {
        "id": "0",
        "name": "Not Authenticated",
        "ip": environ["REMOTE_IP"],
        "groups": "0",
        "categories": ["*"],
        "scripts": ["*"],
    }


def main() -> int:
    """
    Takes the username, the password and the api-key as arguments,
    creates an ldap client instance and binds the ldap client
    with the username and password,
    finally, recovers the user's data and dumps it in a json file
    for WebScripts
    """
    parser = ArgumentParser(description="Authenticates to the C2 ldap server")
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")
    parser.add_argument("-k", "--api-key")

    args = parser.parse_args()
    username = args.username
    password = args.password
    api_key = args.api_key

    # Creates an LDAP client instance
    try:
        ldap_server = "ldapC2.com"  # (à définir)
        ldap_client = initialize(ldap_server)
        ldap_client.protocol_version = VERSION3
    except LDAPException as error:
        print(f"LDAP error:{error}", file=stderr)
        return 3

    # Binds the LDAP client with the username and password
    try:
        ldap_client.bind(username, password, api_key)
    except INVALID_CREDENTIALS:
        print("Invalid credentials or key", file=stderr)
        return 2

    print(dumps(user_authentication(ldap_client, username)))
    return 0


if "__name__" == "__main__":
    exit(main())
