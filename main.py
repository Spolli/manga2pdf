import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import img2pdf
from PyPDF2 import PdfFileMerger, PdfFileReader
from progress.bar import Bar
from PIL import Image

prog_bar = None
manga_url = sys.argv[1]
browser = webdriver.PhantomJS(executable_path='./driver/phantomjs.exe')
# webdriver.Chrome('chromedriver.exe')
pdf_index = 0


def __init__():
    delFilefromFolder('./img')
    delFilefromFolder('./pdf')
    delFilefromFolder('./output')


'''
def remove_transparency(img, bg_colour=(255, 255, 255)):
    im = Image.open(img)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg.filename

    else:
        return img
'''


def mergePDF():
    merger = PdfFileMerger()
    for pdf in reversed([(f'./pdf/{i}') for i in os.listdir('./pdf')]):
        merger.append(PdfFileReader(open(pdf, 'rb')))
    merger.write("./output/final.pdf")
    merger.close()
    delFilefromFolder('./pdf')


def delFilefromFolder(folder_name):
    for the_file in os.listdir(folder_name):
        file_path = os.path.join(folder_name, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def img2pdfConvert():
    global pdf_index
    pdf_name = f'./pdf/{pdf_index:03}.pdf'
    with open(pdf_name, "wb") as f:
        f.write(img2pdf.convert([(
            f'./img/{i}') for i in os.listdir('./img')]))
    pdf_index += 1


def getImagesFromChapter(chapter_url):
    global prog_bar
    browser.get(chapter_url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    manga_images = soup.find_all('img', {'class': 'page-img'}, src=True)
    i = 0
    for image in manga_images:
        name = f'./img/{i:02}.jpeg'
        f = open(name, 'wb')
        f.write(requests.get(image.get('src')).content)
        f.close()
        i += 1
    img2pdfConvert()
    prog_bar.next()
    delFilefromFolder('./img')


def main():
    global prog_bar
    page = requests.get(manga_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    chapters_url = soup.find_all("a", {"class": "chapt"}, href=True)
    prog_bar = Bar(' - Downloading - ', max=len(chapters_url))
    for chapter in chapters_url:
        getImagesFromChapter(f'https://bato.to{chapter.get("href")}')
    prog_bar.finish()
    print('Merging pdfs...')
    mergePDF()


if __name__ == '__main__':
    main()
