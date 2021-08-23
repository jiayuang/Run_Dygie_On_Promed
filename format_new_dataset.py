"""
Format a new dataset.
"""

import argparse
import os
import json
import re
import spacy
import string


def preprocess_string(doc_str):
  doc_str = re.sub("\n", "", doc_str)
  
  doc_str = doc_str.replace("'", '"')
  return re.sub(r' +', ' ', re.sub(r'(\-\-+|\.\.+)', "", doc_str.lower()))

def findIndiceForMention(document, mention):
      for i in range(len(document)- len(mention) + 1):
            
            for j in range(len(mention)):
              if mention[j] != document[i+j]:
                break

            if (mention[-1] == document[i+len(mention)-1]) and (j+1 == len(mention)):
              return True, i

      return False, -1


def convert_data(text_dir, ans_dir, mode, percent_dev=0): #use exclusively for formatting test dataset in this case

    slot_names = ['Story', 'ID', 'Date', 'Event', 'Status', 'Containment', 'Country', 'Diseases', 'Victims']
    role_names = ['Status', 'Country', 'Disease', 'Victims']

    nlp_name = "en_core_web_sm"
    nlp = spacy.load(nlp_name)

    docs = os.listdir(text_dir)
    #docs = ["20020113.3249.maintext"]

    if mode == "train":
      out_f = open("train.json", "w")
      pout_f = open("pretty_train.json", "w")

    if mode == "test":
      if percent_dev == 0:
        raise Exception("You need to decide percentage of test set to be used as dev set.")
      out_f = open("test.json", "w")
      pout_f = open("pretty_test.json", "w")
      dev_f = open("dev.json", "w")
      pdev_f = open("pretty_dev.json", "w")
      missing_country_dev = []
    
    missing_country = []
    dev_count = int((percent_dev/100)*len(docs))

    for doc in docs:
      #new_doc = {}
      #parts = doc.split(".")
      #new_doc["docid"] = "0-PROMED-" + "".join(parts[:2])
      
      parts = doc.split(".")
      text_f = format_document(text_dir + "/" + doc, "ProMed", "0-PROMED-" + "".join(parts[:2]), nlp)
      #text_f = open(text_dir + "/" + doc, "r")

      #new_doc["doctext"] = preprocess_string("".join(line[:-1] for line in text_f))[1:]
      temp_f = open(ans_dir + "/" + doc + ".annot", "r")

      #newline_count = 0
      #new_template = False

      #index all words with cumulative counts
      #current_role = ""

      '''
      cumulative_token_indice = 0
      counted_token_sentences = []
      for word in text_f["sentences"]: 
        counted_token_sentences.append((word, cumulative_token_indice))
        cumulative_token_indice += 1
      '''

      #extract gold roles and fillers from gold template
      events = []
      new_line_count = 0
      event = {}
      new_template = False


      entityWithRole = list()
      entityWithRole.append(list())

      for line in temp_f:
        if new_line_count == 2 or new_template:
          if event != {}:
            events.append(event)
          event = {}
          new_line_count = 0
          new_template = False
          current_role = ""

        l = line[:-1]
        if line == "\n":
          new_line_count += 1
          continue
        elif l.split(" ")[0] == "Bytespans":
          break
        else:
          data_line = [word.strip() for word in l.split(":")]
          if data_line[0] == "Event" and data_line[1] == "not an outbreak":
            new_template = True

          if data_line[0] in role_names:
            current_role = data_line[0]
            if data_line[1] == "-----":
              event[current_role] = []
            else:
              #if current_role == "Event" or current_role == "Date" or current_role == "Story" or current_role == "ID":
              #  continue
              if current_role == "Status":
                
                #role_filler = data_line[1].strip().replace("'", '"')
                #event[current_role] = role_filler
                continue
              #elif current_role == "Disease":
                #event_trigger_tokens = [[preprocess_string(mention.strip()).split(" ")] for mention in data_line[1].split("/")][0] #straightforward setting to get rid of the complexity
                
              #  event["Disease"] = [[preprocess_string(mention.strip())] for mention in data_line[1].split("/")]
              else:

                temp = [mention for mention in data_line[1].split("/")]
                print(temp)
                firstMention = temp[0]
                print(firstMention)
                
                mentions = [[preprocess_string(token.text) for token in nlp(firstMention) if token.text not in string.punctuation]] 
                
                #print(mentions)
                for mention in mentions:
                  print(mention)
                  res = findIndiceForMention(text_f["sentences"][0], mention)
                  if res[0] == True:
                    triple = [res[1], res[1]+len(mention)-1, current_role]
                    print(triple)
                    print("------------")
                    
                    entityWithRole[0].append(triple)
                  

          else:
                if data_line[0] in slot_names:
                    current_role = data_line[0]
                else:
                    if current_role in role_names:
                       temp = [mention for mention in data_line[0].split("/")]
                       print(temp)
                       firstMention = temp[0]
                       print(firstMention)
                       
                       mentions = [[preprocess_string(token.text) for token in nlp(firstMention) if token.text not in string.punctuation]]
                       
                       #print(mentions)
                       for mention in mentions:
                          print(mention)
                          
                          res = findIndiceForMention(text_f["sentences"][0], mention)
                          if res[0] == True:
                            triple = [res[1], res[1]+len(mention)-1, current_role]
                            print(triple)
                            print("------------")
                            
                            entityWithRole[0].append(triple)
                          
      '''
      event_trigger_indice = -1
      for event in events:
        if len(event["Disease"]) == 0 or len(event["Disease"][0]) == 0:
          candidate = event["Country"][0]
          #print(candidate)
          trigger_type = "Country"
        else:
          candidate = event["Disease"][0]
          trigger_type = "Disease"

        for sent in counted_token_sentences:
          for tup in sent:
              if tup[0] == candidate[0][0]: #event trigger: first mention of disease:
                event_trigger_indice = tup[1]

        #if event_trigger_indice == -1:
        

      sentencesEvents = [] #distribute roles and mentions of events into sentences for a doc
      for sent in counted_token_sentences:
        sublist = []
        first_mention = True
        for event in events:
          e = []
          for role in event.keys():
            for mention in event[role]:
              res = findIndiceForMention(sent, mention[0]) #here is different now, sent is supposed to be a sentence before, now should be a document
              if res[0]:
                if first_mention:
                  event_tri = [event_trigger_indice, trigger_type]
                  e.append(event_tri)
                  first_mention = False

                mention_info = [res[1], res[1]+len(mention)-1, str(role)]
                e.append(mention_info)

          if len(e) != 0:
            sublist.append(e)
        sentencesEvents.append(sublist)
        '''

      text_f["ner"] = entityWithRole

      if mode == "test" and dev_count > 0:
        dev_f.write(json.dumps(text_f) + "\n")
        pdev_f.write(json.dumps(text_f, indent=4) + "\n")
        dev_count -= 1
      else:
        out_f.write(json.dumps(text_f) + "\n")
        pout_f.write(json.dumps(text_f, indent=4) + "\n")

