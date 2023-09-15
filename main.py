from PIL import Image, ImageDraw, ImageFont
import paho.mqtt.client as mqtt
from TP_lib import epd2in9_V2
from TP_lib import icnt86
import threading
import logging
import time
import json
import os
# 296×128
#Pairs are(horizontal, vertical)
#0-295
#0-127

assetdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')
owlimg = Image.open(os.path.join(assetdir, 'Untitled.bmp'))

logging.basicConfig(level=logging.DEBUG)
flag_t = 1
# current page
page = 1
# refresh count: 0 should refresh, > 0 some time after last refresh
refreshf = 0

haData={}
prevHaData={}

# Touch Listener
def pthread_irq():
    logging.info("pthread irq running")
    while flag_t == 1:
        if (tp.digital_read(tp.INT) == 0):
            ICNT_Dev.Touch = 1
        else:
            ICNT_Dev.Touch = 0
        time.sleep(0.01)
    logging.info("thread irq: exit")
# Increment page and overflow to 0
def page_inc():
    logging.info("@page_inc")
    global page
    global refreshf
    logging.info(refreshf)
    page = page + 1 if page < 2 else 0
    refreshf = 0
    logging.info(refreshf)

# Decrement page and underflow to page count
def page_dec():
    logging.info("@page_dec")
    global page
    global refreshf
    page = page - 1 if page > 0 else 2
    refreshf = 0

def handle_button_zero():
    logging.info("Button Zero Pressed")
    page_dec()
def handle_button_one():
    logging.info("Button One Pressed")
def handle_button_two():
    logging.info("Button Two Pressed")
def handle_button_three():
    logging.info("Button Three Pressed")
def handle_button_four():
    logging.info("Button Four Pressed")
def handle_button_five():
    logging.info("Button Five Pressed")
    page_inc()

buttonList = [[0,49,handle_button_zero],[50,98,handle_button_one],[99,147,handle_button_two],[148,196,handle_button_three],[197,245,handle_button_four],[246,295,handle_button_five]]

def render_buttons(draw):
    for x in buttonList:
        draw.rectangle((x[0], 127, x[1], 77), fill=1, outline=0, width=2)


def handle_button_press(x,y):
    if y < 77: return
    for b in buttonList:
        if x <= b[1]:
            b[2]()
            return

def render_page():
    global refreshf
    logging.info("Starting First Draw")
    Himage = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(Himage)
    render_buttons(draw)

    if page == 0:
        logging.info("Page Zero")
        epd.display(epd.getbuffer(owlimg))
    elif page == 1:
        logging.info("Page One")
        draw.text((10, 0), haData["livingroom_current_temperature"], font=font24, fill=0)
        epd.display(epd.getbuffer(Himage))
    elif page == 2:
        logging.info("Page Two")
        draw.text((10, 0), 'Page Two:', font=font24, fill=0)
        epd.display(epd.getbuffer(Himage))
    else:
        epd.Clear(0xFF)
    refreshf += 1


# on connect sub to things
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("dabs")

# on message callback
def on_message(client, userdata, msg):
    global haData
    global prevHaData
    print("Got Message:"+" "+msg.payload.decode("utf-8"))
    try:
        prevHaData = haData
        haData = json.loads(msg.payload.decode("utf-8"))
    except json.decoder.JSONDecodeError as e:
        logging.info(e)
        logging.info(msg.payload.decode("utf-8"))


logging.info("Starting MQTT Client")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("paper-dash", password="paper-dash")

logging.info("Connect MQTT Client")
client.connect("192.168.1.205", 1883, 60)
logging.info("Looping MQTT Client")
client.loop_start()

try:
    logging.info("Starting Display")
    epd = epd2in9_V2.EPD_2IN9_V2()
    tp = icnt86.INCT86()

    ICNT_Dev = icnt86.ICNT_Development()
    ICNT_Old = icnt86.ICNT_Development()

    logging.info("Init and Clear Display")
    epd.init()
    tp.ICNT_Init()
    epd.Clear(0xFF)

    logging.info("Starting Touch Listener")
    t1 = threading.Thread(target=pthread_irq)
    t1.setDaemon(True)
    t1.start()

    logging.info("Init Fonts")
    font15 = ImageFont.truetype(os.path.join(assetdir, 'Font.ttc'), 15)
    font24 = ImageFont.truetype(os.path.join(assetdir, 'Font.ttc'), 24)

    render_page()

    logging.info("Starting Drawing Loop")
    while (1):
        # logging.info("%s %s", ICNT_Dev.X[0], ICNT_Old.Y[0])
        tp.ICNT_Scan(ICNT_Dev, ICNT_Old)
        if (ICNT_Old.X[0] == ICNT_Dev.X[0] and ICNT_Old.Y[0] == ICNT_Dev.Y[0]):
            continue
    
        if (ICNT_Dev.TouchCount):
            ICNT_Dev.TouchCount = 0
            # logging.info("%s %s", ICNT_Dev.X[0], ICNT_Dev.Y[0])

            # page up(top right)
            if (ICNT_Dev.X[0] > 246 and ICNT_Dev.Y[0] < 50):
                page_inc()
                refreshf = 0
            handle_button_press(ICNT_Dev.X[0], ICNT_Dev.Y[0])


        # only render/refresh when "told to", but check often to refresh
        if refreshf == 0:
            render_page()


except IOError as e:
    logging.info(e)


except KeyboardInterrupt:
    logging.info("ctrl + c:")
    client.loop_stop()
    flag_t = 0
    epd.sleep()
    time.sleep(2)
    t1.join()
    epd.Dev_exit()
    exit()