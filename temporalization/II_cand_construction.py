# --coding:utf-8--
import json
import os

def judge_timestamp(time_token):
    interval_tokens = ["year", "month", "day", "hour", "minute", "seconds"]
    for token in interval_tokens:
        if token in time_token.lower():
            return False
    return True

def construct_cand_quads(dataset='re-docred'):
    """
    Generate data for LLMs.
    """
    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/{dataset}/rest')
    save_dir = os.path.join(root_dir, f'data/{dataset}/cand/')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    files = ['train_rest.json', 'dev_rest.json', 'test_rest.json']

    relation_path = os.path.join(root_dir, f'data/{dataset}/rel2hypothesis.txt')
    with open(relation_path, 'r', encoding='utf-8') as f:
        rel_hyp = [line.strip().split('\t') for line in f.readlines()]
        id2rel = {rh[0]: rh[1] for rh in rel_hyp}


    # process train
    for file in files:
        raw_data = json.load(open(os.path.join(data_dir, file), 'r', encoding='utf-8'))
        new_data = []
        for sample in raw_data:
            cand_sample = {
                "title": sample["title"],
                "context": " ".join([" ".join(words) for words in sample["sents"]]),
                "cand_temporal_relation": []
            }

            temporal_ids = set()

            for i, mentions in enumerate(sample['vertexSet']):
                if mentions[0]["type"] == "TIME":
                    temporal_ids.update({i})
            if len(temporal_ids) == 0:
                continue

            for relation in sample["labels"]:
                h_id, r_id, t_id = relation["h"], relation["r"], relation["t"]
                if h_id in temporal_ids or t_id in temporal_ids:
                    continue
                head = sample['vertexSet'][h_id][0]['name']
                tail = sample['vertexSet'][t_id][0]['name']
                cands = [[id2rel[r_id].replace("sub.", head).replace("obj.", tail) + f" on {sample['vertexSet'][time_id][0]['name']}.", 
                          {"h": h_id, "r": r_id, "t": t_id, "time": time_id, "evidence": relation["evidence"]}] for time_id in temporal_ids if judge_timestamp(sample['vertexSet'][time_id][0]['name'])]
                cand_sample["cand_temporal_relation"].append(cands)
            new_data.append(cand_sample)
        print(f"Num of {file} is {len(new_data)}")
        json.dump(new_data, open(os.path.join(save_dir, file[:-5] + '_cand.json'), 'w', encoding='utf-8'), indent=4)
    # process dev/test
    return




if __name__ == '__main__':
    construct_cand_quads("re-docred")