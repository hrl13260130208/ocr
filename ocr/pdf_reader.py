import re
import xlrd
# import xlwt
from  xlutils import copy
import os
import logging
import threading
from pdf2image import convert_from_path
import string
import pytesseract

from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import sys
from stanfordcorenlp import StanfordCoreNLP
from configparser import ConfigParser

from PyQt5 import QtCore,QtGui

from PyQt5.QtCore import  QEventLoop, QTimer,pyqtSignal

from PyQt5.QtWidgets import QMainWindow, QPushButton, \
    QApplication,QComboBox,QLabel,QLineEdit,QFileDialog,QPlainTextEdit,QWidget



NLP_DIR="stanford-corenlp-full-2016-10-31"
PATH="path"
ABSTRACT="abstract"
AUTHOR_NAME="author_name"
AFFILIATION="affiliation"
CLEAR_DEF={", MASc":"",", Eng.":"",", PhD":"",", Professor":" ",", PE":" ",", Ph.D.":"",", ing.":""}
AFFILIATION_SUP_CLEAR_DICT={".":"",",":""}


def config_to_dict(path,dict):
    # text="配置格式：key=value（将作者名中的key替换成value，value为空的时候使用null）"
    au_conf=Conf_Parser()
    au_conf.read(path,encoding="utf-8")
    for i in au_conf.items('items'):
        if i[1]=="null":
            dict[i[0]]=""
        else:
            dict[i[0]]=i[1]
    # print(CLEAR_DEF)
    # print(AFFILIATION_SUP_CLEAR_DICT)

class Conf_Parser(ConfigParser):
    '''
    python自带模块读取conf中的cnpiec_1_A为cnpiec_1_a，该类读取为cnpiec_1_A
    '''
    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr

class excels():

    '''
    待改进：ocr_read方法的复用，PDF_read与ocr_read的替换
    '''

    def __init__(self,file_path,find_abstract=False,find_author=False,
                 find_affilition=False,logger=None,
                 nlp_path=r'C:\File\stanford-corenlp-full-2016-10-31'):
        self.outputDir = os.path.join(os.path.abspath("."),"png")
        if not self.outputDir:
            os.mkdir(self.outputDir)
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)

        if logger==None:
            pass
        else:
            self.logger=logger

        self.nlp = StanfordCoreNLP(nlp_path)

        if file_path!=None:
            self.file_path = file_path
            self.values = [PATH]
            self.find_abstract=find_abstract
            self.find_affiliation=find_affilition
            self.find_author=find_author
            if self.find_abstract:
                self.values.append(ABSTRACT)
            if self.find_author:
                self.values.append(AUTHOR_NAME)
            if self.find_affiliation:
                self.values.append(AFFILIATION)
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
            # print(value)
            print(self.list)
            index = self.list.index(value)
            self.nums[value]=index
        # self.nums["path"]=


    def create_data(self,txt_dir=r"C:\data\text"):
        for row in range(self.r_sheet.nrows - 1):

            row_num = row + 1

            self.logger.info("处理第" + str(row_num) + "行...")
            path = self.r_sheet.cell(row_num, self.nums["path"]).value
            self.logger.info("文件路径：" + str(path))
            if not os.path.exists(path):
                self.logger.warning("路径不存在！")
                continue

            lines = self.au_pdf_read(path)

            if len(lines) < 10:
                lines = self.au_ocr_read(path)

            txt_path = os.path.join(txt_dir, str(row_num) + ".txt")
            with open(txt_path,"w+",encoding="utf-8") as f:
                f.write(str(path))
                for i,line in enumerate(lines):
                    f.write("0\t"+str(i)+"\t"+str(line)+"\n")

    def read(self):
        '''
        抽取作者或摘要

        :return:
        '''
        self.logger.info("开始抽取文件...")
        for row in range(self.r_sheet.nrows-1):

            row_num=row+1
            if row_num%1000==0:
                self.save()
            self.logger.info("处理第"+str(row_num)+"行...")
            path=self.r_sheet.cell(row_num,self.nums[PATH]).value
            self.logger.info("文件路径："+str(path))
            if not os.path.exists(path):
                self.logger.warning("路径不存在！")
                continue
            try:
                if self.find_abstract:
                    self.find_abs(row_num,path)
                if self.find_author:
                    self.find_author_and_affiliation(path,row_num)
                else:
                    if self.find_affiliation:
                        raise ValueError("作者机构需要一起抽取，机构不能单独抽取！")
            except:
                self.logger.error("处理出错！",exc_info=True)

        self.logger.info("文件抽取完成。保存中...")
        self.save()
        self.nlp.close()
        self.logger.info("保存完成。")

    def find_author_and_affiliation(self,path,row_num):
        aus = self.r_sheet.cell(row_num, self.nums[AUTHOR_NAME]).value
        if aus != "":
            return
        try:
            au,aff=self.read_au_and_aff(path)

            if self.find_affiliation:
                if "$$" not  in aff:
                    self.write(au, row_num, AUTHOR_NAME)
                    self.write(aff,row_num,AFFILIATION)
            else:
                self.write(au, row_num, AUTHOR_NAME)
        except:
            pass

    def read_au_and_aff(self,path,debug=False):
        self.logger.info("开始抽取作者...")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        lines=self.au_pdf_read(path)
        # print(len(lines),lines)
        # lines=self.au_ocr_read(path)
        if len(lines)<10:
            lines=self.au_ocr_read(path)
        au,aff=self.analyze_lines(lines)
        aus=self.clear_authors(au,{})

        author_name=""
        affilition=""
        # print(aff)
        for au_key in aus.keys():
            author_name+=au_key+"##"
            temp_aff=""
            for sup in set(aus[au_key]):
                if sup in aff.keys():
                    temp_aff+=aff[sup]+";"
            if temp_aff=="":
                if "0" in aff:
                    affilition+=aff["0"]+"##"
                else:
                    affilition+="$$##"
            else:
                affilition+=temp_aff[:-1]+"##"
        return author_name[:-2],affilition[:-2]

    def analyze_lines(self,lines,aff_skip_num=2):

        find=False
        author_line=""
        aff={}
        author_line_num = -1
        f_num = -1
        aff_num=-1
        last_aff_sup=None
        for index,line in enumerate(lines):
            # print("++++++++++++++",index,line)
            if self.author_analyze(line):
                find=True
                self.logger.debug("找到作者。")
                self.logger.debug("编号：" + str(index))
                self.logger.debug("文本：" + line)

                if author_line_num==-1:
                    author_line_num=index
                    f_num=index
                    author_line += line + ","
                else:
                    if f_num+1==index:
                        f_num=index
                        author_line += line + ","

            if find:
                if self.affilition_analyze(line):
                    self.logger.debug("找到机构。")
                    self.logger.debug("编号：" + str(index))
                    self.logger.debug("文本：" + line)
                    if aff_num==-1:
                        aff_num=f_num

                    if aff_num + aff_skip_num >= index:
                        # print(line)
                        aff_num=index
                        sup,value=self.find_first(line)

                        # print("-------------",sup,value)
                        if sup==None:
                            if last_aff_sup==None:
                                if "0" in aff.keys():
                                    aff["0"] += value
                                else:
                                    aff["0"] = value
                            else:
                                aff[last_aff_sup] += value

                        else:
                            for key in AFFILIATION_SUP_CLEAR_DICT.keys():
                                sup=sup.replace(key,AFFILIATION_SUP_CLEAR_DICT[key])
                            sup = sup.strip()
                            aff[sup]=value
                            last_aff_sup=sup

        # print(author_line,aff)
        if author_line_num>len(lines)/2:
            author_line=""
            aff={}
        return author_line,aff


    def au_pdf_read(self,path):
        self.logger.info("使用pdfminer抽取...")
        lines=[]
        fp = open(path, 'rb')
        parser = PDFParser(fp)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)

        doc.initialize()

        if not doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            for page in doc.get_pages():
                interpreter.process_page(page)
                layout = device.get_result()
                for x in layout:
                    if (isinstance(x, LTTextBoxHorizontal)):
                        text=x.get_text()
                        # print("-------------",text)
                        for l in text.split("\n"):
                            lines.append(l)
                break
        return lines
            #                 line_num += 1
            #                 if self.author_analyze(l):
            #                     self.logger.debug("找到作者。")
            #                     self.logger.debug("编号：" + str(line_num))
            #
            #                     if author_line_num == -1:
            #                         author_line_num = line_num
            #                         f_num = line_num
            #                         author_line += l + ","
            #                     else:
            #                         if f_num + 1 == line_num:
            #                             f_num = line_num
            #                             author_line += l + ","
            #     break
            # if author_line_num > line_num / 2:
            #     author_line = ""
            # self.logger.debug("所有找到作者：" + author_line[:-1])
            # return author_line[:-1]
    def au_ocr_read(self,path):
        self.logger.info("使用ocr抽取...")
        lines = []
        images = convert_from_path(path)
        for index, img in enumerate(images):
            if index > 10:
                break
            image_path = '%s/page_%s.png' % (self.outputDir, index)

            img.save(image_path)
            text = pytesseract.image_to_string(image_path)

            for line in self.get_sections(text):
                for l in line.split("\n"):
                    lines.append(l)
            break
        return lines
        #             line_num+=1
        #             if self.author_analyze(l):
        #                 self.logger.debug("找到作者。")
        #                 self.logger.debug("编号：" + str(line_num))
        #
        #                 if author_line_num==-1:
        #                     author_line_num=line_num
        #                     f_num=line_num
        #                     author_line += l + ","
        #                 else:
        #                     if f_num+1==line_num:
        #                         f_num=line_num
        #                         author_line += l + ","
        #
        #     if author_line_num>line_num/2:
        #         author_line=""
        #     break
        # self.logger.debug("所有找到作者："+author_line[:-1])
        # return author_line[:-1]

    def author_analyze(self,text):
        """
        判断传入的是否是作者
        :param text: PDF中的一行字符
        :return:
        """

        find = False

        r = self.nlp.ner(text)
        author_len = 0

        for item in r:
            if item[1] == "PERSON":
                find = True
                author_len += len(item[0])

        if find:
            if "@" in text:
                return False
            else:

                num=0
                for word in text.split(" "):
                    num+=len(word.strip())
                self.logger.debug("找到人名...")

                self.logger.debug("原文：" + str(text))
                self.logger.debug("拆分：" + str(r))
                if num==0:
                    raise ValueError("字符长度有误！")
                try:
                    aus=self.clear_authors(text,{})
                    clear_au_num=0
                    for key in aus.keys():
                        if len(key) >len(text)/10*8 and len(key)>30:
                            clear_au_num=0
                            break
                        for ar in self.nlp.ner(key):
                            if ar[1]=="PERSON":
                                clear_au_num+=len(key)
                                break
                except:
                    clear_au_num=0

                return author_len / num >= 0.5 or clear_au_num / num >= 0.5
        else:
            return False

    def affilition_analyze(self,text):

        r = self.nlp.ner(text)

        for item in r:
            if item[1] == "ORGANIZATION" or item[1]=="LOCATION":
                return True



    def clear_authors(self,author_line, key_set, split_char=",",clear_dict=None):
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
        author_line = author_line.replace(" and", split_char).replace("\u200b","").replace("&",split_char)

        if clear_dict!=None:
            for key in clear_dict.keys():
                author_line=author_line.replace(key,clear_dict[key])

        self.logger.debug("清洗后作者："+str(author_line))
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
                # print("-----------",au)
                author_name, sup_list = self.split_author_sup(au, key_set, [])
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

    def split_author_sup(self, text, key_set, sup_list, auto_split=True, check_last=True):
        '''
        抽取作者名字中的脚标


        :param text:
        :param key_set:
        :param sup_list:
        :param auto_split:
        :return:
        '''

        num = self.get_sup(text, key_set, 0)
        # print(num)
        if num == 0:
            # 在text最后没有在set中的脚标
            min = -1
            for key in key_set:
                if key in text:
                    if auto_split:
                        # 在text存在脚标，但不在text最后，提取所有脚标，并舍弃脚标后的文字
                        key_num = text.find(key)
                        if min != -1:
                            if key_num < min:
                                min = key_num
                        else:
                            min = key_num
                        sup_list.append(key)

                    else:
                        raise ValueError("脚标位置有误或有未知的脚标！")
            if min != -1:
                text = text[:min]

            if check_last:
                # 检查text最后是否是*等非字母
                # print("-------------",text)
                text,sup = self.find_last(text)
                if sup!=None:
                    for s in list(sup):
                        sup_list.append(s)
                if text == None:
                    raise ValueError("作者名为空！")
            # print(text,sup_list)
            return text, sup_list
        else:
            # 找到脚标text[-num:]
            # print("----------",text,text[-num:])
            sup_list.append(text[-num:])
            if num == len(text):
                # 整个text都是脚标
                return None, sup_list
            else:
                # 继续判断text中是否还有脚标
                return self.split_author_sup(text[:-num], key_set, sup_list)

    def find_first(self,text,index=0):
        """
        判断第一个字符是否是字母
        :param text:
        :param index:
        :return:
        """
        if index == len(text):
            return None,text
        if text[index].isalpha():
            if index==0:
                return None,text
            else:
                return text[:index],text[index:]
        else:
            return self.find_first(text,index=index+1)

    def find_last(self, text, index=-1):
        '''
        检查最后一位是否是字母
        :param text:
        :param index:
        :return:
        '''
        if index == len(text):
            return None,text
        if index == -1:
            index = 1
        # print(text,index)
        if text[-index].isalpha():
            if index == 1:
                return text,None
            else:
                return text[:-(index - 1)],text[-(index - 1):]
        else:
            return self.find_last(text, index + 1)

    def get_sup(self, text, key_set, num):
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

        if num == len(text):
            return num
        new_num = num + 1
        text = text.strip()

        if text[-new_num:] in key_set:
            return self.get_sup(text, key_set, new_num)
        else:
            return num


    def find_abs(self,row_num,path):
        abs = self.r_sheet.cell(row_num, self.nums[ABSTRACT]).value
        if abs != "":
            return
        try:
            text=self.read_abs(path)
            if text!=None:
                text = text.replace("\n", " ")
                self.write(text, row_num,ABSTRACT)
        except:
            self.logger.error("err", exc_info=True)

    def read_abs(self,path):
        text = self.ocr_read(path)
        return text


    def ocr_read(self,filename):

        images = convert_from_path(filename)
        for index, img in enumerate(images):
            if index > 10:
                break
            image_path = '%s/page_%s.png' % (self.outputDir, index)
            self.logger.info("临时图片路径：" + image_path)
            img.save(image_path)
            text = self.get_abs(pytesseract.image_to_string(image_path))
            if text != None:
                return text

    def get_abs(self,text):
        abs_num = text.lower().find("abstract")
        if abs_num > text.__len__() * 9 / 10:
            abs_num = -1
        if abs_num != -1:
            keywords_num = text.lower().find("keywords")
            if keywords_num != -1:
                #有keywords，取abs与keywords之间的字符
                if keywords_num > abs_num + 8:
                    return self.abs_clear(text[abs_num:keywords_num])
            else:
                #没有keywords
                # print(text)
                abs = ""
                for section in self.get_sections(text[abs_num + 8:]):
                    if section=="":
                        continue
                    if section.__len__() > 300:
                        if self.is_abs(section):
                            abs += section
                            break
                    else:
                        if self.is_abs(section):
                            abs += section + "\n"
                            if abs.__len__() > 300:
                                break
                return self.abs_clear(abs)
        else:
            for section in self.get_sections(text):
                if section.__len__() > 300:
                    if self.is_abs(section):
                        num = section.rfind(".")
                        if num > 300:
                            return self.abs_clear(section[:num + 1])

    def get_sections(self,text):
        return text.split("\n\n")

    def is_abs(self,abs):
        d = u = l = o = 0

        if "@" in abs:
            self.logger.debug("有@符号！")
            self.logger.debug("摘要：", abs)
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
        self.logger.debug("数字字符：" + str(d) + " 大写字母字符：" + str(u) + " 标点字符：" + str(o) + "字符总数：" + str(abs.__len__()))
        if d / abs.__len__() > 0.01:
            self.logger.debug("数字比例过高：" + str(d) + "  " + str(d / abs.__len__()))
            self.logger.debug("摘要：" + str(abs))
            return False

        if u / abs.__len__() > 0.05:
            self.logger.debug("大写字母比例过高：" + str(u) + "  " + str(u / abs.__len__()))
            self.logger.debug("摘要：" + str(abs))
            return False
        if o / abs.__len__() > 0.1:
            self.logger.debug("标点特殊字符比例过高：" + str(o) + "  " + str(o / abs.__len__()))
            self.logger.debug("摘要：" + str(abs))
            return False

        return True

    def abs_clear(self,abs):
        abs = self.abs_head_clear(abs.strip())
        if abs == None:
            return None
        self.logger.debug("last char:" + abs[-1])
        if abs[-1] != "." and abs[-1] != "。":
            abs = abs + "."
        return abs

    def abs_head_clear(self,abs):
        if ":" in abs:
            num = abs.find(":")
            if num < 30:
                abs = abs[num + 1:].strip()

        sumnary = re.match("SUMMARY", abs.upper())
        if sumnary != None:
            abs = abs[sumnary.end():].strip()
        abstract = re.match("ABSTRACT", abs.upper())
        if abstract != None:
            abs = abs[abstract.end():].strip()
        abs = self.find_upper(abs)
        if abs.__len__() < 150:
            self.logger.debug("摘要过短！")
            abs = None
        return abs

    def find_upper(self,abs):
        if abs.__len__() < 150:
            return abs
        if abs[0].isupper():
            return abs
        else:
            return self.find_upper(abs[1:])

    def write(self,text,row_num,item_name):
        self.w_sheet.write(row_num,self.nums[item_name],text)


    def save(self):
        self.wb.save(self.file_path)


