import json

import sql
from market.model import Market
from mian import ModelRun

if __name__ == '__main__':

    stu1 = ModelRun(student_id="0000", student_init_json_path="data/student_init.json", k=6, p=0.3)
    print("==========")
    stu2 = ModelRun(student_id="0002", student_init_json_path="data/student_init.json", k=5, p=0.2)