import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import base64
import os
import logging
import time
import redis
import threading

from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("root").setLevel(logging.ERROR)
logger=logging.getLogger("logger")

REDIS_IP="10.3.1.99"
REDIS_PORT="6379"
REDIS_DB="4"
QUEUE_NAME="file_queue"
FILE_SET="file_set"

redis_ = redis.Redis(host=REDIS_IP, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def bulk_insert():
    '''
    从redis中读数据导入到es
    :return:
    '''

    es = Elasticsearch([
        # {'host': '192.168.56.21',"port":9200},
        {'host': '192.168.56.22', "port": 9200},
        # {'host': '192.168.56.23',"port":9200},
    ],timeout=500)

    while(redis_.llen(QUEUE_NAME)>0):
        try:

            start_time=time.time()
            logger.info("开始读取数据...")
            # es.bulk(get_data(),index="pdf",pipeline="attachment")
            datas=get_data(num=500)
            read_data_time = time.time()
            logger.info("读取数据所用时间："+str(read_data_time-start_time))
            logger.info("开始上传...")
            helpers.bulk(es,datas)
            end_time=time.time()
            logger.info("当前批次上传所用时间：" + str(end_time - read_data_time))
        except:
            logger.info("上传出错！", exc_info=True)
            es = Elasticsearch([
                # {'host': '192.168.56.21', "port": 9200},
                {'host': '192.168.56.22', "port": 9200},
                # {'host': '192.168.56.23', "port": 9200},
            ],timeout=500)


def get_data(num=10):
    data=[]
    for i in range(num):
        if redis_.llen(QUEUE_NAME)>0:
            try:
                pdf_name=redis_.lpop(QUEUE_NAME)
                logger.info(str(i)+" PDF："+pdf_name)
                pdf_data = redis_.get(pdf_name)
                data.append({"_index":"pdf",
                             "_type":"test",
                             "_source":{"content": pdf_data, "path": pdf_name}
                             })
            except:
                logger.info("读取出错，跳过。")
                continue
        else:
            break
    return data

def update_queue(dir,update=False):
    '''
    更新redis队列
    :param dir:
    :param update:
    :return:
    '''
    if redis_.llen(QUEUE_NAME)>0:
        if update:
            update_data(dir)
    else:
        update_data(dir)

def update_data(dir):
    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        redis_.lpush(QUEUE_NAME, file)
        logger.info("读取PDF文本："+path)
        pdf_text=read_pdf(path)
        redis_.set(file,pdf_text)

def update(dir):
    update_queue(dir)
    bulk_insert()


def read_pdf(path):
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
                        text+=results+"\n"
        return text

def update_file(file_path):
    es = Elasticsearch([
        # {'host': '192.168.56.21',"port":9200},
        {'host': '192.168.56.22', "port": 9200},
        # {'host': '192.168.56.23',"port":9200},
    ], timeout=500)
    data=[]
    for line in open(file_path).readlines():
        args=line.replace("\n","").split("$$$$")
        if args.__len__()!=6:
            print("字段数有误！")
        else:
            data.append({"_index": "pdf",
                         "_type": "test",
                         "_source": {"title": args[0], "author": args[1],"abstract":args[2],"date":args[3],"page_count":args[4],"ad":args[5]+".pdf"}
                         })

    helpers.bulk(es, data)

class Pdf_To_Text_Thread(threading.Thread):
    def __init__(self,pdf_dir,text_dir):
        threading.Thread.__init__(self)
        self.pdf_dir=pdf_dir
        self.text_dir=text_dir
    def run(self):
        while redis_.llen(QUEUE_NAME)>0:
            file=redis_.lpop(QUEUE_NAME)
            pdf_path=os.path.join(self.pdf_dir,file)
            try:
                logger.info(self.name+"转换文件："+file)
                text=read_pdf(pdf_path)
                with open(os.path.join(self.text_dir,file.replace(".pdf",".txt")),"w+",encoding="utf-8") as f:
                    f.write(text)
            except:
                logger.error("转换失败："+file,exc_info=True)



def pdf_to_text(pdf_dir,text_dir,thread_num=10):
    for file in os.listdir(pdf_dir):
        if redis_.sadd(FILE_SET,file)==1:
            logger.info("新文件："+file)
            redis_.lpush(QUEUE_NAME,file)

    for i in range(thread_num):
        Pdf_To_Text_Thread(pdf_dir,text_dir).start()




if __name__ == '__main__':
    # update_file(r"C:\Users\zhaozhijie.CNPIEC\Documents\Tencent Files\2046391563\FileRecv\muci(1).txt")
    # update(r"C:\pdfs\jx0621")
    # pdf_to_text(r"C:\pdfs\jx0621",r"C:\pdfs\test")
    read_pdf(r"G:\hrl\adams1\adams\1950-2010\ML19196A077.pdf")



