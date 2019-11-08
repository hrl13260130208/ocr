
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import sys

def update_file(file_path):
    es = Elasticsearch([{'host': '192.168.56.21', "port": 9200},], timeout=500)
    data=[]
    for index,line in enumerate(open(file_path).readlines()):
        print(index)
        args=line.replace("\n","").split("$$$$")

        if args.__len__()!=6:
            print("字段数有误！")
        else:
            data.append({"_index": "pdf",
                         "_type": "test",
                         "_source": {"title": args[0], "author": args[1],"abstract":args[2],"date":args[3],"page_count":args[4],"ad":args[5]+".pdf"}
                         })

    helpers.bulk(es, data)


if __name__ == '__main__':
    path=sys.argv[1]
    # print(path)
    update_file(path)
    # update(r"C:\pdfs\jx0621")
    # pdf_to_text(r"C:\pdfs\jx0621",r"C:\pdfs\test")
    # read_pdf(r"G:\hrl\adams1\adams\1950-2010\ML19196A077.pdf")



