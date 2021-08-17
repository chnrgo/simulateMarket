import json
import time
from datetime import datetime

import modin.pandas as pd

import sql
from market.agents.brand import Brand
from market.model import Market
from market.utils.print_time import print_time
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', -1)  # or 199


class ModelRun:
    def __init__(self, student_id: str, student_init_json_path: str, k: int, p: float):
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
            print(system_setting)
            print_time("已加载系统参数")

        ## 获取消费者决策数据文件（由学生进行创建）
        with open(student_init_json_path, 'r', encoding='utf-8') as load_f:
            new_brand = json.load(load_f)
            print_time("已加载学生决策")

        market = Market(k, p, system_setting, student_id)
        print_time("已完成模型初始化")


        n_period = system_setting[0]["n_decision_period"]

        time1 = time.time()
        for i in range(90):
            market.step()


        data = market.datacollector.get_model_vars_dataframe()
        brand_market_share = data['BrandMarketShare']

        for i in range(len([x for x in market.schedule.agents if isinstance(x, Brand)])):
            data["{}".format(brand_market_share[0][i][1])] = data['BrandMarketShare'].map(lambda x: x[i][2])

        plot_data = data[[x.brand_name for x in market.schedule.agents if isinstance(x, Brand)]]
        print(plot_data)
        plot_data.plot()
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 设置正常显示符号
        plt.show()

        time2 = time.time()
        print(time2 - time1)
        print_time("模型运行结束！")