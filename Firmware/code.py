import time
import board
import busio
import keypad
import adafruit_ssd1306
import neopixel
import random
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

i2c = busio.I2C(scl=board.D5, sda=board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
status_led = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)

row_pins = (board.D6, board.D3, board.D2, board.D1) 
col_pins = (board.D7, board.D8, board.D9, board.D10)

km = keypad.KeyMatrix(row_pins, col_pins, columns_to_anodes=True, interval=0.005)


try:
    kbd = Keyboard(usb_hid.devices)
    hid_active = True
except:
    hid_active = False


CHAR_MAP = ["1", "2", "3", "DEL", "4", "5", "6", "+", "7", "8", "9", "-", "0", "SPC", "ENT", "MENU"]
HID_MAP = [
    Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.BACKSPACE,
    Keycode.FOUR, Keycode.FIVE, Keycode.SIX, Keycode.KEYPAD_PLUS,
    Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE, Keycode.MINUS,
    Keycode.ZERO, Keycode.SPACE, Keycode.ENTER, None
]


def draw_ui(l1, l2="", inv=False):
    display.fill(0)
    display.rect(0, 0, 128, 32, 1)
    if inv:
        display.fill_rect(2, 2, 124, 28, 1)
        display.text(str(l1), 6, 6, 0)
        display.text(str(l2), 6, 18, 0)
    else:
        display.text(str(l1), 6, 6, 1)
        display.text(str(l2), 6, 18, 1)
    display.show()



def run_pc_kbd():
    draw_ui("PC KEYBOARD", "MENU TO EXIT", True)
    while True:
        event = km.events.get()
        if event:
            idx = event.key_number
            if CHAR_MAP[idx] == "MENU" and event.pressed: return
            code = HID_MAP[idx]
            if code and hid_active:
                if event.pressed:
                    kbd.press(code)
                    status_led[0] = (0, 255, 0)
                else:
                    kbd.release(code)
                    status_led[0] = (0, 0, 0)

def run_memory_game():
    seq = []
    while True:
        seq.append(random.randint(0, 9))
        for n in seq:
            draw_ui("WATCH:", str(n), True)
            time.sleep(0.6)
            draw_ui("WATCH:", " ", False)
            time.sleep(0.2)
        draw_ui("YOUR TURN!", "GO!")
        for correct in seq:
            guess = None
            while guess is None:
                ev = km.events.get()
                if ev and ev.pressed:
                    val = CHAR_MAP[ev.key_number]
                    if val.isdigit(): guess = int(val)
                    elif val == "MENU": return
            if guess != correct:
                draw_ui("FAIL!", f"SCORE: {len(seq)-1}", True)
                status_led[0] = (255, 0, 0)
                time.sleep(2)
                status_led[0] = (0, 0, 0)
                return
        draw_ui("CORRECT!", "NEXT...")
        status_led[0] = (0, 255, 0)
        time.sleep(0.8)
        status_led[0] = (0, 0, 0)

def run_mole_game():
    score = 0
    for i in range(10):
        target = random.randint(0, 11)
        draw_ui(f"HIT: {CHAR_MAP[target]}", f"SCORE: {score}", True)
        start = time.monotonic()
        hit = False
        while time.monotonic() - start < 1.2:
            ev = km.events.get()
            if ev and ev.pressed:
                if ev.key_number == target:
                    score += 1
                    hit = True
                    break
                elif CHAR_MAP[ev.key_number] == "MENU": return
        status_led[0] = (0, 255, 0) if hit else (255, 0, 0)
        time.sleep(0.3)
        status_led[0] = (0, 0, 0)
    draw_ui("GAME OVER", f"SCORE: {score}")
    time.sleep(2)

def run_calc():
    expr = ""
    while True:
        draw_ui("CALC (ENT:=)", expr)
        ev = km.events.get()
        if ev and ev.pressed:
            val = CHAR_MAP[ev.key_number]
            if val == "MENU": return
            elif val == "ENT":
                try: expr = str(eval(expr.replace('SPC', '')))
                except: expr = "ERR"
            elif val == "DEL": expr = ""
            else: expr += val

def run_24_game():
    nums = [random.randint(1, 9) for _ in range(4)]
    draw_ui("MAKE 24", f"NUMS: {nums}")
    while True:
        ev = km.events.get()
        if ev and ev.pressed and CHAR_MAP[ev.key_number] == "MENU": return

def run_sleep():
    while True:
        for f in ["( - . - ) zZZ", "( - o - ) zZ ", "( ^ . ^ )  *"]:
            draw_ui("SLEEPING...", f)
            time.sleep(1)
            ev = km.events.get()
            if ev and ev.pressed and CHAR_MAP[ev.key_number] == "MENU": return


menu_items = ["PC KEYBOARD", "CALCULATOR", "MEMORY GAME", "24 GAME", "WHACK-A-MOLE", "SLEEP MODE"]
m_idx = 0
start_idx = 0

while True:
    
    if m_idx < start_idx: start_idx = m_idx
    elif m_idx >= start_idx + 3: start_idx = m_idx - 2
    
    display.fill(0)
    for i in range(3):
        idx = start_idx + i
        if idx < len(menu_items):
            y = i * 11
            if idx == m_idx:
                display.fill_rect(0, y, 122, 10, 1)
                display.text(menu_items[idx], 4, y + 1, 0)
            else:
                display.text(menu_items[idx], 4, y + 1, 1)
    display.fill_rect(125, int(m_idx * (32/len(menu_items))), 2, 5, 1)
    display.show()

    ev = km.events.get()
    if ev and ev.pressed:
        v = CHAR_MAP[ev.key_number]
        if v == "+": m_idx = (m_idx - 1) % len(menu_items)
        elif v == "-": m_idx = (m_idx + 1) % len(menu_items)
        elif v == "ENT":
            mode = menu_items[m_idx]
            if mode == "PC KEYBOARD": run_pc_kbd()
            elif mode == "CALCULATOR": run_calc()
            elif mode == "MEMORY GAME": run_memory_game()
            elif mode == "WHACK-A-MOLE": run_mole_game()
            elif mode == "24 GAME": run_24_game()
            elif mode == "SLEEP MODE": run_sleep()
