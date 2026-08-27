import pyserial
import time
import numpy as np
import typing

is_Read = False
data = []

def change_read_state(state: bool):
    # 读取键盘的空格，切换读取状态
    global is_Read
    if typing.get() == ' ':
        is_Read = not is_Read
        if is_Read:
            print("[info] Data reading started.")
        else:
            print("[info] Data reading stopped.")

def print_info():
    if is_Read:
        if len(data) > 0:
            print(f"Current data: {data[-1]}")
        else:
            print("[info] No data read yet.")

print("[system] Press space to start/stop data reading.")
while is_Read:
    try:
        data = pyserial.read_data()
        if data is not None:
            time=time.time()
            data.append((time, data))
            if csv_file is not None: # 有则写，无则建写
                csv_file.create(f"{time.data}.csv")
                csv_file.write(f"{time},{data}\n")
            else 
                csv_file = open(f"{time.data}.csv", "w")
                csv_file.write(f"{time},{data}\n")
    except Exception as e:
        print(f"Error reading data: {e}")
        is_Read = False
