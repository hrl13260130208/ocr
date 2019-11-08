
import time
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
from stanfordcorenlp import StanfordCoreNLP

outputDir="C:/temp/png"
nlp = StanfordCoreNLP(r'C:\File\stanford-corenlp-full-2016-10-31')


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout)
logging.root.setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("Ilogger").setLevel(logging.INFO)
logger=logging.getLogger("Ilogger")

def ocr_reader(filename):
    author_line=""
    images = convert_from_path(filename)
    for index, img in enumerate(images):
        if index > 10:
            break
        image_path = '%s/page_%s.png' % (outputDir, index)
        print(image_path)
        img.save(image_path)
        text=pytesseract.image_to_string(image_path)

        for line_index,line in enumerate(get_sections(text)):
            if author_analyze(line):
                author_line+=line
        break
    return author_line
def pdfminer_reader(filename):
    author_line=""
    for text in pdfminer_read_all(filename):

        for index,line in enumerate(text.split("\n")):
            if author_analyze(line):
                author_line+=line
        break
    return author_line

def author_analyze(text):
    authors = {}
    find=False
    # print(text)
    r = nlp.ner(text)
    author_len=0

    for item in r:
        if item[1] == "PERSON":
            find=True
            author_len+=len(item[0])

    if find:
        return author_len/len(text)>0.5
    else:
        return False


def get_sections(text):
    return text.split("\n\n")



def pdfminer_read_all(path):

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


        # 循环遍历列表，每次处理一个page内容
        # doc.get_pages() 获取page列表
        for page in doc.get_pages():

            text=""
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
            # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
            # 想要获取文本就获得对象的text属性，
            for x in layout:
                if (isinstance(x, LTTextBoxHorizontal)):
                    text+=x.get_text()
                    print("-----------",x.get_text())
            # yield text


def clear_authors(author_line, key_set, split_char=","):
    """
    清洗作者
        传入一行包含多个作者及其脚标的字符串
        返回一个字典（key：作者名 value：脚标（list））

    主要针对英语，其他语言可能出问题
    :param author_line:
    :param key_set:
    :param split_char:
    :return:
    """
    author_line = author_line.replace(" and", split_char).replace(", MD","MD").replace("\u200b","")
    # and_num=author_line.find("and")
    # if and_num !=-1:
    #     author_line[and_num-1] in
    last_author = None
    author_dict = {}
    for au in author_line.split(split_char):
        au=au.strip()
        if au == "":
            continue

        if au in key_set or len(au)==1:
            # 拆出的是脚标
            if last_author == None:
                raise ValueError("解析出错！")
            else:
                if last_author in author_dict:
                    author_dict[last_author].append(au)
                else:
                    author_dict[last_author] = [au]
        else:
            # 拆出的非脚标（可能是脚标的混合、作者、作者脚标混合）
            author_name, sup_list = split_author_sup(au, key_set, [])
            if author_name == None:
                if last_author == None:
                    raise ValueError("解析出错！")
            else:
                last_author = author_name

            if last_author in author_dict:
                author_dict[last_author].extend(sup_list)
            else:
                author_dict[last_author] = sup_list
    return author_dict

def split_author_sup(text, key_set, sup_list,auto_split=True,check_last=True):
    '''
    抽取作者名字中的脚标


    :param text:
    :param key_set:
    :param sup_list:
    :param auto_split:
    :return:
    '''

    num = get_sup(text, key_set, 0)
    if num == 0:
        #在text最后没有脚标
        min=-1
        for key in key_set:
            if key in text:
                if auto_split:
                    # 在text存在脚标，但不在text最后，提取所有脚标，并舍弃脚标后的文字
                    key_num=text.find(key)
                    if min!=-1:
                        if key_num<min:
                            min=key_num
                    else:
                        min=key_num
                    sup_list.append(key)

                else:
                    raise ValueError("脚标位置有误或有未知的脚标！")
        if min!=-1:
            text=text[:min]

        if check_last:
            #检查text最后是否是*等非字母
            print("-------------",text)
            text=find_last(text)
            print(text)
            if text==None:
                raise ValueError("作者名为空！")

        return text, sup_list
    else:
        #找到脚标text[-num:]
        sup_list.append(text[-num:])
        if num == len(text):
            #整个text都是脚标
            return None, sup_list
        else:
            #继续判断text中是否还有脚标
            return split_author_sup(text[:-num], key_set, sup_list)

def find_last( text, index=-1):
    '''
    检查最后一位是否是字母
    :param text:
    :param index:
    :return:
    '''
    if index == len(text):
        return None
    if index == -1:
        index = 1
    # print(text,index)
    if text[-index].isalpha():
        if index==1:
            return text
        else:
            return text[:-(index-1)]
    else:
        return find_last(text, index + 1)

def get_sup(text, key_set, num):
    '''

    判断最后一位或多位的数是否在key_set中
    例如：
        key_set中有1,11   --两个脚标
        text为name111    --该name有两个脚标1和11但没有分割符

        get_sup方法返回数字2，表示text的后两位是一个脚标

    :param text:
    :param key_set:
    :param num:
    :return:
    '''

    if num==len(text):
        return num
    new_num = num + 1
    text=text.strip()


    if text[-new_num:] in key_set :
        return get_sup(text, key_set, new_num)
    else:
        return num

