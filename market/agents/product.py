from mesa import Agent


class Product(Agent):
    def __init__(self, unique_id, model, brand_id, name, price, score, cost, chengfen, gongxiao, stock,
                 online_stock, skin_type, fit_age):
        super(Product, self).__init__(unique_id, model)
        self.product_id = unique_id
        self.belong_brand_id = brand_id
        self.name = name
        self.price = price
        self.score = score
        self.cost = cost
        self.chengfen = chengfen
        self.gongxiao = gongxiao
        self.stock = stock
        self.online_stock = online_stock
        self.skin_type = skin_type
        self.fit_age = fit_age

    def step(self) -> None:
        pass