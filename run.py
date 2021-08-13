import json

import sql
from market.model import Market

if __name__ == '__main__':
    student_id = "0000"

    # 初始化数据库
    sql.init_db(student_id=student_id)
    # 初始化模型
    with open("data/system_setting.json", 'r', encoding='utf-8') as load_f:
        system_setting = json.load(load_f)

    with open("data/student_init.json", 'r', encoding='utf-8') as load_f:
        new_brand = json.load(load_f)

    k = 6
    p = 0.3

    market = Market(k, p, system_setting, student_id)

    for i in range(540):
        market.step()
