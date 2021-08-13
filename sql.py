import sqlite3
import pandas as pd
import os, shutil


def init_db(student_id):
    if os.path.exists("data/simulation_{}.db".format(student_id)):
        os.remove("data/simulation_{}.db".format(student_id))
        shutil.copy("data/simulation.db", "data/simulation_{}.db".format(student_id))
    else:
        shutil.copy("data/simulation.db", "data/simulation_{}.db".format(student_id))
    connect_db(student_id)


def init_teacher_db():
    if not os.path.exists("data/teacher_setting.db"):
        print("！请先加载教师配置文件")
    else:
        conn = sqlite3.connect("data/teacher_setting.db")
        print("====》已加载教师配置文件")
        return conn


def connect_db(student_id):
    conn = sqlite3.connect("data/simulation_{}.db".format(student_id))
    return conn


def get_data(sql, student_id):
    conn = connect_db(student_id)
    cursor = conn.cursor()
    cursor.execute(sql)
    values = cursor.fetchall()
    cursor.close()
    conn.close()
    return values


def get_data_df(sql, student_id):
    conn = connect_db(student_id)
    df = pd.read_sql_query(sql, conn)
    return df
