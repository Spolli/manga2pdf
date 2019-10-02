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
splitIndex = 0

folder_path = {
    "img": "./tmp/img",
    "pdf": "./tmp/pdf",
    "pdfs": "./tmp/pdfs",
    "output": "./output"
}


def __init__():
    delFilefromFolder(folder_path["img"])
    delFilefromFolder(folder_path["pdf"])
    delFilefromFolder(folder_path["pdfs"])


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

    tmp_index = 0

    for pdf_subList in splitList(reversed([(f'{folder_path["pdf"]}/{i}') for i in os.listdir(folder_path['pdf'])])):
        for pdf in pdf_subList:
            merger.append(PdfFileReader(open(pdf, 'rb')))
        merger.write(f"{folder_path['pdfs']}/{pdf_index:02}.pdf")
        merger.close()
    for tmp_pdf in [(f'{folder_path["pdfs"]}/{i}') for i in os.listdir(folder_path['pdfs'])]:
        merger.append(PdfFileReader(open(tmp_pdf, 'rb')))
    merger.write(f"{folder_path['output']}/final.pdf")
    merger.close()


def delFilefromFolder(folder_name):
    for the_file in os.listdir(folder_name):
        file_path = os.path.join(folder_name, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

def delPDFfromList(list_name):
    for the_file in os.listdir(folder_name):
        file_path = os.path.join(folder_path['pdf'], the_file)
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

def convert2Pdf():
    global pdf_index
    pdf_file = Image.new(mode='RGB', size=(100, 100), color=0)
    pdf_name = f'{folder_path["pdf"]}/{pdf_index:03}.pdf'
    imList = [Image.open(f'{folder_path["img"]}/{i}') for i in os.listdir(folder_path["img"])]
    pdf_file.save(pdf_name, "PDF" ,resolution=100.0, save_all=True, append_images=imList)
    pdf_file.close()
    pdf_index += 1

def getImagesFromChapter(chapter_url):
    global prog_bar
    browser.get(chapter_url)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    manga_images = soup.find_all('img', {'class': 'page-img'}, src=True)
    i = 0
    for image in manga_images:
        name = f'{folder_path["img"]}/{i:02}.jpeg'
        f = open(name, 'wb')
        f.write(requests.get(image.get('src')).content)
        f.close()
        i += 1
    convert2Pdf()
    delFilefromFolder(folder_path["img"])
    prog_bar.next()

def clearFolders():
    delFilefromFolder('./img')
    delFilefromFolder('./pdf')

def splitList(my_list, split_condition=splitIndex):
    return [my_list[x:x+split_condition] for x in range(0, len(my_list),split_condition)]       #split list every tot number


if __name__ == '__main__':
    global prog_bar, splitIndex
    page = requests.get(manga_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    chapters_url = soup.find_all("a", {"class": "chapt"}, href=True)
    splitIndex = len(chapters_url) < 50 ? len(chapters_url) / 4 : 1     #split if chapers are > 50 else not split
    prog_bar = Bar('\t\tDownloading\t\t', max=len(chapters_url))
    for chapter in chapters_url:
        getImagesFromChapter(f'https://bato.to{chapter.get("href")}')
    prog_bar.finish()
    print('Merging pdfs...')
    mergePDF()
    clearFolders()
