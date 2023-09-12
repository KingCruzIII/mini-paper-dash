from PIL import Image, ImageDraw, ImageFont
import epd2in9_V2
import logging
import os
import sys


picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'imgs')

logging.basicConfig(level=logging.DEBUG)

try:
    epd = epd2in9_V2.EPD()
    epd.init()
    epd.Clear(0xFF)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)

except IOError as e:
    logging.info(e)
