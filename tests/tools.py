import cv2
import os.path
import subprocess
import numpy as np

# apt: sudo apt install python3-opencv
# pip: pip3 install opencv-python


def render_pdf_to_png(path_pdf: str, path_png: str, dpi: int = 300):
    cmd = ['convert', '-density', str(dpi), path_pdf, '-quality', '100', path_png]
    subprocess.call(cmd)


def check_images_are_identical(path_a: str, path_b: str) -> bool:
    img_a = cv2.imread(path_a)
    img_b = cv2.imread(path_b)
    difference = cv2.subtract(img_a, img_b)
    return not np.any(difference)


def check_identical_pdf(path_pdf: str) -> bool:
    path_png_test = os.path.splitext(path_pdf)[0] + '.test.png'
    path_png_expected = os.path.splitext(path_pdf)[0] + '.png'
    render_pdf_to_png(path_pdf, path_png_test)
    if not os.path.exists(path_png_expected):
        raise FileNotFoundError(path_png_expected)
    return check_images_are_identical(path_png_test, path_png_expected)