class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))
        loop = QEventLoop()
        QTimer.singleShot(10, loop.quit)
        loop.exec_()


class Example(QMainWindow):

    def __init__(self,author_config="author_config.cfg",aff_config="aff_config.cfg"):
        super().__init__()
        self.initUI()
        self.author=None
        self.abs=None
        self.aff=None
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            stream=sys.stdout)
        logging.root.setLevel(logging.ERROR)
        logging.getLogger("pdfminer").setLevel(logging.ERROR)
        logging.getLogger("Ilogger").setLevel(logging.INFO)
        self.logger = logging.getLogger("Ilogger")
        self.author_config=author_config
        self.aff_config=aff_config

        au_path = os.path.join(os.path.abspath("."), self.author_config)
        self.au_show=showconfig(au_path, config=CLEAR_DEF)
        aff_path = os.path.join(os.path.abspath("."), self.aff_config)
        self.aff_show=showconfig(aff_path, config=AFFILIATION_SUP_CLEAR_DICT)



    def initUI(self):
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        lbl = QLabel("抽取项目：", self)
        lbl.move(50,50)
        lb2 = QLabel("作者：", self)
        lb2.move(50, 100)


        author=QComboBox(self)
        author.addItems(["True","False"])
        author.setCurrentIndex(1)
        author.move(100,100)


        author.activated[str].connect(self.author_change)
        lb3 = QLabel("摘要：", self)
        lb3.move(50, 150)

        abs = QComboBox(self)
        abs.addItems(["True", "False"])
        abs.setCurrentIndex(1)
        abs.move(100, 150)


        lb4 = QLabel("机构：", self)
        lb4.move(250, 100)

        affs = QComboBox(self)
        affs.addItems(["True", "False"])
        affs.setCurrentIndex(1)
        affs.move(300, 100)

        author.activated[str].connect(self.author_change)
        abs.activated[str].connect(self.abs_change)
        affs.activated[str].connect(self.aff_change)

        lb5 = QLabel("EXCEL路径：", self)
        lb5.move(50, 200)

        self.le = ClickLine(self)
        self.le.resize(200,30)
        self.le.move(150,200)

        btn3 = QPushButton("作者清洗配置", self)
        btn3.move(50, 250)
        btn3.clicked.connect(self.author_clear_show)

        btn4 = QPushButton("机构清洗配置", self)
        btn4.move(200, 250)
        btn4.clicked.connect(self.aff_clear_show)

        btn5 = QPushButton("测试", self)
        btn5.move(250, 250)
        btn5.clicked.connect(self.clear_test)

        btn2 = QPushButton("启动", self)
        btn2.move(50, 300)

        btn2.clicked.connect(self.buttonClicked)

        self.textBrowser=QPlainTextEdit(self)
        self.textBrowser.move(50,350)
        self.textBrowser.resize(400,200)

        self.setGeometry(300, 300, 500, 600)
        self.setWindowTitle('PDF抽取工具')
        self.show()

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def buttonClicked(self):
        # print("-----------",os.path.abspath("."))

        find_author=self.author==str(True)
        find_abs=self.abs==str(True)
        find_affs=self.aff==str(True)

        path=self.le.text()
        if not os.path.exists(path):
            self.logger.error("EXCEL路径不正确！")
            return
        # print(find_author,find_abs,(find_author or find_abs))
        if not (find_author or find_abs):
            self.logger.error("作者摘要都不为True！")
            return

        et=excel_thread(path,find_author,find_abs,find_affs,logger=self.logger,use_absnlppath=True)
        et.setDaemon(True)
        et.start()

    def clear_test(self):
        pass


    def author_clear_show(self):
        self.au_show.show()

    def aff_clear_show(self):
        self.aff_show.show()

    def author_change(self, text):
        self.author=text
    def abs_change(self,text):
        self.abs=text

    def aff_change(self,text):
        self.aff=text


