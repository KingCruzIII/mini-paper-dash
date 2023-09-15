from PIL import Image, ImageDraw, ImageFont
from TP_lib import epd2in9_V2
from TP_lib import icnt86
import threading
import logging
import time
import os

assetdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')

# 296×128
logging.basicConfig(level=logging.DEBUG)
flag_t = 1


# touch something?
def pthread_irq():
    logging.info("pthread irq running")
    while flag_t == 1:
        if (tp.digital_read(tp.INT) == 0):
            ICNT_Dev.Touch = 1
        else:
            ICNT_Dev.Touch = 0
        time.sleep(0.01)
    logging.info("thread irq: exit")


try:
    logging.info("Starting")
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

    logging.info("Starting First Draw")
    Himage = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(Himage)

    owlimg = Image.open(os.path.join(assetdir, 'Untitled.bmp'))

    epd.display_Base(epd.getbuffer(Himage))

    logging.info("Starting Drawing Loop")
    while (1):
        # logging.info("%s %s", ICNT_Dev.X[0], ICNT_Old.Y[0])
        tp.ICNT_Scan(ICNT_Dev, ICNT_Old)
        if (ICNT_Old.X[0] == ICNT_Dev.X[0] and ICNT_Old.Y[0] == ICNT_Dev.Y[0]):
            continue
    
        if (ICNT_Dev.TouchCount):
            ICNT_Dev.TouchCount = 0
            if (ICNT_Dev.X[0] <= 100):
                logging.info("left")
                epd.Clear(0xFF)
                draw.text((10, 0), 'Front Door:', font=font24, fill=0)
                draw.line((0, 48, 100, 48), fill=0)
                draw.text((10, 24), '2 hours ago', font=font24, fill=0)
                epd.display_Base(epd.getbuffer(Himage))
            elif(ICNT_Dev.X[0] >= 196):
                epd.Clear(0xFF)
                epd.display(epd.getbuffer(owlimg))
                logging.info("right")
            elif (ICNT_Dev.X[0] > 100 & ICNT_Dev.X[0] < 196):
                logging.info("center")

except IOError as e:
    logging.info(e)


except KeyboardInterrupt:
    logging.info("ctrl + c:")
    flag_t = 0
    epd.sleep()
    time.sleep(2)
    t1.join()
    epd.Dev_exit()
    exit()
