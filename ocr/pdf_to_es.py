import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import base64
import os
import logging
import time
import redis

from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.getLogger("elasticsearch").setLevel(logging.ERROR)
# logging.getLogger("pdfminer").setLevel(logging.ERROR)
# logging.getLogger("root").setLevel(logging.ERROR)
logger=logging.getLogger("logger")


REDIS_IP="10.3.1.99"
REDIS_PORT="6379"
REDIS_DB="4"
QUEUE_NAME="file_queue"

redis_ = redis.Redis(host=REDIS_IP, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def upload_pdf(pdf_path):
    es = Elasticsearch([
        {'host': '192.168.56.21', "port": 9200},
        {'host': '192.168.56.22', "port": 9200},
        {'host': '192.168.56.23', "port": 9200},
    ])
    with open(pdf_path,"rb") as f:
        pdf_data=base64.b64encode(f.read())

        es.index(index="pdf", pipeline="attachment",
                 body={"data": pdf_data,"path":pdf_path})


def upload_dir(dir):
    es = Elasticsearch([
    # {'host': '192.168.56.21',"port":9200},
    {'host': '192.168.56.22',"port":9200},
    # {'host': '192.168.56.23',"port":9200},
],timeout=60)
    for file in os.listdir(dir):
        start_time=time.time()
        logger.info("处理文件："+file+"...")
        path=os.path.join(dir,file)
        with open(path, "rb") as f:
            pdf_data = base64.b64encode(f.read())
            open_file_time=time.time()
            logger.info("读取文件所用时间："+str(open_file_time-start_time))

            try:
                es.index(index="pdf", pipeline="attachment",
                         body={"data": pdf_data, "file_name": file})
                es_time=time.time()
                logger.info("es存储时间："+str(es_time-open_file_time))
            except:
                logger.info("上传出错！",exc_info=True)
                es = Elasticsearch([
                    # {'host': '192.168.56.21', "port": 9200},
                    {'host': '192.168.56.22', "port": 9200},
                    # {'host': '192.168.56.23', "port": 9200},
                ],timeout=60)


def test():
    es = Elasticsearch([
        # {'host': '192.168.56.21', "port": 9200},
        {'host': '192.168.56.22', "port": 9200},
        # {'host': '192.168.56.23', "port": 9200},
    ])
    start_time = time.time()
    path = r"C:\Users\zhaozhijie.CNPIEC\Desktop\新建文本文档.txt"
    with open(path, "rb") as f:
        pdf_data = f.read()
        open_file_time = time.time()
        logger.info("读取文件所用时间：" + str(open_file_time - start_time))

        try:
            es.index(index="pdf",
                     body={"data": pdf_data, "file_name": "122222222222222"})
            es_time = time.time()
            logger.info("es存储时间：" + str(es_time - open_file_time))
        except:
            logger.info("上传出错！", exc_info=True)
            es = Elasticsearch([
                # {'host': '192.168.56.21', "port": 9200},
                {'host': '192.168.56.22', "port": 9200},
                # {'host': '192.168.56.23', "port": 9200},
            ], timeout=60)


def bulk_test(dir):
    es = Elasticsearch([
        # {'host': '192.168.56.21',"port":9200},
        {'host': '192.168.56.22', "port": 9200},
        # {'host': '192.168.56.23',"port":9200},
    ], timeout=500)
    # data=[]
    # for file in os.listdir(dir):
    #     pdf_path = os.path.join(dir, file)
    #     with open(pdf_path, "rb") as f:
    #         pdf_data = base64.b64encode(f.read())
    #         data.append({"_index": "pdf_b",
    #                      "_type": "test",
    #                      "_source": { "path": pdf_path}
    #                      })
    # helpers.bulk(es, data)
    data=[]
    for i in range(5000):
        data.append({"_index": "pdf_b",
                     "_type": "test",
                     "_source": { "path":"fg fgg dfgdfg her"+str(i)}
                     })
    helpers.bulk(es, data)



def insert():
    es = Elasticsearch([
        # {'host': '192.168.56.21',"port":9200},
        # {'host': '192.168.56.22', "port": 9200},
        {'host': '192.168.56.23',"port":9200}
    ], timeout=500)

    while (redis_.llen(QUEUE_NAME) > 0):
        try:

            start_time = time.time()
            # es.bulk(get_data(),index="pdf",pipeline="attachment")

            if redis_.llen(QUEUE_NAME) > 0:
                pdf_path = redis_.lindex(QUEUE_NAME,0)
                logger.info("上传文件："+pdf_path)
                with open(pdf_path, "rb") as f:
                    # pdf_data = base64.b64encode(f.read())
                    text=read_pdf(pdf_path)
                    # es.index(index="pdf", pipeline="attachment",
                    #          body={"data": pdf_data, "file_name": pdf_path})
                    if text!="":
                        es.index(index="pdf",doc_type="test",
                                 body={"content":text,"file_name": pdf_path})
            logger.info("上传所用时间：" + str( time.time() - start_time))

        except:
            logger.info("上传出错！", exc_info=True)
            redis_.rpush(QUEUE_NAME,pdf_path)
            es = Elasticsearch([
                # {'host': '192.168.56.21', "port": 9200},
                # {'host': '192.168.56.22', "port": 9200},
                {'host': '192.168.56.23', "port": 9200}
            ], timeout=500)
        finally:
            redis_.lpop(QUEUE_NAME)


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
                pdf_path=redis_.lpop(QUEUE_NAME)
                logger.info(str(i)+" PDF："+pdf_path)
                pdf_data = read_pdf(pdf_path)
                data.append({"_index":"pdf",
                             "_type":"test",
                             "_source":{"content": pdf_data, "path": pdf_path}
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
        redis_.lpush(QUEUE_NAME, path)

def update(dir):
    update_queue(dir)
    bulk_insert()
    # insert()

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
                        # print(results)
                        text+=results+"\n"
        return text


if __name__ == '__main__':
    # upload_pdf(r"C:\pdfs\hs0610-c2\0d8101a68e7111e9a35f00ac37466cf9.pdf")
    # upload_dir(r"C:\pdfs\hg0621-c1")
    # update(r"C:\pdfs\osti_0801")
    # bulk_test(r"C:\pdfs\jx0621")
    # read_pdf(r"C:\pdfs\hs0610-c2\0d8101a68e7111e9a35f00ac37466cf9.pdf")
    # test()
    # print(redis_.llen(QUEUE_NAME))
    # redis_.delete(QUEUE_NAME)
    # get_data()
    print(read_pdf(r"C:\pdfs\hs0610-c2\0d8101a68e7111e9a35f00ac37466cf9.pdf"))



