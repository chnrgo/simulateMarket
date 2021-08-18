import sqlite3
import pandas as pd
import os, shutil


def init_db(student_id: str):
    """
    :param student_id: 学生id
    :return: 当前学生的sqlite数据文件，文件保存在data文件夹下，文件名为simulation_{student_id}.db
    """

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

def insert(sql, student_id):
    conn = connect_db(student_id)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()
