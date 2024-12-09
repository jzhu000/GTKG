# Tem-DocRED
This repo contains the code used for the paper "Temporal Knowledge Graph Generation Based on Document-level Temporal Relation Extraction with Large Language Models".

## Requirements
+ Python 3.10
+ Python packages
  + openai
  + zhipuai

## Datasets

### Original Re-DocRED
Downloaded [RE-DocRED](https://github.com/tonytan48/Re-DocRED) is located in ``data``. Our proposed dataset also is located in this index.

### Data Generation


**STEP1** \
The ``temporalization/I_gpt_proposal.py`` script combines triples with combination patterns for each document in the original dataset. \
Example to run (``cd temporalization``): 
```
python I_gpt_proposal.py
```

**STEP2** \
The ``temporalization/II_cand_construction.py`` script construct data with prompts for GPT and GLM.\
Example to run (``cd temporalization``): 
```
python II_cand_construction.py
```


**STEP3&4** \
The ``temporalization/III_gpt_prediction.py`` script judge sentenses for each document and provides scores.
This code requires OpenAI's model APIs. Accessing the API requires an API key, which you can obtain by creating an account and going to the official website.\
Example to run (``cd temporalization``): 
```
python III_gpt_prediction.py
```

For the ``temporalization/IV_glm_prediction.py`` script, which requires ZhipuAI's models APIs, which you can obtain by creating an account and going to the official website.\
Example to run (``cd temporalization``): 
```
python IV_glm_prediction.py
```

**STEP5** \
The ``temporalization/V_temporal_doc_construction.py`` construct dataset based on the previous results.\
Example to run (``cd temporalization``): 
```
python V_temporal_doc_construction.py 
```


**STEP6** \
The ``temporalization/VI_LLM_data_proposal.py`` script construct the dataset for LLM-Factory. \
Example to run: 
```
python VI_LLM_data_proposal.py
```


## Fine-tuning LLMs

### Training and Test
The codebase of this repo is extended from [LLaMA Factory](https://github.com/hiyouga/LLaMA-Factory). 
This work provides an framework for fine-tuning LLMs. 
Just use set files in the ``yamls`` to complete the training and test with dataset constructed in ``STEP6``. \
Run below:
```
llamafactory-cli train train.yaml
llamafactory-cli train test.yaml
```

