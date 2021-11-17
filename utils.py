from pydantic import BaseModel
import logging
import os
import pathlib
import time
class Position(BaseModel):
    x: int
    y: int

def set_logfile(path_file: str, mode='a', encoding='utf-8'):
    """
    กำหนดค่าเริ่มสำหรับ log ที่ต้องการเขียน
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(path_file, mode, encoding)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s(%(levelname)s) - %(message)s'))
    root_logger.addHandler(handler)

def log_level(level: int, message: str, type=logging.INFO):
    "log message โดยจะ indent ตาม level"
    message = str(message)
    space = "\t"*(level-1)
    log_message = space+message
    if type == logging.INFO:
        logging.info(log_message)
    elif type == logging.ERROR:
        logging.error(log_message)
    elif type == logging.WARNING:
        logging.warning(log_message)
    else:
        logging.warning(log_message)

def get_filename_only(path_file:str):
    return pathlib.Path(path_file).stem

def read_file_in_folder(dir :str,endswith=".txt"):       # 1.Get file names from directory
    file_list=os.listdir(dir)
    print(">",file_list)
    files = dict()
    for f in file_list:
        if f.endswith(endswith):
            files[get_filename_only(f)] = os.path.join(dir,f)
    return files

def input_name_map():
    files_dict = read_file_in_folder("./")
    list_files = [f for f in files_dict.keys()]
    os.system('cls')
    print("name map \n")
    for num,f in enumerate(list_files):
        print(f"{num+1}.{f}\n")
    name_map=input("choose your map :")
    name_map=name_map.lower().strip()
    if name_map.isnumeric():
        name_map=int(name_map)
        if name_map > 0 and name_map <= len(list_files):
            name_map=int(name_map)        
            name_map=list_files[int(name_map)-1]
        else:
            print("not have number map "+name_map)
            time.sleep(2)
            return None
    path_map = files_dict[name_map]
    return path_map

# if __name__ =="__main__":
#     result = read_file_in_folder("./")
#     # print(result.keys())
#     for f in result.keys():
#         print(f)
