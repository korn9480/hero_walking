from typing import List
from utils import * 
from pydantic import BaseModel, parse_obj_as

class Move: #เคลื่อนที่
    def __init__(self) -> None:
        self.front = "go to top"
        self.behind = "go below"
        self.left ="go letf"
        self.right  ="go right"
        self.turn_up= "turn up"
        self.turn_down="turn down"
        self.turn_right="turn right"
        self.turn_letf="turn letf"
        self.vocab_go=[self.front,self.behind,self.left,self.right]
        self.vocab_turn=[self.turn_down , self.turn_letf , self.turn_up , self.turn_right]


class DogData(BaseModel):
    position_current:Position #เก็บตำเเหน่งปัจจุบัน
    position: Position #เก็บตำเเหน่งที่อยู่เดิม
    running_way : List[Position] #เส้นทางที่เดิน
    is_running_x :bool  #วิ่งเเนวไหน x or y
    is_show:bool #แสดงอ็อบเจค
    is_start :bool # สถานะการวิ่ง
    run_list:list # เก็บเส้นทางของฮีโร่

class Charlater:#ตัวละคร
    def __init__(self,my_hero:str):
        self._y=int()
        self._x=int()
        self.body=my_hero
        self.moving = Move()
        self.is_over = False
    def get_position(self):
        return Position(
            x = self._x,
            y = self._y
        )

    def set_position(self,position:Position):
        self._y= position.y        
        self._x = position.x

    def _move(self,moving:Move):
        if moving == self.moving.front:
            self._y-=1
        elif moving== self.moving.behind:
            self._y+=1
        elif moving== self.moving.left:
            self._x-=1
        elif moving==self.moving.right:
            self._x+=1

    def next_moving(self,moving:Move):
        x=0
        y=0
        if moving == self.moving.front:
            y-=1
        elif moving== self.moving.behind:
            y+=1
        elif moving== self.moving.left:
            x-=1
        elif moving==self.moving.right:
            x+=1
        elif moving==self.moving.turn_up:
            y-=1
        elif moving==self.moving.turn_down:
            y+=1
        elif moving==self.moving.turn_letf:
            x-=1
        elif moving==self.moving.turn_right:
            x+=1
        return x,y
