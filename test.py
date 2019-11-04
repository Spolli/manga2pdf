#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup
import requests
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
from progress.bar import Bar
from PIL import Image
import math

# Global Variables
###########################################################################
prog_bar = None
manga_url = sys.argv[1]
manga_name = "final"  # sys.argv[2] if sys.argv[2] is None else "final"
pdf_index = 0
splitIndex = None

folder_path = {
    "img": "./src/tmp/img",
    "pdf": "./src/tmp/pdf",
    "pdfs": "./src/tmp/pdfs",
    "output": "./output"
}
###########################################################################

'''
def __init__():
    # clearFolders()
'''


def grouperList(l):
    return [l[i:i + splitIndex] for i in range(0, len(l), splitIndex)]


def getImagesFromChapter(chapter_url):
    global prog_bar
    r = requests.get(chapter_url)
    soup = BeautifulSoup(r.content, "lxml")
    manga_images = soup.find_all('img', attrs={'class': 'page-img'}, src=True)
    for i, image in enumerate(manga_images):
        name = f'{folder_path["img"]}/{i:02}.jpeg'
        f = open(name, 'wb')
        f.write(requests.get(image.get('src')).content)
        f.close()
    convert2Pdf()
    delFilefromFolder(folder_path["img"])
    prog_bar.next()


def convert2Pdf():
    global pdf_index
    pdf_file = Image.new('RGB', size=(100, 100), color=(255, 255, 255))
    pdf_name = f'{folder_path["pdf"]}/{pdf_index:03}.pdf'
    imList = [Image.open(f'{folder_path["img"]}/{i}').convert('RGB')
              for i in os.listdir(folder_path["img"])]
    pdf_file.save(pdf_name, "PDF", resolution=100.0,
                  save_all=True, append_images=imList)
    pdf_file.close()
    pdf_index += 1


def mergePDF():
    if splitIndex is None:
        merger = PdfFileMerger()
        for pdf in reversed([(f'{folder_path["pdf"]}/{i}') for i in os.listdir(folder_path['pdf'])]):
            merger.append(PdfFileReader(open(pdf, 'rb')))
        merger.write(f"{folder_path['output']}/{manga_name}.pdf")
        merger.close()
    else:
        tmp_index = 0
        for pdf_subList in grouperList(list(reversed([(f'{folder_path["pdf"]}/{i}') for i in os.listdir(folder_path['pdf'])]))):
            merger = PdfFileMerger()
            for pdf in pdf_subList:
                merger.append(PdfFileReader(open(pdf, 'rb')))
            merger.write(f"{folder_path['pdfs']}/{tmp_index:02}.pdf")
            merger.close()
            # delPDFfromList(pdf_subList)
            tmp_index += 1
        merger = PdfFileMerger()
        for tmp_pdf in [(f'{folder_path["pdfs"]}/{i}') for i in os.listdir(folder_path['pdfs'])]:
            merger.append(PdfFileReader(open(tmp_pdf, 'rb')))
        merger.write(f"{folder_path['output']}/{manga_name}.pdf")
        merger.close()


def clearFolders():
    delFilefromFolder(folder_path["img"])
    delFilefromFolder(folder_path["pdf"])
    delFilefromFolder(folder_path["pdfs"])


def delFilefromFolder(folder_name):
    for the_file in os.listdir(folder_name):
        file_path = os.path.join(folder_name, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def delPDFfromList(list_name):
    for the_file in os.listdir(folder_path['pdf']):
        file_path = os.path.join(folder_path['pdf'], the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def main():
    page = requests.get(manga_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    chapters_url = soup.find_all("a", {"class": "chapt"}, href=True)
    global prog_bar, splitIndex
    # split if chapers are > 50 else not split
    splitIndex = math.floor(
        len(chapters_url) / 4) if len(chapters_url) > 50 else None
    prog_bar = Bar('\t\tDownloading\t\t', max=len(chapters_url))
    for chapter in chapters_url:
        getImagesFromChapter(f'https://bato.to{chapter.get("href")}')
    prog_bar.finish()
    print('Merging pdfs...')
    #prog_bar = Bar('\t\Merging\t\t', max=len(chapters_url))
    mergePDF()
    clearFolders()


if __name__ == '__main__':
    clearFolders()
    main()