def download_html(self,url,*dir_name):
    logger.info("下载HTML,下载链接："+url)
    if dir_name:
        file_path = self.creat_filename(dir_name[0],"txt")
    else:
        date_time = time.strftime("%Y%m%d", time.localtime())
        file_path = self.creat_filename(date_time,"txt")
    try:
        self.download(url, file_path)
    except:
        logger.error("HTML下载出错。")
        try:
            os.remove(file_path)
        except:
            pass
        return None
    return file_path


def get_organization_location(list):
    orgs=[]
    locations=[]

    current=None
    current_label=None
    last_label=None
    for item in list:
        if item[1]=="ORGANIZATION":
            if current==None:
                current=item[0]
                current_label="ORGANIZATION"
            else:
                if last_label=="ORGANIZATION":
                    current+=" "+item[0]
                    current_label = "ORGANIZATION"
                else:
                    if current_label=="LOCATION":
                        locations.append(current)
                    current = item[0]
                    current_label = "ORGANIZATION"
            last_label="ORGANIZATION"
        elif item[1]=="LOCATION":
            # print(current)
            if current == None:
                current = item[0]
                current_label = "LOCATION"

            else:
                if last_label == "LOCATION":
                    current +=" "+ item[0]
                    current_label = "LOCATION"
                else:
                    if current_label == "ORGANIZATION":
                        orgs.append(current)
                    current = item[0]
                    current_label = "LOCATION"
            last_label = "LOCATION"
        else:
            if item[0]=="," or item[1]=="NUMBER":
                if current!=None:
                    current+=item[0]
            else:
                if current != None:
                    if current_label=="LOCATION":
                        locations.append(current)
                        current=None
                        current_label=None
                    elif current_label=="ORGANIZATION":
                        orgs.append(current)
                        current=None
                        current_label=None
                last_label=item[1]

    if current!=None:
        if current_label == "LOCATION":
            locations.append(current)
            current = None
            current_label = None
        elif current_label == "ORGANIZATION":
            orgs.append(current)
            current = None
            current_label = None

    return orgs,locations


def test():
    excel_name=r"C:\Users\zhaozhijie.CNPIEC\Desktop\打标记.xls"
    rb = xlrd.open_workbook(excel_name)
    r_sheet = rb.sheet_by_index(0)
    wb = copy.copy(rb)
    w_sheet = wb.get_sheet(0)
    list = r_sheet.row_values(0)

    aff_num = list.index("AFFILIATION")
    org_num = list.index("ORGANIZATION")
    loc_num = list.index("LOCATION")
    lab_num = list.index("label")

    for row in range(r_sheet.nrows - 1):
        aff=r_sheet.cell(row+1,aff_num).value
        print(aff)
        l=nlp.ner(aff)
        orgs,locs=get_organization_location(l)
        org=""
        for o in orgs:
            if o[-1]==",":
                o=o[:-1]
            org+=o+"##"

        loction=""
        for loc in locs:
            loction+=loc+"##"
        print(org,loction)
        w_sheet.write(row + 1, org_num, org[:-2])
        w_sheet.write(row + 1, loc_num, loction[:-2])
        w_sheet.write(row + 1, lab_num, str(l))



        # abs_url=r_sheet.cell(row+1,absurlnum).value
        # print("==============",tp.value)
        # if tp.value=="":
        #     page=r_sheet.cell(row+1,pages_num)
        #     print(page)
        #     if page.value!="":
        #         w_sheet.write(row+1,total_pages_num,page.value)
        # sn = r_sheet.cell(row + 1, sn_num)
        # print(sn)
        # if abs_url=="":
        #     sn=r_sheet.cell(row+1,sn_num)
        #     print(sn.value)
        #     if sn.value=="PMC":
        #         w_sheet.write(row + 1, absurlnum,"https://www.ncbi.nlm.nih.gov/pmc/articles/"+r_sheet.cell(row+1,pmc_num).value)
        #     else:
        #         w_sheet.write(row + 1, absurlnum, r_sheet.cell(row + 1,url_num).value)

    wb.save(excel_name)
    nlp.close()




if __name__ == '__main__':
    # test()
    print(pdfminer_read_all(r"Y:\小兔子\会议录一期一个PDF\desy1\httpwww-library.desy.depreparchdesyprocproc10-04P56.pdf"))
    # file_name=r"C:\pdfs\zx0723-c1\1476afdcb1a311e99e3800ac37466cf9.pdf"
    # auline=ocr_reader(file_name)
    # print(clear_authors(auline,[]))

    # ocr_reader(r"C:\pdfs\yj0903\8dd0cf18cdfa11e98e7100ac37466cf9.pdf")
    # line="Key Laboratory of Sugarcane Biotechnology and Genetic Improvement (Guangxi), Ministry of Agriculture, Guangxi Key Laboratory of Sugarcane Genetic Improvement, Sugarcane Research Center, Chinese Academy of Agricultural Sciences-Guangxi Academy of Agricultural Sciences"
    # line="Department of Obstetrics and Gynecology, F. Del Ponte Hospital, University of Insubria"
    # l=nlp.ner(line)
    # print(l)
    # print(get_organization_location(l))
    # nlp.close()

    # test()





