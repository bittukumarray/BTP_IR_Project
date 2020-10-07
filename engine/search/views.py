from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.db import connection
import json
from collections import OrderedDict
import spacy
import math
import json
import os
sp = spacy.load('en_core_web_sm')
module_dir = os.path.dirname(__file__)
# print(module_dir)

words_dict={}
docs_dict={}

#These codes are for indexing :----
class createIndex(APIView):
    def get(self, req):
        data=""
        with open(os.path.join(module_dir, 'sof20k.json')) as f:
            data = json.load(f)

        print(len(data))
        j=0
        for i in data:
            # if(i["id"]==2143 or i["id"]==8476 or i["id"]==8621 or i["id"]==23294):
            #     print(i["id"], i["title"])
            # if(j>=10):
            #     break
            title(i["title"], i["id"])
            j+=1
        id = len(data)
        CalcTF_IDF(id)
        print("after title")
        # print(docs_dict)
        with open(os.path.join(module_dir, 'sof20k.json')) as f:
            tempFile = json.load(f)
            convert_file(tempFile)


        filePath=os.path.join(module_dir, 'sof_words_dict.json')
        with open(filePath, 'w+') as f:
            json.dump(words_dict, f)


        filePath=os.path.join(module_dir, 'sof_docs_dict.json')
        with open(filePath, 'w+') as f:
            json.dump(docs_dict, f)


        return Response({"msg":"successfully trained", "status":status.HTTP_201_CREATED})


def title(titleText, docId):

    stop_chars = [",", "*", "\n", "\r\n", "\r", "'s", "-", ";", ":", "?", "(", ")", '"', "[", "]","–","." ] 
    stop_words=[",", "-", "/", "'s", "\r", "\r\n", "\n ", "\r\n ", "\n", ";", ":", "?", "(", ")", '"', "[", "]","–",'is', " ", "stack", "overflow", 'to', 'of', 'the', 'ourselves', 'hers', 'yourself', 'there', 'they', 'own', 'an', 'be', 'for', 'its', 'yours', 'such', 'into', 'of', 'itself', 'off', 'is', 's', 'am', 'or', 'as', 'from', 'him', 'each', 'the', 'themselves', 'are', 'we', 'these', 'your', 'his', 'don', 'nor', 'me', 'were', 'her', 'himself', 'this', 'our', 'their', 'to', 'ours', 'had', 'she', 'at', 'them', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'so', 'he', 'you', 'herself', 'has', 'myself',  'those', 'i', 't', 'being', 'if', 'theirs', 'my', 'a', 'by', 'it', 'was', 'here', 'how', 'can']

    for i in stop_chars:
        titleText = titleText.replace(i, "")

    titleText=titleText.lower().split(" ")#it wiil be in the form of a list

    #To delete stopwords
    i=0;
    while(i<len(titleText)):
        if titleText[i] in stop_words or len(titleText[i])==0:
                del titleText[i]
                i=i-1
        i+=1

    #this is to lemmitization
    titleTextTemp=titleText[0]
    for i in range(1,len(titleText)):
        titleTextTemp+=" "+titleText[i]
    titleTextTemp = sp(titleTextTemp)
    titleText=[]

    #creating words dictionary with documents ids.
    if(docId==2143 or docId==8476 or docId==8621 or docId==23294):
        print(titleTextTemp)

    for word in titleTextTemp:
        titleText.append(word.lemma_)
        try:
            words_dict[word.lemma_].append(docId)
        except:
            words_dict[word.lemma_]=[docId]
    if(docId==2143 or docId==8476 or docId==8621 or docId==23294):
        print(titleText)

    #to store the documents into dictionary and score for each word
    for word in titleText:
        if docId in docs_dict:
            if word in docs_dict[docId]:
                docs_dict[docId][word]["tf"]=+1
            else:
                docs_dict[docId].update({word:{"tf":1}})
        else:
            docs_dict[docId]={word:{"tf":1}}


    #to calculate denominator mode score for each documents
    tempWord_dict={}
    for word in titleText:
        try:
            tempWord_dict[word]+=1
        except:
            tempWord_dict[word]=1
    docs_dict[docId]["denom-netor-score"]=CalcDenomMode(tempWord_dict, len(titleText))
    docs_dict[docId]["total-terms"]=len(titleText)



#denominator mode calculating function
def CalcDenomMode(dict, total):
    sqr = 0
    for term in dict:
        sqr = sqr+ (dict[term]/total)**2
    sqr = math.sqrt(sqr)
    return sqr
      

#calculating tf-idf value and associating it with for each token for each documents
def CalcTF_IDF(N):
    for id in docs_dict:
        for word in docs_dict[id]:
            try:
                df = len(words_dict[word])
                idf = math.log10(N/df)

                docs_dict[id][word]["tf_idf"]=((1+math.log10(docs_dict[id][word]["tf"]))/docs_dict[id]["total-terms"])*idf
            except:
                pass

#to convert file into desire format so that easily output the pages
def convert_file(filename):
    updated_file={}
    id=1
    for dict in filename:
        updated_file[id]=dict
        id+=1
    # print(updated_file)
    filePath=os.path.join(module_dir, 'sof_updated20k.json')
    with open(filePath, 'w+') as f:
            json.dump(updated_file, f)












