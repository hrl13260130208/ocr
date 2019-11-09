import elasticsearch.client.nodes
from elasticsearch import helpers
from elasticsearch import Elasticsearch
import os

es = Elasticsearch([
                    {'host': '192.168.56.21', "port": 9200},
                    {'host': '192.168.56.22', "port": 9200},
                    {'host': '192.168.56.23', "port": 9200},

                ])
def search():
    es_search_options = set_search_optional()
    es_result = get_search_result(es_search_options)
    final_result = get_result_list(es_result)
    return final_result


def get_result_list(es_result):
    final_result = []
    for item in es_result:
        final_result.append(item['_source'])
    return final_result


def get_search_result(es_search_options, scroll='3m', index='pdf',  timeout="1m"):
    es_result = helpers.scan(
        client=es,
        query=es_search_options,
        scroll=scroll,
        index=index,
        timeout=timeout
    )
    return es_result


def set_search_optional():
    # 检索选项
    es_search_options = {
        "query": {
            "match_all": {}
        }
    }
    return es_search_options


if __name__ == '__main__':
    final_results = search()
    print(final_results)
    # dir=r"C:\pdfs\0815"
    # index=0
    # for file in final_results:
    #     # file_name=file["file_name"].replace(".pdf",".txt")
    #     file_name=str(index)+".txt"
    #     index+=1
    #     path=os.path.join(dir,file_name)
    #     with open(path,"w+",encoding="utf-8") as f:
    #         f.write(file["attachment"]["content"].replace("\n"," "))
