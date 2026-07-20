import cv2
import os.path
import subprocess
import numpy as np

from dplot import Figure, TypstGenerator

# apt: sudo apt install python3-opencv
# pip: pip3 install opencv-python

PATH_OUTPUT_DIR_LATEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-latex')
PATH_OUTPUT_DIR_TYPST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out-typst')


def render_pdf_to_png(path_pdf: str, path_png: str, dpi: int = 300):
    cmd = ['convert', '-background', 'white', '-alpha', 'remove', '-density', str(dpi), path_pdf, '-quality', '100', path_png]
    subprocess.call(cmd)


def check_images_are_identical(path_a: str, path_b: str) -> bool:
    img_a = cv2.imread(path_a)
    img_b = cv2.imread(path_b)
    if img_a.shape != img_b.shape:
        raise ValueError('the images do not have the same shape')
    difference = cv2.subtract(img_a, img_b)
    return not np.any(difference)


def check_identical_pdf(path_pdf: str) -> bool:
    path_png_actual = os.path.splitext(path_pdf)[0] + '.actual.png'
    path_png_expected = os.path.splitext(path_pdf)[0] + '.expected.png'
    render_pdf_to_png(path_pdf, path_png_actual)
    if not os.path.exists(path_png_expected):
        raise FileNotFoundError(path_png_expected)
    return check_images_are_identical(path_png_actual, path_png_expected)


def check_embedded_typst_export(fig: Figure) -> bool:
    path_typst, path_typst_pdf = TypstGenerator(fig, standalone=False).export(PATH_OUTPUT_DIR_TYPST, create_pdf=False)
    path_doc_label = os.path.join(os.path.dirname(path_typst), os.path.splitext(os.path.basename(path_typst))[0] + '_embedded')
    path_doc = path_doc_label + '.typ'
    path_doc_pdf = path_doc_label + '.pdf'
    with open(path_doc, 'w') as fp:
        padding_width = 40  # mm
        padding_height = 40  # mm
        fp.write(f'#set page(width: {fig.width + fig.margin['l'] + fig.margin['r'] + padding_width}mm, '
                 f'height: {fig.height + fig.margin['t'] + fig.margin['b'] + padding_height}mm)\n')
        fp.write(f'#figure(box(stroke: 0.1mm+black, include("{os.path.basename(path_typst)}")), caption: "{fig.name}")')

    cmd = ['typst', 'compile', path_doc]
    subprocess.call(cmd)

    return check_identical_pdf(path_doc_pdf)
