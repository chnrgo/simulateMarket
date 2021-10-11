import random
import time

from mesa import Agent
import sql
import random
import pandas as pd
import numpy as np

from market.agents.brand import Brand
from market.agents.product import Product
from market.utils.topsis import topsis

pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180)  # 设置打印宽度(**重要**)
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
        self.intention_threshold = random.random() + 0.3
        self.intention = random.random() * 0.5
        self.duration = 30
        self.product = None
        self.brand = None
        self.neighbors = None
        self.buy_online_prefer = random.uniform(0, 1)
        self.info = None

        # 判定该消费者是否加入市场，进行购买行为
        self.in_market = False

        # 广告偏好系数{'代言直播'，'网页广告'，'搜索引擎', '新媒体', '路演', '店面广告', '印刷品'}
        self.ad_prefer_coef = np.random.rand(7)

    def step(self) -> None:

        # 初始化邻居
        if self.model.schedule.time == 0:
            self.neighbors = self.get_neighbors()
            self.info = self.init_topsis_data()

        #
        if self.model.schedule.time == 1:
            temp = self.info.shape[0]
            df = self.init_topsis_data()
            temp = df.shape[0] - temp
            data = df.iloc[0: temp]
            self.info = pd.concat([self.info, data], axis=0)

        if self.model.schedule.time >= 1 & self.in_market == True:
            self.state_change(self.state)


    def state_change(self, state):
        '''
        消费者状态变迁函数
        消费者在三种状态中切换
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
        if self.intention > self.intention_threshold:
            self.state = "wantsToBuy"
            self.intention = 0
        else:
            self.intention += 0.005

    def wantsToBuy(self):
        if random.random() > 0.7:
            if self.buy():
                self.state = "User"
                self.connect_neighbors()
                self.duration = random.randint(25, 40)

    def user(self):
        if self.duration >= 0:
            self.duration = self.duration - 1
        else:
            self.state = "potentialUser"

    def buy(self):
        data = self.update_topsis_data(self.info)
        topsis_sort_data = topsis(data)[0]
        topsis_sort_data.sort_values(by=['排序'], ascending=True, inplace=True)
        # print(topsis_sort_data)
        product_id = topsis_sort_data.index.values[0]
        self.product = self.get_this_product(product_id)
        # self.product.current_sales_volume = self.product.current_sales_volume + 1

        #判断当前商品是否有货可以购买

        if self.judge_buy():
            brand_id = self.product.belong_brand_id
            self.brand = self.get_this_brand(brand_id)
            return True
        else:
            return False

    def judge_buy(self):
        if self.product.stock > 0:
            #判断当前用户的购买方式
            buy_online_coef = random.random()
            #如果大于0.2,则选择线上购买，否则线下购买
            if buy_online_coef >= 0.2:
                if self.product.online_stock > 0:
                    # 更新该产品库存信息
                    self.product.current_sales_volume = self.product.current_sales_volume + 1
                    self.product.stock = self.product.stock - 1
                    self.product.online_stock = self.product.online_stock - 1
                    # 向产品类中的order_list添加记录
                    buy_info = [self.model.schedule.time, self.consumer_id, self.name, self.product.product_id, self.product.name, "online"]
                    self.product.order_list.append(buy_info)
                    return True
                else:
                    #切换渠道购买
                    if random.random() > 0.5:
                        if self.product.stock - self.product.online_stock > 0:
                            self.product.current_sales_volume = self.product.current_sales_volume + 1
                            self.product.stock = self.product.stock - 1
                            buy_info = [self.model.schedule.time, self.consumer_id, self.name, self.product.product_id,
                                        self.product.name, "offline"]
                            self.product.order_list.append(buy_info)
                            return True
                        else:
                            #未成功购买
                            self.product = None
                            return False
                    else:
                        #未成功购买
                        self.product = None
                        return False

            if buy_online_coef < 0.2:
                if self.product.stock - self.product.online_stock > 0:
                    self.product.current_sales_volume = self.product.current_sales_volume + 1
                    self.product.stock = self.product.stock - 1
                    buy_info = [self.model.schedule.time, self.consumer_id, self.name, self.product.product_id, self.product.name, "offline"]
                    self.product.order_list.append(buy_info)
                    return True
                else:
                    #切换渠道购买
                    if random.random() > 0.5:
                        if self.product.online_stock > 0:
                            # 更新该产品库存信息
                            self.product.current_sales_volume = self.product.current_sales_volume + 1
                            self.product.stock = self.product.stock - 1
                            self.product.online_stock = self.product.online_stock - 1
                            # 向产品类中的order_list添加记录
                            buy_info = [self.model.schedule.time, self.consumer_id, self.name, self.product.product_id,
                                        self.product.name, "online"]
                            self.product.order_list.append(buy_info)
                            return True
                        else:
                            self.product = None
                            return False
                    else:
                        self.product = None
                        return False

        if self.product.stock <= 0:
            out_of_buy_info = [self.model.schedule.time, self.consumer_id, self.name, self.product.product_id, self.product.name]
            self.product.out_of_order_list.append(out_of_buy_info)
            return False

    def get_neighbors(self):
        neighbor_nodes = self.model.consumer_grid.get_neighbors(self.node_id)
        neighbors = self.model.consumer_grid.get_cell_list_contents(neighbor_nodes)
        return neighbors

    def get_product_info(self):
        student_id = self.model.student_id
        query = "SELECT p.id, p.brand_id, p.name, p.price, p.score, p.cost, p.chengfen, p.gongxiao, p.stock, p.online_stock, p.skin_type, p.fit_age, b.brand_name from product as p LEFT JOIN brand as b on p.brand_id = b.id"
        df = sql.get_data_df(query, student_id)
        return df

    def init_topsis_data(self):
        info = self.get_product_info()
        info['consumer_age'] = self.age
        info['consumer_skin'] = self.skin_type
        info['consumer_prefer_brand'] = self.prefer_brand
        info['consumer_prefer_gongxiao'] = self.prefer_gongxiao
        info['neighbors_effect'] = 1
        info['ad_effect'] = 1
        return info

    def update_topsis_data(self, info):
        info['年龄匹配分'] = info.apply(
            lambda x: random.uniform(3.5, 5) if x['consumer_age'] in x['fit_age'] else random.uniform(1, 3.5), axis=1)
        info['肤质匹配分'] = info.apply(lambda x: self.skin_type_match(x['skin_type'], x['consumer_skin']), axis=1)
        info['品牌偏好分'] = info.apply(
            lambda x: random.uniform(3.5, 5) if x['consumer_prefer_brand'] == x['brand_name'] else random.uniform(1,
                                                                                                                  3.5),
            axis=1)
        info['邻居偏好分'] = info['neighbors_effect']
        info['广告偏好分'] = info['ad_effect']
        info2 = info.set_index('id')
        data = info2[['年龄匹配分', '肤质匹配分', '品牌偏好分', '邻居偏好分', '广告偏好分']]
        data['年龄匹配分'].astype('float')
        data['肤质匹配分'].astype('float')
        data['品牌偏好分'].astype('float')
        data['邻居偏好分'].astype('float')
        data['广告偏好分'].astype('float')
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
            return random.uniform(3.5, 5)
        else:
            for x in seq2:
                if x in seq1:
                    res.append(x)
            return random.uniform(0.5, len(res) + 1)

    def ad_infect(self, df):
        self.ad_infect_list.append(df)

    def connect_neighbors(self):
        for i in self.neighbors:
            i.infected_by_neighbors(self.product)

    def infected_by_neighbors(self, product: Product):
        self.info.loc[self.info.id == product.product_id, 'neighbors_effect'] = \
            self.info.loc[self.info.id == product.product_id, 'neighbors_effect'].values + 1

        # self.info[(self.info['id'] == product.product_id)]['neighbors_effect'][0] \
        #     = self.info[(self.info['id'] == product.product_id)]['neighbors_effect'][0] + 1

    def infected_by_ad(self, product_id, ad_info):
        # print("ad_infect")
        temp = np.array(ad_info)
        # print(product_id)
        score = np.dot(temp, self.ad_prefer_coef)
        # print(score)
        self.info.loc[self.info.id == product_id, 'ad_effect'] = \
            self.info.loc[self.info.id == product_id, 'ad_effect'].values + score
        # print(self.info)
        # print(self.info)

    def update(self):
        for i in self.neighbor_infect_list:
            if i[4] < 0:
                self.neighbor_infect_list.remove(i)
                # print(i)
            else:
                i[4] = i[4] - 1
                # print(i)

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

    def get_this_product(self, product_id) -> Product:
        products = [x for x in self.model.schedule.agents if isinstance(x, Product)]
        this_product = [x for x in products if x.product_id == product_id][0]
        return this_product

    def get_this_brand(self, brand_id) -> Brand:
        brands = [x for x in self.model.schedule.agents if isinstance(x, Brand)]
        this_brand = [x for x in brands if x.brand_id == brand_id][0]
        return this_brand
