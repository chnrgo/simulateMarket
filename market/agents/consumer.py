import random

from mesa import Agent
import sql
import random
import pandas as pd
from market.utils.topsis import topsis

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
pd.set_option('expand_frame_repr', False)

class Consumer(Agent):
    def __init__(self, unique_id, model, name, age, gender, skin_type, income_level, prefer_brand, prefer_gongxiao,
                 node_id):
        super(Consumer, self).__init__(unique_id, model)
        self.consumer_id = unique_id
        self.name = name
        self.age = self.age_matching(age)
        self.gender = gender
        self.skin_type = skin_type
        self.income_level = income_level
        self.prefer_brand = prefer_brand
        self.prefer_gongxiao = prefer_gongxiao
        self.node_id = node_id

        self.state = "potentialUser"

        self.intention_threshold = random.random()

        self.duration = 30

        self.product = None

        self.ad_infect_list = []

        self.neighbor_infect_list = []

        self.buy_way = "online"

    def step(self) -> None:
        # self.state_change(self.state)
        data = self.create_topsis_data()

        topsis_sort_data = topsis(data)[0]
        topsis_sort_data.sort_values(by=['排序'], ascending=True, inplace=True)


        print(topsis_sort_data)
        # df = ['0', '1001', '4001', '900001', 20, 'online', 'ad']
        # self.connect_with_neighbors(df)
        #
        # self.update()

    def state_change(self, state):
        '''
        消费者状态变迁函数
        :return: self.state
        '''
        states = {
            "potentialUser": self.potentialUser,
            "wantsToBuy": self.wantsToBuy,
            "User": self.user
        }
        method = states.get(state)
        if method:
            method()

    def potentialUser(self):

        info = self.get_product_info()

        print("potential")

    def wantsToBuy(self):

        # 获取data
        data = []
        print(topsis(data))

        print("wants")

    def user(self):
        if self.duration >= 0:
            self.duration = self.duration - 1
        else:
            self.state = "potentialUser"

    def connect_with_neighbors(self, df):
        neighbor_nodes = self.model.consumer_grid.get_neighbors(self.node_id)
        neighbors = self.model.consumer_grid.get_cell_list_contents(neighbor_nodes)
        for i in neighbors:
            i.neighbor_infect(df)

    def get_product_info(self):
        student_id = self.model.student_id
        query = "SELECT * FROM product"
        df = sql.get_data_df(query, student_id)
        return df

    def create_topsis_data(self):
        info = self.get_product_info()
        info['consumer_age'] = self.age
        info['consumer_skin'] = self.skin_type
        info['consumer_prefer_brand'] = self.prefer_brand
        info['consumer_prefer_gongxiao'] = self.prefer_gongxiao

        info['年龄匹配分'] = info.apply(lambda x: 5 if x['consumer_age'] in x['fit_age'] else 1, axis=1)
        info['肤质匹配分'] = info.apply(lambda x: self.skin_type_match(x['skin_type'], x['consumer_skin']), axis=1)
        #info['功效偏好分'] = info.apply(lambda )

        info2 = info.set_index('id')

        # 邻居偏好分


        data = info2[['年龄匹配分', '肤质匹配分']]

        print(data)
        data['年龄匹配分'].astype('float')
        data['肤质匹配分'].astype('float')

        print(data.dtypes)
        return data

    def gongxiao_match(self, seq1, seq2):
        res = []
        for x in seq2:
            if x in seq1:
                res.append(x)

        return len(res)


    def skin_type_match(self, seq1, seq2):
        res = []
        if seq2 == "any" or seq1 == "any":
            return 5
        else:
            for x in seq2:
                if x in seq1:
                    res.append(x)
            return len(res) + 1


    def ad_infect(self, df):
        self.ad_infect_list.append(df)

    def neighbor_infect(self, df):
        self.neighbor_infect_list.append(df)

    def update(self):
        for i in self.neighbor_infect_list:
            if i[4] < 0:
                self.neighbor_infect_list.remove(i)
                print(i)
            else:
                i[4] = i[4] - 1
                print(i)

    def age_matching(self, age):
        if age < 18:
            return 'A'
        elif 18 <= age < 22:
            return 'B'
        elif 22 <= age < 25:
            return 'C'
        elif 25 <= age < 30:
            return 'D'
        elif 30 <= age < 35:
            return 'E'
        elif 35 <= age < 45:
            return 'F'
        elif age >= 45:
            return 'G'
