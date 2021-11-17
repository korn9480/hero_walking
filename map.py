from logging import error, fatal, log
from pydantic.schema import encode_default
from pynput.keyboard import Controller
import os
import copy
import random
import time
import sys
from typing import List
from pydantic import utils

from pydantic.types import PositiveInt
from charlater import*
from utils import *
from pydantic import BaseModel, parse_obj_as


class Map:
    def __init__(self, path_map: str, hero: Charlater):
        with open(path_map, 'r') as f:
            self.map_string = f.read()

        self.map_list = []
        self.birth_position = dict()
        self.list_dog_data = []
        self.my_hero = hero
        # ตัว \n ออก ระหว่างบรรทัด
        for y, line in enumerate(self.map_string.splitlines()):
            if "#" in line:
                segment_char = []
                number = ""
                for x, c in enumerate(line):
                    if c.isnumeric():
                        number += c
                    else:
                        if number.isnumeric():
                            self.birth_position.update(
                                {number: [y, x-len(number)]})
                            number = ""
                    segment_char.append(c)
                self.map_list.append(segment_char)
            else:
                self.list_dog_data.append(self.text_to_dog_data(line))
        index_hero = self.random_position()
        self.my_hero.set_position(index_hero)
        while 1:
            index = self.random_position()
            if index != index_hero:
                self.goal = Charlater("❣️")
                self.goal.set_position(index)
                break

    def text_to_dog_data(self,line: str):
        segment = line.split()
        position = Position(y=int(segment[1]), x=int(segment[2]))
        is_running_x = segment[-3] == "running_x"
        if is_running_x:
            running_way = [Position(x=int(i), y=position.y)
                       for i in range(int(segment[-2]), int(segment[-1])+1)]
        else:
            running_way = [Position(x=position.x, y=int(i))
                       for i in range(int(segment[-2]), int(segment[-1])+1)]
        return DogData(
            position_current=position,
            position=position,
            running_way=running_way,
            is_running_x=is_running_x,
            is_show=False,
            is_start=False,
            run_list=[]
        )

    def random_position(self):
        index_number = random.choice(list(self.birth_position.keys()))
        index = self.birth_position[index_number]
        return Position(
            x=index[1],
            y=index[0]
        )

    def check_dog(self, add_x_hero: int, add_y_hero: int, is_walking=True):
        hero_position = self.my_hero.get_position()
        for i, dog in enumerate(parse_obj_as(List[DogData], self.list_dog_data)):
            if dog.is_show:
                if hero_position == dog.position_current and dog.is_start:
                    log_level(2,"die")               
                    self.my_hero.is_over = True
                if is_walking:
                    log_level(2,"append walking") 
                    dog.run_list.append(self.my_hero.get_position())

            if hero_position == dog.position and not dog.is_show:
                log_level(2,"show dog") 
                dog.is_show = True
            elif dog.is_show and len(dog.run_list) > 0:
                if dog.is_start:
                    if dog.run_list[0] in dog.running_way:
                        log_level(2,"อยู่เส้นทาง")
                        dog.position_current = dog.run_list[0]
                        dog.run_list.pop(0)  
                        if hero_position == dog.position_current:
                            self.my_hero.is_over=True
                    else:
                        log_level(2,"ไม่อยู่ในเส้นทาง") 
                        dog.run_list.clear() 
                        dog.position_current = dog.position
                        dog.is_start=False
                        dog.is_show=False    

                elif len(dog.run_list) > 0:    
                    log_level(2,"เริ่มเดิน")     
                    dog.is_start = True

            self.list_dog_data[i] = dog

    def my_hero_turn(self, turn: Move, go: Move):
        go_x, go_y = self.my_hero.next_moving(go)
        turn_x, turn_y = self.my_hero.next_moving(turn)
        if self.map_list[self.my_hero._y+go_y+turn_y][self.my_hero._x+go_x+turn_x] != "#":
            # เเสดงการเดิน
            self.my_hero._y += go_y
            self.my_hero._x += go_x
            self.check_dog(go_x, go_y)
            self.refresh_map()
            # เเสดงการเลี้ยว
            self.my_hero._y += turn_y
            self.my_hero._x += turn_x
            self.check_dog(turn_x, turn_y)
            self.refresh_map()
        else:
            print("can't turn")
            self.check_dog(0, 0, False)
            time.sleep(2)

    def move_hero(self, moving: Move):
        is_continue = False
        next_x, next_y = self.my_hero.next_moving(moving)
        if self.map_list[self.my_hero._y+next_y][self.my_hero._x+next_x] != "#":
            result_go = self.next_go_straight(next_x, next_y)
            if result_go == True:
                self.my_hero._move(moving)
                self.check_dog(next_x, next_y)
            else:
                print("please your way turn")
                time.sleep(2)
        else:
            print("can't go")
            is_continue = True
            time.sleep(2)
            self.check_dog(next_x, next_y, False)
        self.refresh_map()

        while True:
            next_x, next_y = self.my_hero.next_moving(moving)
            is_continue = self.is_crossroads(next_x, next_y)
            if self.map_list[self.my_hero._y+next_y][self.my_hero._x+next_x] != "#":
                if not is_continue:
                    # self.is_crossroads(next_x, next_y)
                    self.my_hero._move(moving)  # ให้เดิน
                    self.check_dog(next_x, next_y)
                    self.refresh_map()
                else:                    
                    break
            else:
                break
            # self.refresh_map()

    def is_crossroads(self, next_x, next_y):
        if next_x != 0:
            if self.map_list[self.my_hero._y-1][self.my_hero._x+next_x] == " ":
                return True
            elif self.map_list[self.my_hero._y+1][self.my_hero._x+next_x] == " ":
                return True
            elif self.map_list[self.my_hero._y-1][self.my_hero._x+next_x].isnumeric():
                return True
            elif self.map_list[self.my_hero._y+1][self.my_hero._x+next_x].isnumeric():
                return True
        elif next_y != 0:
            if self.map_list[self.my_hero._y+next_y][self.my_hero._x-1] == " ":
                return True
            elif self.map_list[self.my_hero._y+next_y][self.my_hero._x+1] == " ":
                return True
            elif self.map_list[self.my_hero._y+next_y][self.my_hero._x-1].isnumeric():
                return True
            elif self.map_list[self.my_hero._y+next_y][self.my_hero._x+1].isnumeric():
                return True
        return False

    def next_go_straight(self, next_x, next_y):
        if next_x != 0:
            if self.map_list[self.my_hero._y][self.my_hero._x+(next_x*2)] != "#":
                return True
        elif next_y != 0:
            if self.map_list[self.my_hero._y+next_y*2][self.my_hero._x] != "#":
                return True
        return False

    def start(self):
        os.system('cls')
        self.show_map()

    def refresh_map(self):
        os.system('cls')
        self.show_map()
        time.sleep(0.3)

    def show_map(self):
        area_edit = copy.deepcopy(self.map_list)
        if str(area_edit[self.my_hero._y][self.my_hero._x+1]).isnumeric():
            area_edit[self.my_hero._y][self.my_hero._x+1] = " "

        if str(area_edit[self.goal._y][self.goal._x+1]).isnumeric():
            area_edit[self.goal._y][self.goal._x+1] = " "

        area_edit[self.goal._y][self.goal._x] = self.goal.body

        for dog in parse_obj_as(List[DogData], self.list_dog_data):
            if dog.is_show:
                index = dog.position_current
                area_edit[index.y][index.x] = u"\u001b[32m{}\u001b[0m".format("D")

        if self.my_hero.is_over:
            pass
        else:
            area_edit[self.my_hero._y][self.my_hero._x] = u"\u001b[33m{}\u001b[0m".format(
                self.my_hero.body)
        for j in area_edit:
            print(''.join(j))
