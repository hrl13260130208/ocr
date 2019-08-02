
import img2pdf
from pdf2image import convert_from_path
import PyPDF2
import os


def main(path,new_path):
    images_dir="C:/temp/png/"
    pdf_file = open(path, "rb")
    pdf = PyPDF2.PdfFileReader(pdf_file, strict=False)
    num=pdf.getNumPages()
    new_pages=-1
    if num<10:
        new_pages=1
    elif num>100:
        new_pages=10
    else:
        new_pages=int(num/10)
    images = convert_from_path(path)
    print(images,type(images))
    image_paths=[]
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
    dir="C:/pdfs"
    new_dir="C:/image_pdfs/"
    name=""
    # for name_dir in os.listdir(dir):

    new_name_dir=os.path.join(new_dir,name)
    old_name_dir=os.path.join(dir,name)
    if not os.path.exists(new_name_dir):
        os.mkdir(new_name_dir)
    for part_dir in os.listdir(old_name_dir):
        new_part_dir=os.path.join(new_name_dir,part_dir)
        old_part_dir=os.path.join(old_name_dir,part_dir)
        if not os.path.exists(new_part_dir):
            os.mkdir(new_part_dir)
        for pdf_name in os.listdir(old_part_dir):
            new_pdf_path = os.path.join(new_part_dir, pdf_name)
            old_pdf_path = os.path.join(old_part_dir, pdf_name)
            main(old_pdf_path,new_pdf_path)






if __name__ == '__main__':
    main(r"C:\pdfs\test\85590d58a90611e9b3e500ac37466cf9.pdf",)
    # a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
    # layout_fun = img2pdf.get_layout_fun(a4inpt)
    # with open('a.pdf','wb') as f:
    #     f.write(img2pdf.convert([r'C:\temp\png\page_1.png',r'C:\temp\png\page_2.png'],layout_fun=layout_fun))

