# --coding:utf-8--
import json
import os


def read_com_rels():
    root_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/re-docred/temporal/')
    with open(os.path.join(data_dir, "com_hop2.txt"), "r", encoding="utf-8") as f:
        hop2_rels = [line.strip().split(" ## ") for line in f.readlines()]

    return hop2_rels

def construct_temporal_data(dataset='re-docred'):
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/{dataset}/')
    save_tem_dir = os.path.join(root_dir, f'data/tem-{dataset}/com_rels')
    save_res_dir = os.path.join(root_dir, f'data/{dataset}/rest')

    if not os.path.exists(save_tem_dir):
        os.makedirs(save_tem_dir)

    if not os.path.exists(save_res_dir):
        os.makedirs(save_res_dir)
    files = ['train_revised.json', 'dev_revised.json', 'test_revised.json']

    relation_path = os.path.join(data_dir, 'rel_info.json')
    with open(relation_path, 'r', encoding='utf-8') as f:
        id2rel = json.load(f)
        rel2id = {value: key for key, value in id2rel.items()}
    
    hop2_rels = read_com_rels()
    hop2_rels = [[rel2id[r] for r in rel[:2]] + rel[2:] for rel in hop2_rels]


    # process train
    for file in files:
        raw_data = json.load(open(os.path.join(data_dir, file), 'r', encoding='utf-8'))
        res_data = []
        all_tem_rel = {}
        tem_rel_count = 0
        for sample in raw_data:
            tem_relations = []
            res_sample = sample
            

            temporal_ids = set()

            for i, mentions in enumerate(sample['vertexSet']):
                if mentions[0]["type"] == "TIME":
                    temporal_ids.update({i})
            
            if len(temporal_ids) == 0:
                res_data.append(res_sample)
                continue

            # res_sample["labels"] = []
            
            rel_triplets = {rel:[] for rel in id2rel.keys()}

            for relation in sample["labels"]:
                rel_triplets[relation['r']].append(relation)
    
            for rel1, rel2, tem_rel, rtype in hop2_rels:
                if rel_triplets[rel2] != [] and rel_triplets[rel1] != []:
                    if rtype == "ABACABC":
                        
                        tem_relations += [{"h": tri1["h"], "r": tem_rel, "t": tri1["t"], 
                                    "time": tri2["t"], "evidence": tri1["evidence"] + tri2["evidence"]} 
                                    for tri1 in rel_triplets[rel1] for tri2 in rel_triplets[rel2] 
                                    if tri1["h"] == tri2["h"]]
                    if rtype == "ABBCABC":
                        tem_relations += [{"h": tri1["h"], "r": tem_rel, "t": tri1["t"], 
                                    "time": tri2["t"], "evidence": tri1["evidence"] + tri2["evidence"]} 
                                    for tri1 in rel_triplets[rel1] for tri2 in rel_triplets[rel2] 
                                    if tri1["t"] == tri2["h"]]

            
            if tem_relations != []:
                all_tem_rel[sample["title"]] = tem_relations
                tem_rel_set = set([str(tr["h"]) + "_" + str(tr["t"]) for tr in tem_relations])
                res_sample["labels"] = [tri for tri in sample["labels"] if tri["t"] not in temporal_ids 
                                        and str(tri["h"]) + "_" + str(tri["t"]) not in tem_rel_set]
            res_data.append(res_sample)

            tem_rel_count += len(tem_relations)
            
        print(f"Num of temporal relations of {file} is {tem_rel_count}")
        json.dump(res_data, open(os.path.join(save_res_dir, file.replace("_revised", "_rest")), 'w', encoding='utf-8'))
        json.dump(all_tem_rel, open(os.path.join(save_tem_dir, file.replace("_revised", "_com_rels")), 'w', encoding='utf-8'), indent=4)
    # process dev/test
    return

if __name__ == '__main__':
    construct_temporal_data("re-docred")