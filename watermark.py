#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont
import piexif
from datetime import datetime

def get_shooting_date(image_path):
    try:
        image = Image.open(image_path)
        exif_dict = piexif.load(image.info.get('exif', b''))
        date_str = exif_dict['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
        if date_str:
            dt = datetime.strptime(date_str.decode('utf-8'), '%Y:%m:%d %H:%M:%S')
            return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"无法读取 {image_path} 的EXIF信息: {e}")
    return None

def add_watermark(image_path, text, font_size, color, position):
    image = Image.open(image_path).convert("RGBA")
    txt = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    img_width, img_height = image.size

    if position == '左上角':
        x, y = 10, 10
    elif position == '居中':
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    elif position == '右下角':
        x = img_width - text_width - 10
        y = img_height - text_height - 10
    else:
        print("无效位置，默认居中")
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2

    draw.text((x, y), text, fill=color + (255,), font=font)
    combined = Image.alpha_composite(image, txt).convert("RGB")
    return combined

def process_directory(input_dir):
    output_dir = os.path.join(input_dir, os.path.basename(input_dir.rstrip('/')) + "_watermark")
    os.makedirs(output_dir, exist_ok=True)

    font_size = int(input("请输入字体大小（如 40）："))
    color_input = input("请输入字体颜色（RGB，如 255 255 255）：").strip().split()
    color = tuple(int(c) for c in color_input)
    position = input("请输入水印位置（左上角/居中/右下角）：").strip()

    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(input_dir, filename)
            date_text = get_shooting_date(file_path)
            if not date_text:
                print(f"跳过 {filename}，无拍摄时间")
                continue
            new_image = add_watermark(file_path, date_text, font_size, color, position)
            output_path = os.path.join(output_dir, filename)
            new_image.save(output_path)
            print(f"已保存：{output_path}")

if __name__ == "__main__":
    input_path = input("请输入图片所在目录路径：").strip()
    if not os.path.isdir(input_path):
        print("路径无效，请输入一个有效目录")
    else:
        process_directory(input_path)