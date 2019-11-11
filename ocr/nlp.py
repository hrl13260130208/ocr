
from stanfordcorenlp import StanfordCoreNLP


nlp = StanfordCoreNLP(r'C:\File\stanford-corenlp-full-2016-10-31')

person="PERSON"
number="NUMBER"


def nlp_read(text):
    l=nlp.ner(text)
    print(l)
    print(itme_analyze(l))
    # for i in nlp.ner(text):
    #     if i[1]==person:
    #         if last_item_label==None or last_item_label==person:
    #             item+=i[0]+" "
    #             last_item_label=person
    #         else:


    nlp.close()

def itme_analyze(list,item="",last_item_label=None,person_list=[],number_list=[]):
    if len(list)==0:
        return person_list,number_list
    current=list.pop(0)
    print(current)
    if current[1]==last_item_label:
        item+=item[0]
    else:
        if last_item_label==person:
            person_list.append(item)
        elif last_item_label==number:
            number_list.append(item)
        item=current[0]
        last_item_label=current[1]
    return itme_analyze(list,item,last_item_label,person_list,number_list)


if __name__ == '__main__':
    text="Johanna Puurunen, Terhi Piltonen, Laure Morin-Papunen, Antti Perheentupa,Ilkka Ja¨rvela¨, Aimo Ruokonen, and Juha S. Tapanainen "
    nlp_read(text)






