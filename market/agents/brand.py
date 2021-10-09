import random

from mesa import Agent



from market.agents.product import Product


class Brand(Agent):
    '''


    '''
    def __init__(self, unique_id, model, brand_name, yield_change_rate=None, price_change_rate=None, ad_strategy=None):
        super(Brand, self).__init__(unique_id, model)
        self.brand_id = unique_id
        self.brand_name = brand_name
        self.yield_change_rate = yield_change_rate
        self.price_change_rate = price_change_rate
        self.ad_strategy = ad_strategy
        self.status = 'agent'
        self.products = []

        #投资回报率
        self.ROI = 0

    def step(self) -> None:

        # 模型在第一步时，进行初始化
        if self.model.schedule.time == 0:
            self.init_at_0()

        # 主模型的时间步单位为天，Brand类的决策周期为90天
        if (self.model.schedule.time - 1) % 90 == 0:
            if self.status == 'agent':
                self.agent_enterprise_staregy()
                self.promote()
            if self.status == 'student':
                pass


    def init_at_0(self):
        '''
        初始化当前Brand的属性：
            1. 初始化products列表
        :return:
        '''
        all_products = [x for x in self.model.schedule.agents if isinstance(x, Product)]
        self.products = [x for x in all_products if x.belong_brand_id == self.brand_id]

    def agent_enterprise_staregy(self):
        for i in self.products:
            new_stock  = i.stock * (1 + self.yield_change_rate)
            new_online_stock = new_stock * 0.7
            new_price = i.price * (1 + self.price_change_rate)
            i.update_stock_price(new_stock, new_online_stock, new_price)



    def create_promote_plan(self):
        '''
        当该企业为虚拟企业时，
        当该企业为学生决策企业时，参数由学生输入
        :return:
        '''
        pass


    def promote(self):
        '''
        当前企业进行推广
        :return:
        '''
        from market.agents.consumer import Consumer
        consumers = [x for x in self.model.schedule.agents if isinstance(x, Consumer)]
        target_consumers = random.sample(consumers, 500)
        for i in self.products:
            i.ad(consumers)
