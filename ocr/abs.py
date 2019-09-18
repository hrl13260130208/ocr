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
import redis
from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import sys

FILE_NAME_QUEUE="file_name_queue"

redis_ = redis.Redis(host="10.3.1.99", port=6379, db=5,decode_responses=True)
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout)
logging.root.setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("Ilogger").setLevel(logging.INFO)
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
    logger.info('PDF路径：'+ filename)
    if not os.path.exists(filename):
        raise ValueError("PDF不存在！")

    outputDir="C:/temp/png"
    try:
        images = convert_from_path(filename)
        for index, img in enumerate(images):
            if index > 10:
                break
            image_path = '%s/page_%s.png' % (outputDir, index)
            logger.info("临时图片路径："+image_path)
            img.save(image_path)
            text=get_abs(pytesseract.image_to_string(image_path))
            if text!=None:
                return text
    except:
        pass

def pdfminer_read(path):
    fp = open(path, 'rb')
    # 用文件对象创建一个PDF文档分析器
    parser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器，与文档对象
    parser.set_document(doc)
    doc.set_parser(parser)

    # 提供初始化密码，如果没有密码，就创建一个空的字符串
    doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDF，资源管理器，来共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释其对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        text=""
        # 循环遍历列表，每次处理一个page内容
        # doc.get_pages() 获取page列表
        for page in doc.get_pages():
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
            # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
            # 想要获取文本就获得对象的text属性，
            for x in layout:
                if (isinstance(x, LTTextBoxHorizontal)):

                        results = x.get_text()
                        if is_abs(results):
                            text=abs_clear(results)
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
        logger.debug("有@符号！")
        logger.debug("摘要：", abs)
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
    logger.debug("数字字符："+str(d)+" 大写字母字符："+str(u)+" 标点字符："+str(o)+"字符总数："+str(abs.__len__()))
    if d/abs.__len__()>0.01:
        logger.debug("数字比例过高："+str(d)+"  "+str( d / abs.__len__()))
        logger.debug("摘要："+str(abs))
        return False

    if u/ abs.__len__() > 0.05:
        logger.debug("大写字母比例过高："+str(u)+"  "+str( u / abs.__len__()))
        logger.debug("摘要："+str(abs))
        return False
    if o/ abs.__len__() > 0.1:
        logger.debug("标点特殊字符比例过高："+str(o)+"  "+str( o / abs.__len__()))
        logger.debug("摘要："+str( abs))
        return False

    return True




def abs_clear(abs):
    abs=abs_head_clear(abs.strip())
    if abs==None:
        return None
    logger.debug("last char:"+abs[-1])
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
        logger.debug("摘要过短！")
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

def write_pages_and_absurl(excel_name):
    rb = xlrd.open_workbook(excel_name)
    r_sheet = rb.sheet_by_index(0)
    wb = copy.copy(rb)
    w_sheet = wb.get_sheet(0)
    list = r_sheet.row_values(0)

    total_pages_num = list.index("TOTALPAGES")
    pages_num = list.index("page")
    absurlnum=list.index("ABS_URL")
    url_num=list.index("PINJIE")
    pmc_num=list.index("WAIBUAID")
    sn_num=list.index("SOURCENAME")

    for row in range(r_sheet.nrows - 1):
        tp=r_sheet.cell(row+1,total_pages_num)
        abs_url=r_sheet.cell(row+1,absurlnum).value
        print("==============",tp.value)
        if tp.value=="":
            page=r_sheet.cell(row+1,pages_num)
            print(page)
            if page.value!="":
                w_sheet.write(row+1,total_pages_num,page.value)
        sn = r_sheet.cell(row + 1, sn_num)
        print(sn)
        if abs_url=="":
            sn=r_sheet.cell(row+1,sn_num)
            print(sn.value)
            if sn.value=="PMC":
                w_sheet.write(row + 1, absurlnum,"https://www.ncbi.nlm.nih.gov/pmc/articles/"+r_sheet.cell(row+1,pmc_num).value)
            else:
                w_sheet.write(row + 1, absurlnum, r_sheet.cell(row + 1,url_num).value)

    wb.save(excel_name)

