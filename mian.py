import json

import sql
from market.model import Market


class ModelRun:
    def __init__(self, student_id, student_init_json_path, k, p):
        '''
        :param student_id: 学生id
        :param student_init_json_path: 学生初始化决策json文件地址
        :param k: 小世界网络参数k，邻居个数
        :param p: 小世界网络参数p，重连概率
        '''
        # 初始化学生数据库
        sql.init_db(student_id=student_id)

        # 初始化模型

        ## 获取系统参数（由教师端进行控制）
        with open("data/system_setting.json", 'r', encoding='utf-8') as load_f:
            system_setting = json.load(load_f)

        ## 获取消费者决策数据文件（由学生进行创建）
        with open(student_init_json_path, 'r', encoding='utf-8') as load_f:
            new_brand = json.load(load_f)

        market = Market(k, p, system_setting, student_id)

        for i in range(3):
            market.step()