class showconfig(QWidget):
    '''自定义窗口'''


    before_close_signal = pyqtSignal(int)  # 自定义信号（int类型）

    def __init__(self,file_path="",config=CLEAR_DEF):
        super().__init__()

        self.setWindowTitle('配置窗口')
        self.resize(400, 500)
        self.file_path=file_path
        self.config=config

        f= open(file_path,encoding="utf-8")
        text=f.read()
        self.t=QPlainTextEdit(self)
        self.t.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.t.resize(400,400)
        self.t.setPlainText(text)

        btn1 = QPushButton("更新",self)
        btn1.move(100,400)
        btn1.clicked.connect(self.up_config)

        btn2 = QPushButton("关闭",self)
        btn2.move(250,400)
        btn2.clicked.connect(self.closeitem)


    def up_config(self):
        text=self.t.toPlainText()
        with open(self.file_path,"w+",encoding="utf-8") as f:
            f.write(text)
        config_to_dict(self.file_path,self.config)
        self.close()


    # 默认关闭事件
    def closeitem(self):
        self.close()


class ClickLine(QLineEdit):

    def mousePressEvent(self, QMouseEvent):
        fileName = QFileDialog.getOpenFileName(
            self, 'Open Image', './__data', '*.xls')
        self.setText(fileName[0])

