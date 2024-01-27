--    This file creates the C2 database.
--    Copyright (C) 2023  Christophe SUBLET (KrysCat-KitKat)

--    This program is free software: you can redistribute it and/or modify
--    it under the terms of the GNU General Public License as published by
--    the Free Software Foundation, either version 3 of the License, or
--    (at your option) any later version.

--    This program is distributed in the hope that it will be useful,
--    but WITHOUT ANY WARRANTY; without even the implied warranty of
--    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--    GNU General Public License for more details.

--    You should have received a copy of the GNU General Public License
--    along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- Insert User
INSERT INTO "User" ("name", "user") VALUES (?, ?) ON CONFLICT DO NOTHING;

-- Insert OS
INSERT INTO "OS" ("name") VALUES (?) ON CONFLICT DO NOTHING;

-- Insert Agent
INSERT INTO "Agent" ("name", "key", "ips", "os")
VALUES (?, ?, ?, (SELECT "id" FROM "OS" WHERE "name" = ?))
ON CONFLICT ("name") DO NOTHING;

-- Insert Group
INSERT INTO "AgentsGroup" ("name", "description") VALUES (?, ?) ON CONFLICT DO NOTHING;

-- Insert Agent into Group
INSERT INTO "UnionGroupAgent" ("agent", "group", "user")
VALUES (
    (SELECT "id" FROM "Agent" WHERE "name" = ?),
    (SELECT "id" FROM "AgentsGroup" WHERE "name" = ?),
    (SELECT "id" FROM "User" WHERE "name" = ?)
);

-- Insert OrderTemplate
INSERT INTO "OrderTemplate" (
    "type",
    "user",
    "data",
    "readPermission",
    "executePermission",
    "after",
    "name",
    "description"
    "filename",
    "timeout"
) VALUES (
    (SELECT "id" FROM "OrderType" WHERE "name" = ?),
    (SELECT "id" FROM "User" WHERE "name" = ?),
    ?,
    ?,
    ?,
    (SELECT "id" FROM "OrderTemplate" WHERE "name" = ?),
    ?,
    ?,
    ?,
    ?
);

-- Insert OrderInstance
INSERT INTO "OrderInstance" (
    "startDate",
    "user",
    "orderTargetType",
    "template",
    "add_to_new_agent"
) VALUES (
    ?,
    (SELECT "id" FROM "User" WHERE "name" = ?),
    (SELECT CASE WHEN "Agent" = "Agent" THEN 1 WHEN "Group" = "Group" THEN 0 END AS "TargetType"),
    (SELECT "id" FROM "OrderTemplate" WHERE "name" = ? AND "executePermission" <= ?),
    ?
);

-- Insert OrderToGroup
INSERT INTO "OrderToGroup" (
    "group",
    "instance"
) VALUES (
    (SELECT "id" FROM "AgentsGroup" WHERE "name" = ?),
    last_insert_rowid()
);

-- Insert OrderToAgent
INSERT INTO "OrderToAgent" (
    "agent",
    "instance"
) VALUES (
    (SELECT "id" FROM "Agent" WHERE "name" = ?),
    last_insert_rowid()
);

-- Insert OrderResult
INSERT INTO "OrderResult" (
    "data",
    "error",
    "exitcode",
    "requestDate",
    "responseDate",
    "startDate",
    "endDate",
    "agent",
    "instance"
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?
);

-- Insert OrderResult base
INSERT INTO "OrderResult" (
    "agent",
    "instance"
) VALUES (
    (SELECT "id" FROM "Agent" WHERE "name" = ?), ?
);

-- Insert OrderResult data
UPDATE "OrderResult" SET
    "requestDate" = ?
WHERE (
    "instance" = ? AND
    "agent" = (SELECT "id" FROM "Agent" WHERE "name" = ? AND "key" = ?) AND
    "requestDate" IS NULL
);

-- Insert OrderResult data
UPDATE "OrderResult" SET
    "data" = ?,
    "error" = ?,
    "exitcode" = ?,
    "responseDate" = ?,
    "startDate" = ?,
    "endDate" = ?
WHERE (
    "instance" = ? AND
    "agent" = (SELECT "id" FROM "Agent" WHERE "name" = ? AND "key" = ?) AND
    "responseDate" IS NULL
);