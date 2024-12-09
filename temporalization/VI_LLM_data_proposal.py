# --coding:utf-8--
import json
import os
from argparse import ArgumentParser

def documentize(sents):
    doc = ''
    for sent in sents:
        doc += ' '.join(sent[:-1])
        doc += (sent[-1] + ' ')
    return doc[:-1]

def judge_timestamp(time_token):
    interval_tokens = ["year", "month", "day", "hour", "minute", "seconds"]
    for token in interval_tokens:
        if token in time_token.lower():
            return False
    return True

def get_LLM_input(input_path, output_path, use_rel=True):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    files = ['train_temporal.json', 'dev_temporal.json', 'test_temporal.json']
    rel_info = json.load(open(os.path.join(input_path, "rel_info.json")))

    relation_path = os.path.join(input_path, 'rel_info.json')
    max_pmt_len = 0
    with open(relation_path, 'r', encoding='utf-8') as f:
        rel_info = json.load(f)

    for file in files:
        raw_data = json.load(open(os.path.join(input_path, file), 'r', encoding='utf-8'))
        new_data = []
        for data in raw_data:
            doc_content = documentize(data['sents'])
            vertex_list = data['vertexSet']
            entity_list = [repr(vertex[0]['name']) for vertex in vertex_list if vertex[0]['type'] != "TIME"]
            entity_str = ', '.join(entity_list)
            time_list = [repr(vertex[0]['name']) for vertex in vertex_list if vertex[0]['type'] == "TIME" and judge_timestamp(vertex[0]['name'])]
            time_str = ', '.join(time_list)
            relation_set_str = ', '.join([repr(value) for value in rel_info.values()])
            prompt1 = 'Context: ' + repr(doc_content) + \
                    '\nAnd entity list: [ ' + entity_str + \
                    ' ] \n relation list: [' + relation_set_str + \
                    ' ] \n timestamps_list:[' + time_str + \
                    ' ]. \n For example, <\'Jim\', \'born in\', \'Stockholm\', \'1962\'>, \n<\'Jim\', \'died in\', \'Los Angeles\', \'1995\'>'
            prompt2 = 'Please generate at least 5 quadruples that are considered to be true with respect to below context using only given entities, relations ' \
                        'and timestamps from the entity, relation and timestamp list. Please answer using quadruples in form of <\'entity1\', \'relation\', \'entity2\', ' \
                        '\'timestamp\'>. \'entity1\' and \'entity2\' are from the below entity list, \'relation\' is from the below relation list, and \'timestamp\' ' \
                        'is from the below timestamp list. It is true if \'entity1\' did \'relation\' to \'entity1\' at \'timestamp\''
            prompt3 = ', '.join([
                "<\'{}\', \'{}\', \'{}\', \'{}\'>"
                    .format(vertex_list[label["h"]][0]["name"], rel_info[label["r"]],
                            vertex_list[label["t"]][0]["name"], vertex_list[label["time"]][0]["name"])
                for label in data["labels"]])
            new_data.append({
                "instruction": prompt2,
                "input": prompt1,
                "output": prompt3,
                "history": []
            }) 
        
        print(f"Num of {file} is {len(new_data)}")
        json.dump(new_data, open(os.path.join(output_path, file.replace('_temporal', '_chat')), 'w', encoding='utf-8'))
    return




if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', help='Path to the input file', default='data/tem-re-docred')
    parser.add_argument('-o', '--output', help='Path to the output file', default='data/processed_data/tem-re-docred')
    args = parser.parse_args()
    get_LLM_input(args.input, args.output, use_rel=True)