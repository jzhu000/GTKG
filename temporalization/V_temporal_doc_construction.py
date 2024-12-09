# --coding:utf-8--
import json
import os


def gen_data_intersection(rels1, rels2):
    for key1 in rels1.items():
        rel1_dict = {"##".join([str(rel["h"]), rel["r"], str(rel["t"]), str(rel["time"])]): rel for rel in rels1[key1]}
        rel2_dict = {"##".join([str(rel["h"]), rel["r"], str(rel["t"]), str(rel["time"])]): rel for rel in rels2[key1]}
        new_rel_list = [rels1[new_key] for new_key in set(list(rel1_dict.keys())).intersection(list(rel2_dict.keys()))]
        rel1_dict[key1] = new_rel_list
    return rels1

        

def read_rels(dataset):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data1_dir = os.path.join(root_dir, f'data/{dataset}')
    data2_dir = os.path.join(root_dir, f'data/{dataset}')
    train_title2rels = {}
    valid_title2rels = {}
    test_title2rels = {}

    for file in os.listdir(data1_dir):
        rel1_path = os.path.join(data1_dir, file)
        rel2_path = os.path.join(data2_dir, file)
        if "train" in file:
            with open(rel1_path, "r", encoding="utf-8") as f:
                rel_dict1 = json.load(f)
            with open(rel2_path, "r", encoding="utf-8") as f:
                rel_dict2 = json.load(f)
            train_title2rels.update(gen_data_intersection(rel_dict1, rel_dict2))
        elif "dev" in file:
            with open(rel1_path, "r", encoding="utf-8") as f:
                rel_dict1 = json.load(f)
            with open(rel2_path, "r", encoding="utf-8") as f:
                rel_dict2 = json.load(f)
            valid_title2rels.update(gen_data_intersection(rel_dict1, rel_dict2))
        elif "test" in file:
            with open(rel1_path, "r", encoding="utf-8") as f:
                rel_dict1 = json.load(f)
            with open(rel2_path, "r", encoding="utf-8") as f:
                rel_dict2 = json.load(f)
            test_title2rels.update(gen_data_intersection(rel_dict1, rel_dict2))
    
    return train_title2rels, valid_title2rels, test_title2rels

def combine_rels(rel1s, rel2s):
    for title in rel1s.keys():
        if title in rel2s:
            rel2s[title] += rel1s[title]
        else:
            rel2s[title] = rel1s[title]
    rel_count = sum([len(rels) for rels in rel2s.values()])
    print(f"The num of new rels is {rel_count}")
    return rel2s

def reconstruct_rels(rels_dict_list, dataset):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/{dataset}')
    save_path = os.path.join(root_dir, f'data/tem-re-docred/')

    relation_path = os.path.join(data_dir, 'rel_info.json')
    with open(relation_path, 'r', encoding='utf-8') as f:
        id2rel = json.load(f)

    temporal_path = os.path.join(data_dir, f'temporal/temporal_relation.txt')
    rel2tem = {rel1: rel2 for rel1, rel2 in [line.strip().split(" ## ") for line in open(temporal_path, 'r')]}
    tem_rel_set = set(rel2tem.values())

    new_rel_dict_list = []

    for rels_dict in rels_dict_list:
        new_rel_dict = {}
        for title, rels in rels_dict.items():
            new_rel_title_list = []
            for rel in rels:
                if rel["r"] in id2rel:
                    rel["r"] = id2rel[rel["r"]]
                if rel["r"] in rel2tem:
                    rel["r"] = rel2tem[rel["r"]]
                    new_rel_title_list.append(rel)
                elif rel["r"] in tem_rel_set:
                    new_rel_title_list.append(rel)

            if len(new_rel_title_list) != 0:
                new_rel_dict[title] = new_rel_title_list
        new_rel_dict_list.append(new_rel_dict)


    all_rels = list(tem_rel_set)
    all_rels.sort()
    new_rel2id = {rel: f"T{i}" for i, rel in enumerate(all_rels)}

    rels_dict_list = new_rel_dict_list

    for rels_dict in rels_dict_list:
        for rels in rels_dict.values():
            for rel in rels:
                rel["r"] = new_rel2id[rel["r"]]
    

    id2new_rel = dict(zip(list(new_rel2id.values()), list(new_rel2id.keys())))
    with open(os.path.join(save_path, 'rel_info.json'), 'w', encoding='utf-8') as f:
        json.dump(id2new_rel, f, indent=4)

    return rels_dict_list

def transform_rels(dataset):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/{dataset}')
    for file in os.listdir(data_dir):
        rel_path = os.path.join(data_dir, file)
        with open(rel_path, "r", encoding="utf-8") as f:
            title2rels = json.load(f)
        for title, rels in title2rels.items():
            title2rels[title] = [{"h": rel[0], "r": rel[1], "t": rel[2], "time": rel[3], "evidence": []} for rel in rels]
        with open(rel_path, "w", encoding="utf-8") as f:
            title2rels = json.dump(title2rels, f, indent=4)


def construct_tem_data(rels_list, dataset='docred', save_dataset='tem-re-docred'):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/{dataset}')
    save_dir = os.path.join(root_dir, f'data/{save_dataset}')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    files = ['train_revised.json', 'dev_revised.json', 'test_revised.json']


    # process data
    for file, rels in zip(files, rels_list):
        raw_data = json.load(open(os.path.join(data_dir, file), 'r', encoding='utf-8'))
        new_data = []
        for sample in raw_data:
            if sample["title"] in rels:
                sample["labels"] = rels[sample["title"]]
                new_data.append(sample)
        print(f"Num of {file} is {len(new_data)}")
        json.dump(new_data, open(os.path.join(save_dir, file.replace("revised", "temporal")), 'w', encoding='utf-8'))


if __name__ == '__main__':
    
    rel_data_path_gpt = "tem-re-docred/add_rels/gpt"
    rel_data_path_glm = "tem-re-docred/add_rels/glm"
    rel_data_path_com = "tem-re-docred/com_rels"
    train_add_rels, valid_add_rels, test_add_rels = read_rels(rel_data_path_gpt, rel_data_path_glm)
    train_com_rels, valid_com_rels, test_com_rels = read_rels(rel_data_path_com)

    train_rels = combine_rels(train_add_rels, train_com_rels)
    valid_rels = combine_rels(valid_add_rels, valid_com_rels)
    test_rels = combine_rels(test_add_rels, test_com_rels)

    rel_dict_list = reconstruct_rels([train_rels, valid_rels, test_rels], 're-docred')

    origin_doc_dataset = "re-docred"
    new_doc_dataset = "tem-re-docred"
    construct_tem_data(rel_dict_list, dataset=origin_doc_dataset, save_dataset=new_doc_dataset)