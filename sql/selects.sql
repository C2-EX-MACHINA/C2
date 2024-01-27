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

-- Get Agents in a group
SELECT "name", "os", "ips", "group", "description", "user"
FROM "Groups"
WHERE "Groups"."group" = ?;

-- Get all Orders Instances
SELECT
    "task",
    "description",
    "data",
    "creation",
    "orderType",
    "userCreation",
    "readPermission",
    "executePermission",
    "userExecution",
    "start",
    "requirementTask"
FROM "Orders";

-- Get Orders Instance with Agent
SELECT "task", "agent", "description", "data", "start", "user", "ips", "os"
FROM "AgentOrders";

-- Get Orders Instance by matching Agent
SELECT "task", "agent", "description", "data", "start", "user", "ips", "os"
FROM "AgentOrders"
WHERE "agent" LIKE '%?%';

-- Get Orders Instance with Group
SELECT "task", "group", "groupDescription", "taskDescription", "data", "start", "user"
FROM "GroupOrders";

-- Get Orders Instance for new agent of a specific Group
SELECT "task", "group", "groupDescription", "description", "data", "start", "user"
FROM "GroupOrders"
WHERE "group" = ? AND "add_to_new_agent";

-- Get Orders Instance by matching Group
SELECT "task", "group", "groupDescription", "description", "data", "start", "user"
FROM "GroupOrders"
WHERE "group" LIKE '%?%';

-- Get Agents Orders by matching Task
SELECT "task", "agent", "description", "data", "start", "user", "ips", "os"
FROM "AgentOrders"
WHERE "task" LIKE '%?%';

-- Get Groups Orders by matching Task
SELECT "task", "group", "groupDescription", "description", "data", "start", "user"
FROM "GroupOrders"
WHERE "task" LIKE '%?%';

-- List Agents
SELECT "Agent"."name" AS "name", "OS"."name" AS "os", "Agent"."ips" AS "ips"
FROM "Agent"
INNER JOIN "OS" ON "OS"."id" = "Agent"."os";

-- List Groups
SELECT "name", "description" FROM "AgentsGroup";

-- List users
SELECT "name" FROM "User";

-- Get tasks launched by a user
SELECT
    "task",
    "description",
    "data",
    "start"
FROM "Orders"
WHERE "userExecution" = ?;

-- Get tasks created by a user
SELECT
    "OrderTemplate"."name" AS "task",
    "OrderTemplate"."description" AS "description",
    "OrderTemplate"."data" AS "data",
    "OrderTemplate"."readPermission" AS "readPermission",
    "OrderTemplate"."executePermission" AS "executePermission"
FROM "OrderTemplate"
INNER JOIN "User" ON "User"."id" = "OrderTemplate"."user"
WHERE "User"."name" = ?;

-- Get failed tasks
SELECT
    "OrderTemplate"."name" AS "name",
    "OrderTemplate"."description" AS "description",
    "OrderResult"."exitcode" AS "exitcode",
    "OrderResult"."data" AS "data",
    "OrderResult"."error" AS "error"
FROM "OrderResult"
INNER JOIN ON "OrderResult"."instance" = "OrderInstance"."id"
INNER JOIN ON "OrderInstance"."template" = "OrderTemplate"."id"
INNER JOIN ON "OrderResult"."agent" = "Agent"."id"
WHERE "OrderResult"."exitcode" != 0
ORDER BY "OrderResult"."responseDate", "OrderResult"."endDate" DESC;

-- Get failed tasks by user
SELECT
    "OrderTemplate"."name" AS "name",
    "OrderTemplate"."description" AS "description",
    "OrderResult"."exitcode" AS "exitcode",
    "OrderResult"."data" AS "data",
    "OrderResult"."error" AS "error"
FROM "OrderResult"
INNER JOIN ON "OrderResult"."instance" = "OrderInstance"."id"
INNER JOIN ON "OrderInstance"."template" = "OrderTemplate"."id"
INNER JOIN ON "OrderInstance"."user" = "User"."id"
INNER JOIN ON "OrderResult"."agent" = "Agent"."id"
WHERE "OrderResult"."exitcode" != 0 AND "User"."name" = ?
ORDER BY "OrderResult"."responseDate", "OrderResult"."endDate" DESC;

-- Get failed tasks by agent
SELECT
    "OrderTemplate"."name" AS "name",
    "OrderTemplate"."description" AS "description",
    "OrderResult"."exitcode" AS "exitcode",
    "OrderResult"."data" AS "data",
    "OrderResult"."error" AS "error"
FROM "OrderResult"
INNER JOIN ON "OrderResult"."instance" = "OrderInstance"."id"
INNER JOIN ON "OrderInstance"."template" = "OrderTemplate"."id"
INNER JOIN ON "OrderResult"."agent" = "Agent"."id"
WHERE "OrderResult"."exitcode" != 0 AND "Agent"."name" = ?
ORDER BY "OrderResult"."responseDate", "OrderResult"."endDate" DESC;

-- Get tasks by agent
SELECT "exitcode", "task", "taskData", "user", "startDate", "endDate"
FROM "Tasks"
WHERE "agent" = ?
ORDER BY "responseDate", "endDate" DESC;

-- Get instances by templates
SELECT "userExecution", "start", 
FROM "Orders"
WHERE "task" = ?
ORDER BY "start", "creation";

-- List Tasks by matching Group
SELECT "group", "groupDescription", "task", "taskDescription", "data", "start", "user"
FROM "GroupTasks";

-- List Tasks by matching Group
SELECT "group", "groupDescription", "task", "taskDescription", "data", "start", "user"
FROM "GroupTasks"
WHERE "group" LIKE '%?%';

-- Get all agent and tasks not executed
SELECT * FROM InstancesToAgents;

-- Get all tasks not executed for an agent
SELECT * FROM InstancesToAgents WHERE "agent" = ?;

-- Check hostname and key agent
SELECT "id" FROM "Agent" WHERE "name" = ? AND "key" = ?;