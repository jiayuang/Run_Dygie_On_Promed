import argparse
import os
import json
import re
import spacy
import string

def findIndiceForMention(document, mention):
    for i in range(len(document)- len(mention) + 1):
        for j in range(len(mention)):
            if mention[j] != document[i+j]:
                break

        if (mention[-1] == document[i+len(mention)-1]) and (j+1 == len(mention)):
            return True, i
    return False, -1

def preprocess_string(doc_str):
    doc_str = re.sub("\n", "", doc_str)
    doc_str = doc_str.replace("'", '"')
    return re.sub(r' +', ' ', re.sub(r'(\-\-+|\.\.+)', "", doc_str.lower()))

def main():
    # new_train_f = open("new_train.json", "w")
    # new_ptrain_f = open("new_pretty_train.json", "w")
    # new_test_f = open("new_test.json", "w")
    # new_ptest_f = open("new_pretty_test.json", "w")
    # new_dev_f = open("new_dev.json", "w")
    # new_pdev_f = open("new_pretty_dev.json", "w")
    new_debug_f = open("debug_out.json","w")


    files = ["debug.json"]
    # files = ["train.json", "dev.json", "test.json"]
    for file in files:
        instances = []
        with open(file) as f:
            for row in f:
                # each row (sample) is a json object
                a_dict = json.loads(row)
                instances.append(a_dict)
            print("len(instances): ", len(instances))
            print("type(instances): ", type(instances),"\n")
            for inst in instances:
                doc = {}
                entityWithRole = list()
                entityWithRole.append(list())
                doc["doc_key"] = inst["docid"]
                doc["dataset"] = "SciREX"
                document = inst["doctext"]
                prepro_doc = preprocess_string(document)
                nlp = spacy.load("en_core_web_sm")
                spacyed_doc = nlp(prepro_doc)
                # tokens = [[preprocess_string(token.text) for token in spacyed_doc if token.text.isalnum()]]
                tokens = [[preprocess_string(token.text) for token in spacyed_doc if token.text not in string.punctuation]]
                '''
                要不要只alnum()? 
                '''
        
                doc["sentences"] = tokens
                templates = inst["templates"]

                # print(tokens)

                for template in templates:
                    # print("templ: ", template)
                    roles = ["Material", "Method", "Metric", "Task"]

                    for role in roles:
                        # print("role:", role)
                        if len(template[role]) != 0:
                            # print("template[role][0]: ", template[role][0])
                            entities = template[role][0]
                            for entity in entities:
                                # print("tokens[0]: ", tokens[0])
                                # print("entity: ", entity)
                                enti_tokens = nlp(entity[0])
                                # print("enti_tokens: ", enti_tokens)
                                preped_enti_tokens = [[preprocess_string(token.text) for token in enti_tokens if token.text not in string.punctuation]]
                                # preped_enti_tokens = [[preprocess_string(token.text) for token in enti_tokens if token.text.isalnum()]]
                                '''
                                要不要只 alnum?
                                '''
                                # print("prep_enti_tokens: ", preped_enti_tokens)

                                # print("==============GOING IN SEARCHING =================\n")

                                # print("arg1 is: ", tokens[0])
                                # print("arg2 is:", preped_enti_tokens)

                                res = findIndiceForMention(tokens[0], preped_enti_tokens[0])

                                # print("res:", res)

                                # print("==============SEARCH DONE=================\n")
                                if res[0] == True:
                                    # triple = [res[1], res[1]+len(entity)-1, role]
                                    triple = [res[1], res[1]+len(preped_enti_tokens[0])-1, role]
                                    # print(preped_enti_tokens[0])
                                    # print(type(preped_enti_tokens[0]))
                                    # BUG: previously, the len(entity) is 2. 

                                    # 这个 len entity 还有点问题.

                                    '''
                                    还有就是发现: 带dash的token不见了. 
                                    "imagenet-1 k dataset"  --> k dataset
                                
                                    就是因为 isalnum, 只允许一个token里全是字母加数字。
                                    
                                    '''
                                    entityWithRole[0].append(triple)

                doc["ner"] = entityWithRole    

                # print(doc)
                if file == "train.json":
                    # print("========writing new train file========")
                    new_train_f.write(json.dumps(doc) + "\n")
                    # new_ptrain_f.write(json.dumps(doc, indent=4) + "\n")
                elif file == "dev.json":
                    # print("========writing new dev file========")
                    new_dev_f.write(json.dumps(doc) + "\n")
                    # new_pdev_f.write(json.dumps(doc, indent=4) + "\n")
                elif file == "test.json":
                    # print("========writing new test file========")
                    new_test_f.write(json.dumps(doc) + "\n")
                    # new_ptest_f.write(json.dumps(doc, indent=4) + "\n")
                else:
                    new_debug_f.write(json.dumps(doc) + "\n")



if __name__ == "__main__":
    main()