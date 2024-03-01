from machine import Pin, reset
import time

# Rotary encoder pins
sia = Pin(4, Pin.IN, Pin.PULL_UP)
sib = Pin(5, Pin.IN, Pin.PULL_UP)

# Button pin
button = Pin(2, Pin.IN, Pin.PULL_UP)

# State variables
encoder_value = 0
last_state = sia.value() << 1 | sib.value()
button_pressed = False
press_start_time = 0

transition_table = {
    (0, 1): 'partial',
    (1, 3): 'partial',
    (3, 2): 'partial',
    (2, 0): 'complete_forward',
    (1, 0): 'partial',
    (3, 1): 'partial',
    (2, 3): 'partial',
    (0, 2): 'complete_backward',
}

def update_encoder():
    global last_state, encoder_value
    new_state = sia.value() << 1 | sib.value()
    state_change = (last_state, new_state)
    
    if state_change in transition_table:
        transition = transition_table[state_change]
        if transition == 'complete_forward' and encoder_value < 12:
            encoder_value += 1
            print(">>> Forward")
        elif transition == 'complete_backward' and encoder_value > -12:
            encoder_value -= 1
            print("<<< Backward")

    last_state = new_state

def encoder_isr(pin):
    update_encoder()

def button_isr(pin):
    global button_pressed, press_start_time
    if not pin.value():  # Button pressed
        if not button_pressed:
            button_pressed = True
            press_start_time = time.ticks_ms()
            print("Button pressed")
    else:  # Button released
        if button_pressed:
            button_pressed = False
            if time.ticks_diff(time.ticks_ms(), press_start_time) >= 5000:
                print("Rebooting...")
                reset()  # Soft reboot the device
            else:
                print("Button released")

sia.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)
sib.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)
button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_isr)

def is_button_pressed():
    global button_pressed
    return button_pressed

def get_encoder_position():
    global encoder_value
    return encoder_value

