from mesa import Model
from mesa.space import NetworkGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import sql
from market.agents.brand import Brand
from market.agents.consumer import Consumer
from market.agents.product import Product
import networkx as nx


class Market(Model):
    def __init__(self, k, p, system_setting, student_id):
        """
        :param k:
        :param p:
        :param system_setting:
        :param student_id:
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
                              i[7], i[8], i[9], i[10])
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
            model_reporters={"MarketShare": compute_market_share},
            # agent_reporters={""}
        )

    def step(self) -> None:
        self.datacollector.collect(self)
        self.schedule.step()

def compute_market_share(model):
    # consumers = [agent.product for agent in model.schedule.agents]
    consumers = [x for x in model.schedule.agents if isinstance(x, Consumer)]
    products = [agent.product for agent in consumers]
    # print("A")
    # print(products)
    # brand_market_share