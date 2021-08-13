import json

import sql
from market.model import Market


class ModelRun:
    def __init__(self, student_id, k, p):

        # 初始化学生数据库
        sql.init_db(student_id=student_id)

        # 初始化模型
        with open("data/system_setting.json", 'r', encoding='utf-8') as load_f:
            system_setting = json.load(load_f)

        with open("data/student_init.json", 'r', encoding='utf-8') as load_f:
            new_brand = json.load(load_f)

        market = Market(k, p, system_setting, student_id)

        for i in range(3):
            market.step()