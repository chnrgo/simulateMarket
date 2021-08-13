from datetime import datetime
def print_time(text):
    print("====> {}".format(text), datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))