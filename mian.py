import json
import time
from datetime import datetime

import pandas as pd

import sql
from market.agents.brand import Brand
from market.model import Market
from market.utils.print_time import print_time
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', -1)  # or 199


class ModelRun:
    def __init__(self, student_id: str, student_init_json_path: str, k: int, p: float,
                 system_setting_json_path="data/system_setting.json"):
        '''
        :param student_id: 学生id
        :param student_init_json_path: 学生初始化决策json文件地址
        :param system_setting_json_path: 系统初始化参数json文件地址
        :param k: 小世界网络参数k，邻居个数
        :param p: 小世界网络参数p，重连概率
        '''
        # 初始化学生数据库
        sql.init_db(student_id=student_id)

        # 初始化模型
        ## 获取系统参数（由教师端进行控制）
        with open(system_setting_json_path, 'r', encoding='utf-8') as load_f:
            system_setting = json.load(load_f)
            print_time("已加载系统参数")

        market = Market(k, p, system_setting, student_id)
        print_time("正在初始化模型---预计1min")

        time1 = time.time()
        for i in range(91):
            market.step()

        print_time("已完成模型初始化")
        self.plot_market_share(market)
        print_time("当前市场环境已向学生展示")

        # 获取运行周期
        n_period = system_setting[0]["n_decision_period"]
        for i in range(n_period):

            print_time("请学生进行第{}期决策".format(i))
            if i == 0:
                student_init_json_path = input("请输入第{}期决策文件：".format(i))
                ## 获取消费者决策数据文件
                ## 前端收集整理并整合成json格式文件, 文件样例：data/student_init.json
                with open(student_init_json_path, 'r', encoding='utf-8') as load_f:
                    my_brand = json.load(load_f)
                    print_time("已加载第{}期学生决策".format(i))
                market.student_strategy_init(my_brand)

            if i > 0 and i <= n_period:
                student_strategy_json_path = input("请输入第{}期决策文件：".format(i))
                ## 获取消费者决策数据文件
                ## 前端收集整理并整合成json格式文件，文件样例：data/student_strategy.json
                ## 每一期需要一个决策文件
                with open(student_strategy_json_path, 'r', encoding='utf-8') as load_f:
                    student_strategy = json.load(load_f)
                    print_time("已加载第{}期学生决策".format(i))
                market.student_strategy_change(student_strategy)

            print_time("正在向模型加载学生第{}期决策".format(i))
            print_time("开始第{}期决策模拟".format(i))
            for j in range(90):
                market.step()
            print_time("已完成第{}期模拟".format(i))
            self.plot_market_share(market)
            print_time("当前市场环境已向学生展示")

        time2 = time.time()
        print(time2 - time1)
        print_time("模型运行结束！")

    def plot_market_share(self, model):
        data = model.datacollector.get_model_vars_dataframe()
        temp = data.to_dict()
        # print(temp)
        info = []
        for i in range(len(temp['data'])):
            # print(temp['data'][i])
            info.append(temp['data'][i])
        # print(data)
        # print(info)
        plot_data = pd.DataFrame(info)
        if len(plot_data.columns) == 6:
            plot_data.columns=['产品1', '产品2', '产品3', '产品4', '产品5', '产品6']
        else:
            plot_data.columns = ['产品1', '产品2', '产品3', '产品4', '产品5', '产品6', '产品7']
        p = plot_data[['产品1', '产品2', '产品3']]
        # print(p)

        # plot_data.plot()
        p.plot()
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 设置正常显示符号
        plt.show()