def format_document(fname, dataset_name, doc_id, nlp):
    text = open(fname).read()
    text_ = preprocess_string(text)
    doc = nlp(text_)
    sentences = []
    tokens = [[preprocess_string(token.text) for token in doc if token.text not in string.punctuation and token.text != " "]]
    
    #document = [[preprocess_string("".join(line[:-1] for line in text))[1:]]]
    res = {"doc_key": doc_id,
           "dataset": dataset_name,
           "sentences": tokens}
    return res


def format_dataset(data_directory, output_file, dataset_name, use_scispacy):
    nlp_name = "en_core_sci_sm" if use_scispacy else "en_core_web_sm"
    nlp = spacy.load(nlp_name)

    fnames = [f"{data_directory}/{name}" for name in os.listdir(data_directory)]
    res = [format_document(fname, dataset_name, nlp) for fname in fnames]
    with open(output_file, "w") as f:
        for doc in res:
            print(json.dumps(doc), file=f)


def get_args():
    description = "Format an unlabled dataset, consisting of a directory of `.txt` files; one file per document."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("data_directory", type=str,
                        help="A directory with input `.txt files, one file per document.")
    parser.add_argument("output_file", type=str,
                        help="The output file, `.jsonl` extension recommended.")
    parser.add_argument("dataset_name", type=str,
                        help="The name of the dataset. Should match the name of the model you'll use for prediction.")
    parser.add_argument("--use-scispacy", action="store_true",
                        help="If provided, use scispacy to do the tokenization.")
    return parser.parse_args()


def main():
    #args = get_args()
    #format_dataset(**vars(args))

    text_dir = "tuning-zoned"
    ans_dir = "tuning-anskey"
    convert_data(text_dir, ans_dir, "train")

    text_dir = "test-zoned"
    ans_dir = "test-anskey"
    convert_data(text_dir, ans_dir, "test", 10)

if __name__ == "__main__":
    main()
