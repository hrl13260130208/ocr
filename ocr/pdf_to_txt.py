
import pytesseract
from pdf2image import convert_from_path
from pdfminer.pdfparser import  PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import logging
import os

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("root").setLevel(logging.ERROR)
logger=logging.getLogger("logger")



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

def run(pdf_dir=r"C:\pdfs\jx0927",txt_dir="C:\pdfs\jx0927_txt",ocr=False):
    if not os.path.exists(pdf_dir):
        raise ValueError("pdf目录有误...")
    if not os.path.exists(txt_dir):
        os.mkdir(txt_dir)
    print("-----------")
    for i in os.listdir(pdf_dir):
        logger.info("开始处理文件："+str(i))
        try:
            txt_name=i.replace(".pdf",".txt")
            if not ocr:
                text=read_pdf(os.path.join(pdf_dir,i))
            else:
                text=ocr_read(os.path.join(pdf_dir,i))
            with open(os.path.join(txt_dir,txt_name),"w+",encoding="utf-8") as f:
                f.write(text)
        except:
            logger.error("处理出错！",exc_info=True)

def ocr_read(path,temp_dir="C:/temp/png"):
    text=None
    images = convert_from_path(path)
    for index, img in enumerate(images):
        if index>1:
            break
        image_path = '%s/page_%s.png' % (temp_dir, index)
        logger.info("临时图片路径：" + image_path)
        img.save(image_path)
        if text==None:
            text=pytesseract.image_to_string(image_path)
        else:
            text+= pytesseract.image_to_string(image_path)

    return text


if __name__ == '__main__':
    run(pdf_dir=r"Y:\小杰\jx\jx20191209001\Files\给小何的",
        txt_dir=r"Y:\小杰\jx\jx20191209001\Files\给小何的_txt",
        ocr=True)
    # run(pdf_dir=r"Y:\数据配送专用(勿动）\中信所\会议录\zxhy20191129001\抽取关键词\转过的61",
    #     txt_dir=r"Y:\数据配送专用(勿动）\中信所\会议录\zxhy20191129001\抽取关键词\转过的61_txt",
    #     ocr=True)