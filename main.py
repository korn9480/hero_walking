import os
import sys
from time import time_ns
from pynput import keyboard

from charlater import *
from map import*
from utils import*

def play_game(path_map):
    set_logfile("program.log","w")
    log_level(1,"start..")
    intro_join_game()
    hero=Charlater("A")
    my_map=Map(path_map,hero)
    my_map.start()
    times=0
    save_moving=None
    while  my_map.goal.get_position() != my_map.my_hero.get_position() and not hero.is_over:
    
        moving= input("vocab :")

        moving=moving.lower().strip()
        if moving=="out":
            log_level(1,"exit")
            break
        elif moving in hero.moving.vocab_go:
            log_level(1,"go straight")
            my_map.move_hero(moving)
            save_moving=moving       

        elif moving in hero.moving.vocab_turn:
            log_level(1,"turn")
            if save_moving not in hero.moving.vocab_go:
                save_moving=input("your go :")
                save_moving=save_moving.lower().strip()
            if moving in "turn down turn up" and save_moving in "go right go letf":
                my_map.my_hero_turn(moving,save_moving)
            elif moving in "turn right turn letf" and save_moving in "go to top go below":
                my_map.my_hero_turn(moving,save_moving)
            else :
                print("Control commands do not match ")
                time.sleep(3)
            save_moving=moving
        else:
            print("no control command :"+moving)
            time.sleep(3)
            log_level(1,"walking wrong")
            my_map.check_dog(0,0,False)
            moving=None
            save_moving=None
        my_map.refresh_map()
        times+=1

    if my_map.goal.get_position() == my_map.my_hero.get_position():
        print("you win!!!")
    else:
        print("you lose!!!")
        if hero.is_over:
            print("because bitten by a dog")
    print(f"type {times} times")
    time.sleep(5)
    log_level(1,"end")

def show_menu(name_map):
    menu=[]
    if name_map==None:
        menu=["menu","1.play game","2.edit map","3.out game"]
    else :
        menu=["menu","1.change map","2.past map","3.edit map","4.out game"]
    for i in menu:
        print(i+"\n")

def loading(run):
    for i in range(run, run+10):
        time.sleep(0.1)
        sys.stdout.write(u"\u001b[1000D"+" "*15 + str(i + 1) + "%")
        sys.stdout.flush()
    print

def intro_join_game():
    intro1=" ________               ________"
    intro2="/\_______\             /\_______\ " 
    intro3="|_|______| __________ |_|______|"
    list_intro=[list(intro1),list(intro2),list(intro3)]
    run=0
    os.system('cls')
    for i in range(11,21):
        list_intro[2][i]="🧑"
        for j in list_intro:
            print("".join(j))
        print("\n")
        loading(run)
        list_intro[2][i]="_"
        os.system('cls')
        run +=10

if __name__ =="__main__":
    set_logfile("program.log","w")
    log_level(1,"start..")
    path_map=None
    while True :
        os.system('cls')
        show_menu(path_map)
        menu=input("menu :")
        menu=menu.lower().strip() 
        if menu=="1" and path_map==None or menu=="play game" or menu =="change map":
            path_map=input_name_map()
            if path_map == None:
                continue
            play_game(path_map)

        elif menu=="2" and path_map!=None:
            play_game(path_map)

        elif menu=="2" and path_map==None or menu=="edit map":
            path_map=input_name_map()
            if path_map == None:
                continue
            hero=Charlater("A")
            my_map=Map(path_map,hero)
            edit_map=Edit_map(my_map,path_map)
            edit_map.input_menu_edit()

        elif menu =="3" and path_map!=None:
            path_map=input_name_map()
            if path_map == None:
                continue
            hero=Charlater("A")
            my_map=Map(path_map,hero)
            edit_map=Edit_map(my_map,path_map)
            edit_map.input_menu_edit()

        elif menu =="3" and path_map==None or menu =="out":
            break
        elif menu=="4" and path_map!=None :
            break
        else :
            print("not have menu"+menu)
            time.sleep(2)