class excel_thread(threading.Thread):
    def __init__(self, path, find_author,find_abs,find_aff,logger,use_absnlppath=False ):
        threading.Thread.__init__(self)
        self.use_absnlppath=use_absnlppath
        self.path=path
        self.find_author=find_author
        self.find_abs=find_abs
        self.find_aff=find_aff
        self.logger=logger

    def run(self):
        if self.use_absnlppath:
            excels(self.path,
                   find_author=self.find_author,
                   find_abstract=self.find_abs,
                   find_affilition=self.find_aff,
                   logger=self.logger,
                   nlp_path=os.path.join(os.path.abspath("."),NLP_DIR)
                   ).read()
        else:
            excels(self.path, find_author=self.find_author, find_abstract=self.find_abs,logger=self.logger).read()




if __name__ == '__main__':


    # # print("Liangzhu (Leon) Wang".__len__())
    # # print(excels(None).read_abs(r"Y:\小兔子\会议录一期一个PDF\desy1\httpwww-library.desy.depreparchdesyprocproc08-03A.pdf"))
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #                     stream=sys.stdout)
    # logging.root.setLevel(logging.ERROR)
    # logging.getLogger("pdfminer").setLevel(logging.ERROR)
    # logging.getLogger("Ilogger").setLevel(logging.INFO)
    # logger = logging.getLogger("Ilogger")
    # excel_path=r"C:\public\目次采全文\0108\中信所缺失摘要清单_20200108..xls"
    # # # excel_path=r"Y:\小兔子\中信所2019年任务\补摘要\INTERNATIONAL COMMITTEE ON COMPOSITE MATERIALS 抽\oa_gs_zx_20191111_1_20191111会议录.xls"
    # excels(excel_path,
    #       find_abstract=True,find_affilition=False, find_author=False,
    #        logger=logger).read()
    # excels().create_data()
    # pdf = r"C:\pdfs\jx1108\9f2419ee020d11eab44e00ac37466cf9.pdf"
    # print(excels(r"C:\Users\zhaozhijie.CNPIEC\Documents\Tencent Files\2046391563\FileRecv\hehehe.xls",logger=logger).has_aff())
    # print(excels(None,logger=logger).read_au_and_aff(r"Y:\数据配送专用(勿动）\中信所\OA\zx20190929001四次返工\zx20190929001R\Files\RO201909273414694ZX.pdf",debug=True))
    # print(excels(None,logger=logger).clear_authors("Soo Cheon Chae1, Sun-Ok Chung2,*, and Sang Un Park3,*",{}))
    # print(list("sfdfs"))
    #exe用
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    # dict_to_txt(CLEAR_DEF)
