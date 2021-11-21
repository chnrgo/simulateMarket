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
        self.ad_strategy = {'代言直播':10000, '网页广告':50000, '搜索引擎':2000, '新媒体':5000, '路演':10000, '店面广告':50000, '印刷品':5000}
        self.target_consumer = None
        # 购买列表
        self.order_list = []
        # 缺货列表
        self.out_of_order_list = []

        self.current_sales_volume = 0
        self.stock_cost_per = 0.5
        self.stock_cost = 0


    def step(self) -> None:

        self.stock_cost = self.stock_cost + self.stock * self.stock_cost_per

    # def init_target_consumers(self):
    #     if

    def update_stock_price(self, stock, online_stock, price):
        self.stock = stock
        self.online_stock = online_stock
        self.price = price
        self.stock_cost = 0

    def ad(self, target_consumers):

        #目标客户群人数
        num = len(target_consumers)

        #代言直播
        per_daiyanzhibo = self.ad_strategy['代言直播'] / num

        #网页广告
        per_wangyeguanggao = self.ad_strategy['网页广告'] / num

        #搜索引擎
        per_sousuoyinqing = self.ad_strategy['搜索引擎'] / num

        #新媒体
        per_xinmeiti = self.ad_strategy['新媒体'] / num

        #路演
        per_luyan = self.ad_strategy['路演'] / num

        #店面广告
        per_dianmianguanggao = self.ad_strategy['店面广告'] / num

        #印刷品
        per_yinshuapin = self.ad_strategy['印刷品'] / num

        ad_info = [per_daiyanzhibo, per_wangyeguanggao, per_sousuoyinqing, per_xinmeiti, per_luyan, per_dianmianguanggao,
                   per_yinshuapin]

        for i in target_consumers:
            i.infected_by_ad(self.product_id, ad_info)