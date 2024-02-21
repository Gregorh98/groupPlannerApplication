import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

import dateutil.parser as dp

load_dotenv()


def getConn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )


def getUserId(name, groupCode):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "select id from group_planner.users where name = %s and group_code = %s"
            data = (name, groupCode,)

            cursor.execute(sql, data)
            id = cursor.fetchone()
            return id if id == None else id[0]


def addUser(name, groupCode):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "insert into group_planner.users (name, group_code) values (%s, %s)"
            data = (name, groupCode,)

            cursor.execute(sql, data)
            conn.commit()


def getGroupMemberNames(groupCode, name):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "select name from group_planner.users where group_code = %s and name != %s"
            data = (groupCode, name,)

            cursor.execute(sql, data)
            names = cursor.fetchall()
            return names


def getUsersFreeOnDay(date, groupCode):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT name FROM group_planner.users WHERE id IN (SELECT user_id FROM group_planner.entries WHERE date = %s) and group_code = %s;"
            data = (date, groupCode,)

            cursor.execute(sql, data)
            names = cursor.fetchall()
            names = [name[0] for name in names]
            return names


def getTopDays(groupCode):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT date, COUNT(date) as popularity FROM group_planner.entries INNER JOIN group_planner.users ON group_planner.entries.user_id = group_planner.users.id WHERE group_code = %s GROUP BY group_code, date ORDER BY popularity DESC LIMIT 5;"
            data = (groupCode,)

            cursor.execute(sql, data)
            dates = cursor.fetchall()
            return dates


def addDates(dates, userid):
    with getConn() as conn:
        with conn.cursor() as cursor:
            print(dates)
            for d in dates:
                dateInQuestion = dp.isoparse(d).date()
                sql = "INSERT INTO group_planner.entries (user_id, date, available) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM group_planner.entries WHERE user_id = %s AND date = %s);"
                data = (userid, dateInQuestion, True, userid, dateInQuestion)

                cursor.execute(sql, data)

            conn.commit()


def getDatesForUser(userId):
    with getConn() as conn:
        with conn.cursor() as cursor:
            # TODO: Stop this being generic and applying over all groups
            sql = "select date from group_planner.entries where user_id = %s"
            data = (userId,)

            cursor.execute(sql, data)
            dates = [str(r[0]) for r in cursor.fetchall()]
            return dates


def getGroupUserCount(groupCode):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "select count(id) as memberCount from group_planner.users where group_code = %s"
            data = (groupCode,)

            cursor.execute(sql, data)
            count = cursor.fetchone()
            return count[0] if count is not None else 0


def removeDates(dates, userid):
    with getConn() as conn:
        with conn.cursor() as cursor:
            for d in dates:
                dateInQuestion = dp.isoparse(d).date()
                sql = "DELETE FROM group_planner.entries WHERE user_id = %s AND date = %s;"
                data = (userid, dateInQuestion)

                cursor.execute(sql, data)
            conn.commit()


def changeScreenName(userId, newName):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "UPDATE group_planner.users SET name = %s WHERE id = %s;"
            data = (newName.upper(), userId)

            cursor.execute(sql, data)
            conn.commit()


def removeUser(userId, groupCode):
    with getConn() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM group_planner.entries WHERE user_id = %s"
            data = (userId,)
            cursor.execute(sql, data)

            sql = "DELETE FROM group_planner.users WHERE id = %s"
            data = (userId,)
            cursor.execute(sql, data)

        conn.commit()
