import os, sys
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import SignalInstance
from Resources.Addons import RESOURCE_PATH, TMP_PATH, LOGO_PATH, PREVIEW_PATH, PREVIEW_SAMPLE_PATH, keygen

FONT = ImageFont.truetype('Resources/Font/NANUMGOTHIC.TTF', size=20)

def generate_logo_preview(texts:list[str], settings:dict, signal:SignalInstance=None):
  signal.emit(0)
  path = os.path.join(TMP_PATH, 'preview_test.png')
  logo = Image.open(LOGO_PATH)
  
  # 텍스트 줄 수 확인
  # text_count = len([x for x in texts[:3] if x or x != ' '])
  # if settings["align"] + 1 < text_count:
  #   line_count = text_count//(settings["align"]+1) + 1 if settings["align"] != 0 else text_count
  # else:
  #   line_count = 1
  line_count = len([x for x in texts[:3] if x or x != ' '])
  
  # 워터마크 크기 정의
  thumb_h = 900
  thumb_w = 900
  if settings["text_location"] == 1:
    thumb_w = 50*line_count
    loc = [0, 0]
  elif settings["text_location"] > 1:
    thumb_h = 50*line_count
    if settings["text_location"] == 2:
      loc = [0, 0]
    else:
      length = max([len(x) for x in texts])*25
      loc = [length, 0]
  else:
    thumb_h = 150
  
  signal.emit(1)
  logo.thumbnail([thumb_w, thumb_h])
  background = Image.new('RGBA', (900, 900))
  background.paste(logo.convert('RGBA'), loc, logo.convert('RGBA'))
  preview = ImageDraw.Draw(background)

  if settings["text_location"] == 1:
    startpoint = [0, logo.size[1]]
  elif settings["text_location"] == 2:
    startpoint = [0, 0]
  elif settings["text_location"] == 3:
    startpoint = [logo.size[0], 0]
  # 글씨 넣기
  textpoint = startpoint
  for line in range(line_count+1):
    preview.text(textpoint, texts[line], (1,1,1),FONT)
    textpoint[1] = textpoint[1]+30

  signal.emit(2)
  background.save(path)
  cord = [0, 0]
  isEndPoint = False
  for x in range(background.size[0]-1, -1, -1):
    for y in range(background.size[1]-1, -1, -1):
      pixel = background.getpixel((x, y))
      if sum(pixel) != 0:
        isEndPoint = True
        break
    if isEndPoint:
      break
  cord[0] = (x//10+1)*10
  
  isEndPoint = False
  for y in range(background.size[0]-1, -1, -1):
    for x in range(background.size[1]-1, -1, -1):
      pixel = background.getpixel((x, y))
      if sum(pixel) != 0:
        isEndPoint = True
        break
    if isEndPoint:
      break
  cord[1] = (y//10+1)*10

  signal.emit(8)
  crop = background.crop((0, 0, *cord))
  crop.save(PREVIEW_PATH)
  crop.thumbnail((200, 200))
  crop.save(PREVIEW_SAMPLE_PATH)
  signal.emit(10)
  

def generate_img_preview():...

def generate_image():...