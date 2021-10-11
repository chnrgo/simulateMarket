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
        self.sales_conditions = []
        self.staff = None
        self.ad_investment = None

    def step(self) -> None:
        # 模型在第一步时，进行初始化
        if self.model.schedule.time == 0:
            self.init_at_0()

        # 主模型的时间步单位为天，Brand类的决策周期为90天
        if (self.model.schedule.time - 2) % 90 == 0:
            # print(self.model.schedule.time)
            if self.status == 'agent':
                # 计算上一期内的销售情况
                if self.model.schedule.time >= 90:
                    self.compute_sales_conditions()
                # 企业进行决策
                self.agent_enterprise_staregy()
                # 企业进行推广
                self.promote()
            if self.status == 'student':
                # 计算上一期内的销售情况
                if self.model.schedule.time >= 90:
                    self.compute_sales_conditions()
                # 学生企业进行决策
                # self.student_enterprise_strategy() #已弃用
                # 企业进行推广
                self.promote()

    def init_at_0(self):
        '''
        初始化当前Brand的属性：
            1. 初始化products列表
        :return:
        '''
        all_products = [x for x in self.model.schedule.agents if isinstance(x, Product)]
        self.products = [x for x in all_products if x.belong_brand_id == self.brand_id]
        # 初始化职员配置，所需工资
        if self.status == "agent":
            self.staff = 20000
            self.ad_investment = 500000

    def student_enterprise_strategy(self):
        '''
        弃用函数，更新消费者决策json数据时，已加载相关数据
        :return:
        '''
        pass

    def agent_enterprise_staregy(self):
        for i in self.products:
            i.current_sales_volume = 0
            new_stock = i.stock * (1 + self.yield_change_rate)
            new_online_stock = new_stock * 0.7
            new_price = i.price * (1 + self.price_change_rate)
            i.update_stock_price(new_stock, new_online_stock, new_price)

    def promote(self):
        '''
        当前企业进行推广
        :return:
        '''
        # print(self.status)
        from market.agents.consumer import Consumer
        consumers = [x for x in self.model.schedule.agents if isinstance(x, Consumer)]
        target_consumers = random.sample(consumers, 1000)
        for i in self.products:
            i.ad(target_consumers)



    def compute_sales_conditions(self):

        info = []
        info_detail = {
            "产品id": '',
            "产品名称": '',
            "产品销量": '',
            "产品价格": '',
            "产品成本": '',
            "产品广告费用": '',
            "产品渠道销售费用": '',
            "产品库存成本": '',
        }
        for i in self.products:
            info_detail["产品id"] = i.product_id
            info_detail["产品名称"] = i.name
            info_detail["产品销量"] = i.current_sales_volume
            info_detail["产品价格"] = i.price
            info_detail["产品成本"] = i.cost
            info_detail["产品广告费用"] = i.ad_strategy['代言直播'] + i.ad_strategy['网页广告'] + i.ad_strategy['搜索引擎'] \
                                    + i.ad_strategy['新媒体'] + i.ad_strategy['路演'] + i.ad_strategy['店面广告'] \
                                    + i.ad_strategy['印刷品']
            info_detail["产品销售渠道费用"] = 0
            info_detail["产品库存成本"] = i.stock_cost

            info.append(info_detail)
        self.sales_conditions.append(info)

        # print(info)

