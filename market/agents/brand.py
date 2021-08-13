from mesa import Agent

from market.agents.product import Product


class Brand(Agent):
    def __init__(self, unique_id, model, brand_name, yield_change_rate, price_change_rate, ad_strategy):
        super(Brand, self).__init__(unique_id, model)
        self.brand_id = unique_id
        self.brand_name = brand_name
        self.yield_change_rate = yield_change_rate
        self.price_change_rate = price_change_rate
        self.ad_strategy = ad_strategy
        all_products = [x for x in self.model.schedule.agents if isinstance(x, Product)]
        self.products = [x for x in all_products if x.belong_brand_id == self.brand_id]

    def step(self) -> None:
        pass

    def create_staregy(self):
        for i in self.products:
            i.stock = i.stock * (1 + self.yield_change_rate)
        # 制定产量计划

        # 制定价格计划

    def create_promote_plan(self):
        pass


    def promote(self):
        pass