def run_text(text_path,pdf_dir,abs_text_path=r"G:\hrl\adams1\adams\abs.txt",update=False,skip_first=False):
    if redis_.llen(FILE_NAME_QUEUE)>0:
        if update:
            queue_update(text_path)
    else:
        queue_update(text_path)

    if skip_first:
        redis_.rpush(FILE_NAME_QUEUE,redis_.lpop(FILE_NAME_QUEUE))

    with open(abs_text_path,"a+",encoding="utf-8") as abs:
        while(redis_.llen(FILE_NAME_QUEUE)>0):
            pdf_name=redis_.lindex(FILE_NAME_QUEUE,0)
            logger.info("开始处理文件："+pdf_name)
            pdf_path=os.path.join(pdf_dir,pdf_name+".pdf")

            if os.path.exists(pdf_path):
                try:
                    text=pdfminer_read(pdf_path)
                    # if text==None:
                    #     logger.info("pdf未抽取到摘要，尝试使用ocr识别...")
                    #     text = ocr_read(pdf_path)
                    if text!=None:
                        logger.info("抽取到摘要："+text.replace("\n",""))
                        abs.write(pdf_name+"$$$$"+text.replace("\n","")+"\n")
                except:
                    redis_.lpop(FILE_NAME_QUEUE)
            else:
                logger.info("文件不存在！")
            redis_.lpop(FILE_NAME_QUEUE)



def queue_update(text_path):
    logger.info("更新redis队列...")
    with open(text_path,"r+",encoding="utf-8") as f:
        for line in f.readlines():
            args=line.replace("\n","").split("$$$$")
            if args.__len__() !=4:
                logger.warning("分割有误！lien="+line)
                continue
            redis_.lpush(FILE_NAME_QUEUE,args[1])


if __name__ == '__main__':
    run(r"C:\public\目次采全文\0909\中信所缺失摘要清单_20190909..xls")
    # run_text(r"G:\hrl\adams1\adams\adams1.txt",r"G:\hrl\adams1\adams\1950-2010",skip_first=True)
    # logger.debug("ks")
    # print(is_abs("Introduction .................................................................................................................................................... 3."))
    # run(r"G:\hrl\adams1\adams\adams.xls")
    # for key in redis_.keys("*"):
    #     redis_.delete(key)
    # write_pages_and_absurl(r"C:\public\目次采全文\0909\中信所待补全文清单_20190909..xls")
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

    # set1=set()
    # abs=dict()
    # for item in open(r"H:\hrl\adams1\adams\abs.txt",encoding="utf-8").readlines():
    #     print(item)
    #     args=item.replace("\n","").split("$$$$")
    #     abs[args[0]]=args[1]
    # for item in open(r"H:\hrl\adams1\adams\nofind.txt",encoding="utf-8").readlines():
    #     set1.add(item.replace("\n",""))
    #
    # file1=open(r"H:\hrl\adams1\adams\adams_find.txt","w+",encoding="utf-8")
    # file2=open(r"H:\hrl\adams1\adams\adams_nofind.txt","w+",encoding="utf-8")
    #
    # for item in open(r"H:\hrl\adams1\adams\adams1.txt","r",encoding="utf-8").readlines():
    #     args=item.replace("\n","").split("$$$$")
    #     if args[1] in set1:
    #         file2.write(item)
    #     elif args[1] in abs:
    #         file1.write(args[0]+"$$$$empty$$$$"+abs[args[1]]+"$$$$"+args[3]+"$$$$0$$$$"+args[1]+"\n")
    #     else:
    #         file1.write(args[0] + "$$$$empty$$$$empty$$$$" + args[3] + "$$$$0$$$$" + args[1] + "\n")




