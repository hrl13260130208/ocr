
import img2pdf
from pdf2image import convert_from_path
import PyPDF2
import os
from ocr.redis_queue import Redis_Queue


def main(path,new_path):

    images_dir="D:/temp/"
    pdf_file = open(path, "rb")
    pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
    num=pdf.getNumPages()
    new_pages=-1
    if num<10:
        new_pages=1
    elif num>100:
        new_pages=10
    elif num>500:
        return None
    else:
        new_pages=int(num/10)
    pdf_file.close()
    image_paths=[]
    # with convert_from_path(path) as images:
    images=convert_from_path(path)
    # print(images,type(images))
    for index,image in enumerate(images):
        if index>=new_pages:
            break
        else:
            image_path=images_dir+str(index)+".jpg"
            image.save(image_path)
            image_paths.append(image_path)

    a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
    layout_fun = img2pdf.get_layout_fun(a4inpt)
    with open(new_path,'wb') as f:
        f.write(img2pdf.convert(image_paths,layout_fun=layout_fun))



def run_dir():
    '''
    生成新的pdf文件（限定页数、图片）
    :return:
    '''
    dir=r"E:\电子书\pdfs"
    new_dir=r"E:\电子书\image_pdfs"
    name="digilibraries_2"
    # for name_dir in os.listdir(dir):

    new_name_dir=os.path.join(new_dir,name)
    old_name_dir=os.path.join(dir,name)
    if not os.path.exists(new_name_dir):
        os.mkdir(new_name_dir)
    for part_dir in os.listdir(old_name_dir):
        try:
            new_part_dir=os.path.join(new_name_dir,part_dir)
            old_part_dir=os.path.join(old_name_dir,part_dir)
            if not os.path.exists(new_part_dir):
                os.mkdir(new_part_dir)
            for pdf_name in os.listdir(old_part_dir):
                new_pdf_path = os.path.join(new_part_dir, pdf_name)
                old_pdf_path = os.path.join(old_part_dir, pdf_name)
                print(old_pdf_path,new_pdf_path)
                main(old_pdf_path,new_pdf_path)
        except:
            pass


def queue_run_dir(item):
    old_dir = r"E:\电子书\pdfs\dig"
    new_dir = r"E:\电子书\image_pdfs\dig"
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    new_path=os.path.join(new_dir,item)
    old_path=os.path.join(old_dir,item)
    try:
        print("开始转换："+old_path)
        main(old_path,new_path)
        return True
    except:
        return False





def queue_update():
    q=Redis_Queue()
    dir=r"E:\电子书\pdfs\dig"
    for item in os.listdir(dir):
        q.set_item(item)



def split_pdf(start=2,end=4,name="report2013_1.pdf"):
    path=r"C:\pdfs\0205\report2013.pdf"
    images_dir=r"C:\pdfs\0205"
    # pdf_file = open(path, "rb")
    # pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
    # num = pdf.getNumPages()
    # new_pages = -1
    # if num < 10:
    #     new_pages = 1
    # elif num > 100:
    #     new_pages = 10
    # elif num > 500:
    #     return None
    # else:
    #     new_pages = int(num / 10)
    # pdf_file.close()
    # image_paths = []
    # with convert_from_path(path) as images:
    images = convert_from_path(path)
    # print(images,type(images))
    image_paths=[]
    new_path=os.path.join(images_dir,name)
    for index, image in enumerate(images):
        if index>start and index<=end:

            image_path = images_dir + str(index) + ".jpg"
            image.save(image_path)
            image_paths.append(image_path)

    a4inpt = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
    layout_fun = img2pdf.get_layout_fun(a4inpt)
    with open(new_path, 'wb') as f:
        f.write(img2pdf.convert(image_paths, layout_fun=layout_fun))




if __name__ == '__main__':
    split_pdf(start=2,end=4,name="report2013_1.pdf")
    # run_dir()
    # queue_update()
    # q=Redis_Queue()
    # q.queue_run(f=queue_run_dir,skip_first=True)
    # main(r"C:\pdfs\test\85590d58a90611e9b3e500ac37466cf9.pdf",)
    # a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
    # layout_fun = img2pdf.get_layout_fun(a4inpt)
    # with open('a.pdf','wb') as f:
    #     f.write(img2pdf.convert([r'C:\temp\png\page_1.png',r'C:\temp\png\page_2.png'],layout_fun=layout_fun))

