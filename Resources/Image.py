import os, sys, traceback, shutil
from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import SignalInstance
from Resources.Addons import keygen, gen_watermark_name, RESOURCE_PATH, TMP_PATH, LOGO_PATH, WATERMARK_PATH, WATERMARK_SAMPLE_PATH, MAIN_IMAGE_PATH

FONT = ImageFont.truetype('Resources/Font/NANUMGOTHIC.TTF', size=100)

def generate_mask(img:Image.Image, percent:int=100):
  orig = img.convert('RGBA')
  # 각 픽셀의 투명도 조절
  mask = []
  for pixel in orig.getdata(3):
    if pixel != 0:
      alpha = pixel
      alpha_alt = int(alpha*percent/100)
      mask.append(alpha_alt)
    else:
      mask.append(pixel)
  # 알파 마스크 생성
  alpha_mask = Image.new('L', orig.size, 255)
  alpha_mask.putdata(mask)
  # 투명도 덧붙이기
  orig.putalpha(alpha_mask)
  return orig

def generate_logo_preview(texts:list[str], settings:dict, signal:SignalInstance=None):
  try:
    signal.emit(1)
    path = os.path.join(TMP_PATH, 'preview_test.png')
    logo = Image.open(LOGO_PATH)
    
    # 텍스트 줄 수 확인
    # text_count = len([x for x in texts[:3] if x or x != ' '])
    # if settings["align"] + 1 < text_count:
    #   line_count = text_count//(settings["align"]+1) + 1 if settings["align"] != 0 else text_count
    # else:
    #   line_count = 1
    line_count = len([x for x in texts[:3] if x != ' '])

    # 워터마크 크기 정의
    thumb_h = 2000
    thumb_w = 2000
    if settings["text_location"] == 1:
      thumb_w = 180*(line_count+2)
      loc = [0, 0]
    elif settings["text_location"] == 2:
      thumb_h = 180*line_count
      length = max([len(x) for x in texts])*10
      loc = [length, 0]
    elif settings["text_location"] == 3:
      thumb_h = 180*line_count
      loc = [0, 0]
    else:
      thumb_h = 900
      loc = [0, 0]
    
    signal.emit(2)
    logo.thumbnail([thumb_w, thumb_h])
    background = Image.new('RGBA', (2000, 1000))
    background.paste(logo.convert('RGBA'), loc, logo.convert('RGBA'))
    preview = ImageDraw.Draw(background)

    if settings["text_location"] != 0:
      if settings["text_location"] == 1:
        startpoint = [0, logo.size[1]+20]
      elif settings["text_location"] == 2:
        startpoint = [0, 0]
      elif settings["text_location"] == 3:
        startpoint = [logo.size[0]+20, 0]
      # 글씨 넣기
      textpoint = startpoint
      for line in range(line_count+1):
        line_text = [x for x in texts if x != ' ']
        preview.text(textpoint, line_text[line], (1,1,1),FONT)
        textpoint[1] = textpoint[1]+110

      signal.emit(3)
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
      cord[0] = (x//10+3)*10
      
      signal.emit(6)
      isEndPoint = False
      for y in range(background.size[1]-1, -1, -1):
        for x in range(cord[0]):
          pixel = background.getpixel((x, y))
          if sum(pixel) != 0:
            isEndPoint = True
            break
        if isEndPoint:
          break
      cord[1] = (y//10+3)*10
    else:
      cord = [900, 900]

    signal.emit(8)
    crop = background.crop((0, 0, *cord))
    crop.save(WATERMARK_PATH)
    crop.thumbnail((290, 150))
    crop.save(WATERMARK_SAMPLE_PATH)
    signal.emit(10)
  except Exception as e:
    print(e)
    print(traceback.format_exc())
    signal.emit(str(e))
  

def generate_img_preview():...

def generate_image(settings:dict, filename:str, signal:SignalInstance=None):
  try:
    signal.emit(1)
    watermark = Image.open(WATERMARK_PATH).convert('RGBA')
    main_image = Image.open(MAIN_IMAGE_PATH)

    print(settings)
    rotation = settings["orientation"]
    base_location = settings["mark_location"]
    custom_location = settings["mark_custom_location"]
    mark_size = settings["mark_size"]
    mark_type = settings["type"]
    alpha = settings["alpha"]

    signal.emit(2)
    if rotation > 0:
      watermark = watermark.rotate(-rotation, expand=True)


    if mark_type == 0 or mark_type == 3:
      if mark_size[1] == 0:
        watermark.thumbnail((mark_size[0],2000))
      elif mark_size[1] == 1:
        watermark.thumbnail((int(main_image.width*mark_size[0]/100),2000))
      signal.emit(4)

      if base_location == 0:    # 중앙
        pos = [int(main_image.width/2 - watermark.width/2), int(main_image.height/2 - watermark.height/2)]
      elif base_location == 1:  # 좌상단
        pos = [0, 0]
      elif base_location == 2:  # 상단
        pos = [int(main_image.width/2 - watermark.width/2), 0]
      elif base_location == 3:  # 우상단
        pos = [main_image.width - watermark.width, 0]
      elif base_location == 4:  # 좌
        pos = [0, int(main_image.height/2 - watermark.height/2)]
      elif base_location == 5:  # 우
        pos = [main_image.width - watermark.width, int(main_image.height/2 - watermark.height/2)]
      elif base_location == 6:  # 좌하단
        pos = [0, main_image.height - watermark.height]
      elif base_location == 7:  # 하단
        pos = [int(main_image.width/2 - watermark.width/2), main_image.height - watermark.height]
      elif base_location == 8:  # 우하단
        pos = [main_image.width - watermark.width, main_image.height - watermark.height]
      elif base_location == 9:  # 지정 위치
        if custom_location[2] == 0:
          pos = [*custom_location[:2]]
        else:
          pos = [int(main_image.width*custom_location[0]/100 - watermark.width/2), int(main_image.height*custom_location[1]/100 - watermark.height/2)]
    signal.emit(6)

    if mark_type == 0:
      main_image.paste(watermark, pos, generate_mask(watermark, alpha))
    elif mark_type == 1:
      ratio = watermark.size[1]/watermark.size[0]
      watermark_size = [main_image.size[0], int(main_image.size[0]*ratio)]
      watermark = watermark.resize(watermark_size)
      pos = [int((main_image.size[0] - watermark.size[0])/2), int((main_image.size[1]-watermark.size[1])/2)]
      main_image.paste(watermark, pos, generate_mask(watermark, alpha))
    elif mark_type == 2:
      watermark = watermark.resize(main_image.size)
      main_image.paste(watermark, [0,0], generate_mask(watermark, alpha))
    elif mark_type == 3:
      startpoint = [0, 0]
      startpoint[0] = int(pos[0]-watermark.size[0]*((pos[0]-watermark.size[0]/2)//watermark.size[0]+1.5))
      startpoint[1] = int(pos[1]-watermark.size[1]*((pos[1]-watermark.size[1]/2)//watermark.size[1]+1.5))
      # print('startpoint: ', startpoint)
      point = [*startpoint]
      mask = generate_mask(watermark, alpha)
      while point[0] < main_image.size[0]:
        while point[1] < main_image.size[1]:
          target = [*point]
          watermark_tmp = watermark
          mask_tmp = mask
          if target[0] < 0:
            watermark_tmp = watermark_tmp.crop((-target[0], 0, *watermark_tmp.size))
            mask_tmp = generate_mask(watermark_tmp, alpha)
            target[0] = 0
          elif target[0]+watermark_tmp.size[0] > main_image.size[0]:
            watermark_tmp = watermark_tmp.crop((0, 0, watermark_tmp.size[0]-(target[0]+watermark_tmp.size[0]-main_image.size[0]), watermark_tmp.size[1]))
            mask_tmp = generate_mask(watermark_tmp, alpha)

          if target[1] < 0:
            watermark_tmp = watermark_tmp.crop((0, -target[1], *watermark_tmp.size))
            mask_tmp = generate_mask(watermark_tmp, alpha)
            target[1] = 0
          elif target[1]+watermark_tmp.size[1] > main_image.size[1]:
            watermark_tmp = watermark_tmp.crop((0, 0, watermark_tmp.size[0], watermark_tmp.size[1]-(target[1]+watermark_tmp.size[1]-main_image.size[1])))
            mask_tmp = generate_mask(watermark_tmp, alpha)

          main_image.paste(watermark_tmp, target, mask_tmp)
          point[1] = point[1]+watermark.size[1]
        point[0] = point[0]+watermark.size[0]
        point[1] = startpoint[1]
        # print('point: ', point)
    signal.emit(8)


    tmp_path = os.path.join(TMP_PATH, f'{keygen()}.png')
    main_image.save(tmp_path)
    shutil.copy(tmp_path, gen_watermark_name(filename))
    signal.emit(10)
  except Exception as e:
    print(e)
    print(traceback.format_exc())
    signal.emit(str(e))