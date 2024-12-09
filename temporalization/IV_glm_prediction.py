# --coding:utf-8--
import json
import os
# from transformers import AutoTokenizer, AutoModel
from zhipuai import ZhipuAI
import time
import copy

client = ZhipuAI(
    api_key="your_api_key"
)

def chatglmAPI(sys_pmt, user_pmt):
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "system", "content": sys_pmt},
            {"role": "user", "content": user_pmt}
        ],
    )
    
    return response.choices[0].message['content']

def string_scores_process(score_str:str):
    score_str = score_str.strip().strip("[").strip("]").replace(" ", "")
    try:
        scores = [float(score) for score in score_str.split(",") if score != ""]
    except:
        print(f"Error score: {score_str}")
        scores = [0]
    return scores

def construct_temporal_relations(dataset, file):
    start_time = time.time()

    root_dir = os.path.dirname(os.path.realpath(__file__))
    print(root_dir)
    root_dir = os.path.dirname(root_dir)
    data_dir = os.path.join(root_dir, f'data/{dataset}/cand/')
    save_dir = os.path.join(root_dir, f'data/tem-{dataset}/add_rels/glm/')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # files = ['train_rest_cand.json', 'dev_rest_cand.json', 'test_rest_cand.json']
    
    prompt = open("prompt.txt").read().strip()
    error_data = []

    # for file in files:
    raw_data = json.load(open(os.path.join(data_dir, file), 'r', encoding='utf-8'))
    new_data = {}
    rel_count = 0
    for sample in raw_data:
        context = sample["context"]
        new_rels = []
        for sentences in sample["cand_temporal_relation"]:
            sen_group = [sen[0] for sen in sentences]
            labels = [sen[1] for sen in sentences]
            sys_prompt = prompt.format(sen_num=len(sen_group))
            user_prompt = f"context:{context}\n sentences:{str(sen_group)}"
            try:
                ans = chatglmAPI(sys_pmt=sys_prompt, user_pmt=user_prompt)
                print(ans)
                scores = string_scores_process(ans)
                if len(scores) != len(sen_group) or scores.count(max(scores)) > 1:
                    continue
                max_loc, max_score = max(enumerate(scores), key=lambda x:x[1])
                if max_score >= 0.9:
                    new_rels.append(labels[max_loc])
            except Exception as e:
                print(e)

        if len(new_rels) > 0:
            new_data[sample["title"]] = new_rels
            rel_count += len(new_rels)
    
    print(f"Num of temporal relations of {file} is {rel_count}")
    json.dump(new_data, open(os.path.join(save_dir, file.replace("rest_cand", f"add_rels")), 'w', encoding='utf-8'), indent=4)
    print(f"cost_time = {time.time() - start_time}.")

        
if __name__ == '__main__':
    files = ['train_rest_cand.json', 'dev_rest_cand.json', 'test_rest_cand.json']
    for file in files:
        construct_temporal_relations("re-docred", file)