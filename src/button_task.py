from components.button import Button

def button_task():
    button = Button(27)
    #while 1:
    #    if button.pressed():
    #        print("pressed")
    #    time.sleep(1)
    button.add_callback(lambda pin: print("helloworld"), bouncetime=200)