# ---------------------------------------edit map------------------------------------------------------
class Edit_map:
    def __init__(self, map: Map,file_map:str) -> None:
        self.map_edit = copy.deepcopy(map.map_list)
        self.map_function = copy.deepcopy(map)
        self.dog_data = copy.deepcopy(map.list_dog_data)
        self.file_map=file_map

    def write_to_terminal(self, text: str, indent: int):
        keyboard = Controller()
        for k in range(indent):
            keyboard.press(" ")
            keyboard.release(" ")
        for key in text:
            keyboard.press(key)
            keyboard.release(key)

    def input_menu_edit(self):
        while True:
            os.system('cls')
            self.show_map_edit()
            menu = input("menu edet :")
            if menu == "1" or menu == "add line":
                line_input = input("add :")
                line_input = list(line_input)
                line_input=self.map_edge(line_input)
                self.map_edit.append(line_input)

            elif menu == "2" or menu == "insert line":
                number_line = int(input("line number :"))
                number_line-=1
                line_input = input("add :")
                line_input=list(line_input)
                line_input=self.map_edge(line_input)
                self.map_edit.insert(number_line, line_input)

            elif menu == "3" or menu == "edit line":
                number_line = int(input("line number :"))
                number_line-=1
                self.write_to_terminal(self.map_edit[number_line], indent=5)
                line_input = input("")
                line_input=list(line_input)
                line_input=self.map_edge(line_input)
                self.map_edit[number_line] = line_input[5:]

            elif menu == "4" or menu == "delete line":
                number_line = int(input("line number :"))
                number_line-=1
                self.map_edit.pop(number_line)

            elif menu == "5" or menu == "add dog":
                self.show_map_edit_dog()
                print("\nexample :position 4 6 running_x 2 13")
                print("should be input :4 6 x 2 13")
                input_dog = input("dog :")
                input_dog = input_dog.split()
                if input_dog[2] in "x y":
                    input_dog[0]=str(int(input_dog[0])-1)
                    input_dog[1]=str(int(input_dog[1])-1)
                    input_dog[3]=str(int(input_dog[3])-1)
                    input_dog[-1]=str(int(input_dog[-1])-1)
                    input_dog.insert(0,"position")
                    input_dog[3]="running_"+input_dog[3]
                    line = " ".join(input_dog)

                    dog_data = self.map_function.text_to_dog_data(line)
                    self.dog_data.append(dog_data)
                else:
                    print("input is wrong")
                    time.sleep(2)
                
            elif menu == "6" or menu == "edit dog":
                self.show_map_edit_dog()
                number_dog=int(input("number dog :"))
                number_dog-=1
                if number_dog <len(self.dog_data):
                    print("\nexample :position 4 6 running_x 2 13")
                    print("should be input :4 6 x 2 13")
                    input_dog = input("dog :")
                    input_dog = input_dog.split()
                    if input_dog[2] in "x y":
                        input_dog[0]=str(int(input_dog[0])-1)
                        input_dog[1]=str(int(input_dog[1])-1)
                        input_dog[3]=str(int(input_dog[3])-1)
                        input_dog[-1]=str(int(input_dog[-1])-1)
                        
                        input_dog.insert(0,"position")
                        input_dog[3]="running_"+input_dog[3]
                        line = " ".join(input_dog)
                        dog_data = self.map_function.text_to_dog_data(line)
                        self.dog_data[number_dog]=dog_data
                else :
                    print("not have number dog"+number_dog)
                    time.sleep(2)

            elif menu == "7" or menu == "delete dog":
                self.show_map_edit_dog()
                number_dog=int(input("number dog :"))
                number_dog-=1
                if number_dog<len(self.dog_data):
                    self.dog_data.pop(number_dog)
                else :
                    print("not have number dog"+number_dog)
                    time.sleep(2)

            elif menu == "8" or menu == "save":
                print("your save map edit ?\n1.ok\n2.cancel")
                save=input("you save map edit :")
                if save == "1" or save=="yes" or save=="ok":
                    #บันทึกเเผนที่ เป็นstr
                    map_string = ""
                    for line in self.map_edit:
                        line=self.map_edge(line)
                        map_string+=''.join(line)+"\n"
                    #บันทึกหมา เป็นstr
                    dog_string=""
                    for dog in parse_obj_as(List[DogData],self.dog_data) :
                        dog_string+="position "
                        dog_string+=str(dog.position.y)+" "
                        dog_string+=str(dog.position.x)+" "
                        run=""
                        if dog.is_running_x:
                            dog_string+="running_x "
                            run =str(dog.running_way[0].x)+" "+str(dog.running_way[-1].x)
                        elif not dog.is_running_x:
                            dog_string+="running_y "
                            run =str(dog.running_way[0].y)+" "+str(dog.running_way[-1].y)
                        dog_string+=run+"\n"

                    with open(self.file_map,'w') as file_map:
                        file_map.writelines(map_string)
                        file_map.writelines(dog_string)
                    break
        

    def map_edge(self,line_input:list):
        max_row = max([len(row) for row in self.map_edit])
        if len(line_input)<=max_row:
            bar=list(" "*(max_row-len(line_input)))
            line_input.extend(bar) 
        line_input[0]="#"
        line_input[-1]="#"

        return line_input   

    def show_map_edit_dog(self):
        list_num_color = ['\u001b[31;1m', '\u001b[32;1m',
                    '\u001b[33;1m', '\u001b[34;1m', '\u001b[35;1m']
        area_edit = copy.deepcopy(self.map_edit)
        max_row = max([len(row) for row in area_edit])
        no_color = 0
        os.system('cls')
        print(" "*5, end="")
        for num in range(0, max_row):
            num+=1
            if num % 10 == 0:
                no_color += 1
            print("{}{}\u001b[0m".format(
                list_num_color[no_color], num % 10), end="")
        print()
        area_edit= self.add_position_dog_to_map()
        for i, j in enumerate(area_edit):
            i+=1
            print(str(i).rjust(4), ''.join(j))
            

    def show_map_edit(self):
        menu = ("menu", "1.add line", "2.insert line", "3.edit line",
                "4.delete line", "5.add dog", "6.edit dag", "7.delete dog", "8.save")
        area_edit = copy.deepcopy(self.map_edit)
        max_row = max([len(row) for row in area_edit])
        area_edit= self.add_position_dog_to_map()
        os.system('cls')
        for i, j in enumerate(area_edit):
            i+=1
            if i <= len(menu):
                print(str(i).rjust(4), ''.join(j).ljust(max_row),f"{'':>3}{menu[i-1]}")
            else:
                print(str(i).rjust(4), ''.join(j))

    def add_position_dog_to_map(self):
        list_bg_color = ["\u001b[41;1m", "\u001b[42;1m", "\u001b[43;1m",
                         "\u001b[44;1m", "\u001b[45;1m", "\u001b[46;1m"]
        area_edit = copy.deepcopy(self.map_edit)
        try:
            for i, dog in enumerate(parse_obj_as(List[DogData], self.dog_data)):
                i+=1
                area_edit[dog.position.y][dog.position.x] = u"\u001b[40m{}\u001b[0m".format(i)
                for run in dog.running_way:
                    area_edit[run.y][run.x] = u'{}{}\u001b[0m'.format(
                    list_bg_color[i % len(list_bg_color)], area_edit[run.y][run.x])
        except Exception as e:
            pass
        return area_edit