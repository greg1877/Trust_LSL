def something():
    str1 = input("write something here \n")
    print((str1+" balls\n")*3)


def one_more():
    global x:
    x=1

def on_space():
    print('space was pressed')

keyboard.add_hotkey('space', on_space)


i = 0

while True:
    try:
        print("a ")
    except KeyboardInterrupt:
        str1 = input("enter a letter \n")
        if str1 == "b":
            continue
        else:
            print("Wrong Key Dude!")
            exit()


while True:
    try:
        print("a ")
    except KeyboardInterrupt:
        str1 = input("enter a letter \n")
        if str1 == "b":
            continue
        else:
            print("Wrong Key Dude!")
            exit()