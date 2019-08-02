#!/usr/bin/python
#-*- coding: utf-8 -*-

import re
import xlrd
import xlwt
from  xlutils import copy
import os
import logging
import PyPDF2
from pdf2image import convert_from_path
import string
import pytesseract

logging.basicConfig(level = logging.ERROR,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("Ilogger")


class excels():
    def __init__(self,file_path):
        self.file_path=file_path
        self.values=["path","abstract"]
        self.nums={}
        self.create()
    def create(self):
        rb = xlrd.open_workbook(self.file_path)
        self.r_sheet = rb.sheet_by_index(0)
        self.wb = copy.copy(rb)
        self.w_sheet = self.wb.get_sheet(0)
        self.init_nums()

    def init_nums(self):
        self.list = self.r_sheet.row_values(0)
        for value in self.values:
            print(value)
            print(self.list)
            index = self.list.index(value)
            self.nums[value]=index
        # self.nums["path"]=

    def read(self):

        # self.create()
        print("====")
        for row in range(self.r_sheet.nrows-1):
            row_num=row+1
            print(row_num)
            path=self.r_sheet.cell(row_num,self.nums["path"]).value
            abs=self.r_sheet.cell(row_num,self.nums["abstract"]).value
            print(abs)
            if abs!="":
                continue
            if os.path.exists(path):
                try:
                    print("读取PDF："+path+"...")
                    # text=read(path)
                    # text=text.replace("\n"," ").replace("Abstract:","").replace("Abstract","").strip()
                    pdf_file=open(path, "rb")
                    pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
                    if pdf.getNumPages()>100:
                        pdf_file.close()
                        continue
                    pdf_file.close()
                    text=ocr_read(path)
                    text = text.replace("\n", " ")
                    print(text)
                    self.write(text,row_num)
                except:
                    logger.error("err",exc_info=True)
            else:
                print("路径不存在！")
        self.save()

    def clear_abs(self):
        for row in range(self.r_sheet.nrows - 1):
            row_num = row + 1
            print(row_num)
            abs = self.r_sheet.cell(row_num, self.nums["abstract"]).value
            print(abs)
            if abs != "":
                new_abs=abs_head_clear(abs)
                if new_abs==None:
                    new_abs=""
                self.write(new_abs,row_num)
        self.save()

    def write(self,text,row_num):
        self.w_sheet.write(row_num,self.nums["abstract"],text)


    def save(self):
        self.wb.save(self.file_path)

def py2pdf_read(path):
    file=open(path, "rb")
    pdf = PyPDF2.PdfFileReader(file, strict=False)
    print(pdf.getNumPages())
    print(pdf.getFormTextFields())

def ocr_read(filename):
    print('filename=', filename)
    outputDir="C:/temp/png"

    images = convert_from_path(filename)
    for index, img in enumerate(images):
        if index > 2:
            break
        image_path = '%s/page_%s.png' % (outputDir, index)
        print(image_path)
        img.save(image_path)
        text=get_abs(pytesseract.image_to_string(image_path))
        if text!=None:
            return text

def get_abs(text):
    abs_num=text.lower().find("abstract")
    if abs_num>text.__len__()*9/10:
        abs_num=-1
    if abs_num!=-1:
        keywords_num=text.lower().find("keywords")
        if keywords_num!=-1:
            if keywords_num>abs_num+8:

                return abs_clear(text[abs_num:keywords_num])
        else:
            # print(text)
            abs=""
            for section in get_sections(text[abs_num+8:]):
                if section.__len__()>300:
                    if is_abs(section):
                        abs+=section
                        break
                else:
                    if is_abs(section):
                        abs+=section+"\n"
                        if abs.__len__()>300:
                            break
            return abs_clear(abs)
    else:
        for section in get_sections(text):
            if section.__len__()>300:
                if is_abs(section):
                    num=section.rfind(".")
                    if num >300:
                        return abs_clear(section[:num+1])

def get_sections(text):
    return text.split("\n\n")

def is_abs(abs):
    d = u = l = o = 0

    if "@" in abs:
        print("有@符号！")
        print("摘要：", abs)
        return False
    for i in range(len(abs)):
        if abs[i] in string.digits:
            d += 1
        elif abs[i] in string.ascii_uppercase:
            u += 1
        elif abs[i] in string.ascii_lowercase:
            l += 1
        elif abs[i] in string.punctuation:
            o += 1

    if d/abs.__len__()>0.01:
        print("数字比例过高：", d, d / abs.__len__())
        print("摘要：",abs)
        return False

    if u/ abs.__len__() > 0.05:
        print("大写字母比例过高：", u, u / abs.__len__())
        print("摘要：", abs)
        return False
    if u/ abs.__len__() > 0.1:
        print("标点特殊字符比例过高：", o, o / abs.__len__())
        print("摘要：", abs)
        return False

    return True




def abs_clear(abs):
    abs=abs_head_clear(abs.strip())
    if abs==None:
        return None
    print("last char:",abs[-1])
    if abs[-1] !="." and abs[-1] !="。":
        abs=abs+"."
    return abs
def abs_head_clear(abs):
    if ":" in abs:
        num = abs.find(":")
        if num < 30:
            abs=abs[num+1:].strip()
    else:
        sumnary=re.match("SUMMARY",abs)
        if sumnary!=None:
            abs=abs[sumnary.end():].strip()
    abs=find_upper(abs)
    if abs.__len__()<150:
        print("摘要过短！")
        abs=None
    return abs

def find_upper(abs):
    if abs.__len__()<150:
        return abs
    if abs[0].isupper():
        return abs
    else:
        return find_upper(abs[1:])

def run(excel_path):
    '''
    Excel 要求：Excel第一行为列名，必须有列（）：path，abstract
                path：pdf路径
                abstract：需要补的摘要

    :param excel_path:
    :return:
    '''
    excels(excel_path).read()
    # excels(excel_path).clear_abs()

def run_dir(dir):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet1=wb.add_sheet("sheet1")
    sheet1.write(0, 0, "path")
    sheet1.write(0, 1, "abstract")
    for index,file in enumerate(os.listdir(dir)):
        print(file)
        path=os.path.join(dir,file)
        print(path)


        pdf_file = open(path, "rb")
        pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
        if pdf.getNumPages() > 100:
            pdf_file.close()
            continue
        pdf_file.close()
        text = ocr_read_jpn(path)
        # text = text.replace("\n", " ")
        # print(text)
        # sheet1.write(index+1,0,path)
        # sheet1.write(index+1,1,text)

    wb.save("C:/temp/a.xls")

def ocr_read_jpn(filename):
    print('filename=', filename)
    outputDir = "C:/temp/png"

    images = convert_from_path(filename)
    for index, img in enumerate(images):
        if index > 2:
            break
        image_path = '%s/page_%s.png' % (outputDir, index)
        print(image_path)
        img.save(image_path)
        print(pytesseract.image_to_string(image_path))
        # text = get_abs(pytesseract.image_to_string(image_path,lang="jpn"))
        # if text != None:
        #     return text

if __name__ == '__main__':
    # run("C:/execl/aae6.xlsx")
    run(r"C:\execl\wc_hrl_N-OMICS_20190801_1_20190801_.xlsx")
    # print(ocr_read(r"G:\hrl\0723\zx0723-c2/601fdf5cad3711e9837500ac1f744c94.pdf"))
    # run_dir("C:/temp/新建文件夹")
    # path="C:/pdfs/iccm"
    # c_path="C:/temp/train"
    # for file in os.listdir(path):
    #     file_path=os.path.join(path,file)
    #     print(file_path)
    #     img=convert_from_path(file_path)
    #     img[0].save(os.path.join(c_path,file.replace(".pdf",".jpg")))


    # excels("C:/temp/ISTS1.xls").read()
    # path="C:/temp/oRxeC5q6BgOl.pdf"
    # read(path)
    # path="Z:/数据组内部共享/中信所2019年任务/132/1-東光高岳-69874\httpswww.tktk.co.jpresearchreportpdf2014giho2014_27.pdf"
    # print("=============",read(path))

    # path="Z:/数据组内部共享/中信所2019年任务/补摘要/Japan Society for Aeronautical and Space Sciences 抽/ISTS1/6RyKnw4m14tQ.pdf"
    # py2pdf_read(path)