words_dict_file={}
docs_dict_file={}

class get_ranked_docs(APIView):
    def post(self, req):
        print("in request data ", req.data)
        with open(os.path.join(module_dir, 'sof_docs_dict.json')) as f:
            docs_dict_file = json.load(f)

        with open(os.path.join(module_dir, 'sof_words_dict.json')) as f:
            words_dict_file = json.load(f)


        inp =req.data["query"] #input("Enter the input\n")
        cleanTextList=userQuery(inp)
        docs_list_from_words_dict=get_Docs(cleanTextList["cleantext"], words_dict_file)
        docs_list_dict={}#to store all the documents in which at least one word is present

        # print(docs_list_from_words_dict)

        for docid in docs_list_from_words_dict:
            docs_list_dict.update({docid:docs_dict_file[str(docid)]})

        # print(docs_list_dict)
        # print(cleanTextList["cleandict"])

        final_ranking={}
        query_denom_score=CalcDenomMode(cleanTextList["cleandict"], len(cleanTextList["cleantext"]))
        # print("denom is ",query_denom_score)
        for id in docs_list_dict:
            score=0
            for word in cleanTextList["cleandict"]:
                try:
                    score = score + cleanTextList["cleandict"][word]*docs_list_dict[id][word]["tf_idf"]
                except:
                    pass
            final_ranking[id]=score/(query_denom_score*docs_list_dict[id]["denom-netor-score"])

        final_ranking = sorted(final_ranking.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
        # print(final_ranking[0])
        
        with open(os.path.join(module_dir, 'sof_updated20k.json')) as f:
            tempFile = json.load(f)
            # print(tempFile)
            final_ans=[]
            #print(final_ranking[0:50])
            for doc in final_ranking:
                final_ans.append(tempFile[str(doc[0])])
            return Response(final_ans[0:20])
    


def userQuery(titleText):
    
    stop_chars = [",", "*", "\n", "\r\n", "\r", "'s", "-", ";", ":", "?", "(", ")", '"', "[", "]","–","." ] 
    stop_words=[",", "-", "/", "'s", "\r", "\r\n", "\n ", "\r\n ", "\n", ";", ":", "?", "(", ")", '"', "[", "]","–",'is', " ", "stack", "overflow", 'to', 'of', 'the', 'ourselves', 'hers', 'yourself', 'there', 'they', 'own', 'an', 'be', 'for', 'its', 'yours', 'such', 'into', 'of', 'itself', 'off', 'is', 's', 'am', 'or', 'as', 'from', 'him', 'each', 'the', 'themselves', 'are', 'we', 'these', 'your', 'his', 'don', 'nor', 'me', 'were', 'her', 'himself', 'this', 'our', 'their', 'to', 'ours', 'had', 'she', 'at', 'them', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'so', 'he', 'you', 'herself', 'has', 'myself',  'those', 'i', 't', 'being', 'if', 'theirs', 'my', 'a', 'by', 'it', 'was', 'here', 'how', 'can']

    for i in stop_chars:
        cleanText = titleText.replace(i, "")

    cleanText=cleanText.lower().split(" ")#it wiil be in the form of a list

    #To delete stopwords
    i=0;
    while(i<len(cleanText)):
        if cleanText[i] in stop_words or len(cleanText[i])==0:
                del cleanText[i]
                i=i-1
        i+=1

    #this is to lemmitization
    titleTextTemp=cleanText[0]
    for i in range(1,len(cleanText)):
        titleTextTemp+=" "+cleanText[i]
    titleTextTemp = sp(titleTextTemp)
    cleanText=[]

    #creating words dictionary with documents ids.

    graph_data=""
    with open(os.path.join(module_dir, 'per_word_knowledge_graph.json')) as f:
        graph_data = json.load(f)
    total=0
    for word in titleTextTemp:
        try:
            total+=len(graph_data[word.lemma_])
        except:
            pass

    print("total is ", total)
    length = len(titleTextTemp)
    clean_dict={}
    for word in titleTextTemp:
        cleanText.append(word.lemma_)
        try:
            clean_dict[word.lemma_]+=1/length
            try:
                clean_dict[word.lemma_]=clean_dict[word.lemma_]+len(graph_data[word.lemma_])/total
            except:
                pass
            if clean_dict[word.lemma_]>1:
                clean_dict[word.lemma_]=1
        except:
            clean_dict[word.lemma_]=1/length
            try:
                clean_dict[word.lemma_]=clean_dict[word.lemma_]+len(graph_data[word.lemma_])/total
            except:
                pass
            if clean_dict[word.lemma_]>1:
                clean_dict[word.lemma_]=1
    
    # print(cleanText)
    return {"cleantext":cleanText, "cleandict":clean_dict}


#getting all the documents in which the words are present
def get_Docs(cleanInp, words_dict_file):
    docs_list=[]
    for word in cleanInp:
        try:
            docs_list=docs_list+words_dict_file[word]
        except:
            pass
    
    return set(docs_list)



class getSuggestData(APIView):
    def get(self, request):
        data=""
        with open(os.path.join(module_dir, 'sof20k.json')) as f:
            data = json.load(f)
        return Response({"data":data})