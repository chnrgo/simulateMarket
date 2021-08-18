from mesa import Model
from mesa.space import NetworkGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import sql
from market.agents.brand import Brand
from market.agents.consumer import Consumer
from market.agents.product import Product
import networkx as nx
import pandas as pd

class Market(Model):
    def __init__(self, k, p, system_setting, student_id):
        """
        :param k: 小世界网络参数k，邻居个数
        :param p: 小世界网络参数p，重连概率
        :param system_setting: 教师设置好的系统参数
        :param student_id: 学生id
        """

        self.student_id = student_id

        # 添加调度器
        self.schedule = SimultaneousActivation(self)
        self.running = True

        # 从数据库提取数据
        sql_brand = "SELECT * FROM brand"
        sql_product = "SELECT * FROM product"
        sql_consumer = "SELECT * FROM consumer"

        brands = sql.get_data(sql_brand, student_id)
        products = sql.get_data(sql_product, student_id)
        consumers = sql.get_data(sql_consumer, student_id)

        # 添加小世界网络
        self.num_nodes = len(consumers)
        self.G = nx.watts_strogatz_graph(n=self.num_nodes, k=k, p=p)
        self.consumer_grid = NetworkGrid(self.G)
        List_of_random_nodes = self.random.sample(self.G.nodes(), self.num_nodes)

        # 构造对象
        ## 构造品牌对象

        for i in products:
            product = Product(i[0], self, i[1], i[2], i[3], i[4], i[5], i[6],
                              i[7], i[8], i[9], i[10], i[11])
            self.schedule.add(product)

        for i in brands:
            brand = Brand(i[0], self, i[1], i[2], i[3], i[4])
            self.schedule.add(brand)

        index_temp = 0
        for i in consumers:
            node_id = List_of_random_nodes[index_temp]
            consumer = Consumer(i[0], self, i[1], i[2], i[3], i[4], i[5], i[6], i[7], node_id)
            self.schedule.add(consumer)
            self.consumer_grid.place_agent(consumer, node_id)
            index_temp = index_temp + 1

        self.datacollector = DataCollector(
            # model_reporters={"ProductMarketShare": compute_product_market_share,
            #                  "BrandMarketShare": compute_brand_market_share},
            # agent_reporters={""}
            model_reporters={"data": compute}
        )

    def step(self) -> None:
        self.datacollector.collect(self)
        self.schedule.step()

    def student_strategy_init(self, my_brand):
        brand = Brand(8000, self, my_brand[0]['brand_name'])
        self.schedule.add(brand)
        sql_new_brand = "INSERT INTO brand (id, brand_name)  VALUES ({}, '{}')".format(brand.brand_id, brand.brand_name)
        sql.insert(sql_new_brand, self.student_id)
        my_products = my_brand[0]['products']
        for i, p in enumerate(my_products):
            product = Product(800000 + i , self, 8000, p['name'], p['price'], p['score'], p['cost'],
                                 p['chengfen'], p['gongxiao'], p['stock'], p['online_stock'], p['skin_type'],
                                 p['fit_age'])
            brand.products.append(product)
            self.schedule.add(product)
            sql_new_product = "INSERT INTO product (id, brand_id, name, price, score, cost, chengfen, gongxiao, stock, online_stock, skin_type, fit_age)" \
                              "  VALUES ({}, {}, '{}', {}, {}, {}, '{}', '{}', {}, {}, '{}', '{}')".format(product.product_id, product.belong_brand_id, product.name, product.price, product.score, product.cost, product.chengfen, product.gongxiao, product.stock, product.online_stock, product.skin_type, product.fit_age)
            sql.insert(sql_new_product, self.student_id)



def compute_product_market_share(model):
    consumers_buy_list = [x.product for x in model.schedule.agents if isinstance(x, Consumer)]
    products = [x for x in model.schedule.agents if isinstance(x, Product)]
    info = []
    for i in products:
        info.append([i.product_id, i.name, consumers_buy_list.count(i)])
    return info

def compute_brand_market_share(model):
    consumers_buy_list = [x.brand for x in model.schedule.agents if isinstance(x, Consumer)]
    brands = [x for x in model.schedule.agents if isinstance(x, Brand)]
    info = []
    for i in brands:
        info.append([i.brand_id, i.brand_name, consumers_buy_list.count(i)])
    return info

def compute(model):
    consumers_buy_list = [x.brand for x in model.schedule.agents if isinstance(x, Consumer)]
    brands = [x for x in model.schedule.agents if isinstance(x, Brand)]
    info = {}
    for i in brands:
        info[i.brand_name] = consumers_buy_list.count(i)
    return info