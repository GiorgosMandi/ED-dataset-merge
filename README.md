# EventDetectionDataset-Unifier

**EventDetectionDataset-Unifier** is an ETL tool which goal is to transform four well-known Event-Detection datasets into a unified common schema. 
These four datasets are the following:

  - [RAMS](https://nlp.jhu.edu/rams/)
  - [M2E2](https://github.com/limanling/m2e2)
  - [ACE2005](https://catalog.ldc.upenn.edu/LDC2006T06) after being preprocessed by [ace2005-preprocessing](https://github.com/nlpcl-lab/ace2005-preprocessing)
  - Event Extraction Annotated Data from EMM.

You can download the complete dataset [here](https://drive.google.com/file/d/1PoYHTHuUW_SN2IZqbEMnnRmvF6PTAJMJ/view?usp=sharing). By default, 
the dataset will contain the Event Types of ACE.

## Build Instructions
    
First users need to download Standford's CoreNLP model. You can find more information about CoreNLP in its [repository](https://github.com/stanfordnlp/CoreNLP).
To download it you can run:

```shell script
wget -O stanford-corenlp.zip http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip 
unzip stanford-corenlp.zip
```

Then, install requirements using:

    pip install -r requirements.txt


## Execution

To execute  *EventDetectionDataset-Unifier*, users must provide some arguments. There are two types of input arguments, execution arguments 
and dataset related arguments. 

The **Execution Arguments** are the following:

- *-coreNLP path/to/coreNLP_directory*:  Path to the directory of CoreNLP. (Required)
- *-out path/to/output.jsonlines*: Path to the output. **WARNING**:  *EventDetectionDataset-Unifier* opens this file in append mode, so in case it already exists, the results will be appended to its existing content. (Required)
- *-memory X*: The size of heap memory to provide to coreNLP.  X must be an integer.  (Optional, default value is 3)
- *-timeout X*: CoreNLP's timeout processing time.  X must be an integer.  (Optional, default value is 10s)
- *-disableMapping*: Disable mapping the event types of the dataset to the ones of ACE.
- *-h*:        Print instructions.

The **Datasets Arguments** are the following:

- *-ace /path/to/ace.json*: This will instantiate an AceTransformer to transform Ace dataset instances into the common schema. 
                            Reminding that the dataset must have first been pre-processed by  [ace2005-preprocessing](https://github.com/nlpcl-lab/ace2005-preprocessing)
                            
- *-emm /path/to/emm*:      This will instantiate an EmmTransformer to transform EMM dataset instances into the common schema. 
                            The path can point to either a JSON file or to a directory containing multiple JSON files.

- *-rams /path/to/rams*:    This will instantiate a RamsTransformer to transform RAMS dataset instances into the common schema. 

- *-m2e2 /path/to/m2e2*:    This will instantiate an M2e2Transformer to transform M2E2 dataset instances into the common schema.

Users can provide multiple Dataset Arguments in order to transform multiple dataset in a single run. At least one Dataset Arguments must be provided.

Finally, to execute run something like:
 
    $ python -m src.main  -coreNLP path/to/coreNLP_directory -out path/to/output_directory -memory 1 -ace data/Ace.json -emm data/EMM/emm.json 

## Schema

The output will consist of JSONlines of the following schema:

```json

{
    "origin": "M2E2", 
    "id": "M2E2-instance-25-VOA_EN_NW_2016.04.19.3291980_32", 
    "no-of-sentences": 1, 
    "sentences": [
        {
            "start": 0, 
            "end": 25, 
            "text": "In Mississippi , protests greeted a law signed by Governor Phil Bryant allowing business owners in Mississippi to refuse service to same - sex couples"
        }
    ],
    "text": "In Mississippi, protests greeted a law signed by Governor Phil Bryant allowing business owners in Mississippi to refuse service to same-sex couples", 
    "words": ["In", "Mississippi", ",", "protests", "greeted", "a", "law", "signed", "by", "Governor", "Phil", "Bryant", "allowing", "business", "owners", "in", "Mississippi", "to", "refuse", "service", "to", "same", "-", "sex", "couples"], 
    "lemma": ["in", "Mississippi", ",", "protest", "greet", "a", "law", "sign", "by", "governor", "Phil", "Bryant", "allow", "business", "owner", "in", "Mississippi", "to", "refuse", "service", "to", "same", "-", "sex", "couple"], 
    "pos-tags": ["IN", "NNP", ",", "NNS", "VBD", "DT", "NN", "VBN", "IN", "NN", "NNP", "NNP", "VBG", "NN", "NNS", "IN", "NNP", "TO", "VB", "NN", "TO", "JJ", ":", "NN", "NNS"], 
    "ner": ["O", "B-STATE_OR_PROVINCE", "O", "O", "O", "O", "O", "O", "O", "B-TITLE", "B-PERSON", "I-PERSON", "O", "O", "O", "O", "B-STATE_OR_PROVINCE", "O", "O", "O", "O", "O", "O", "O", "O"], 
    "golden-entity-mentions": [
        {
            "entity-id": "M2E2-instance-25-VOA_EN_NW_2016.04.19.3291980_32-entity-0", 
            "start": 24, 
            "end": 25, 
            "text": "couples", 
            "entity-type": "O", 
            "existing-entity-type": "PER"
        }, 
        {
            "entity-id": "M2E2-instance-25-VOA_EN_NW_2016.04.19.3291980_32-entity-1", 
            "start": 9, 
            "end": 10, 
            "text": "Governor", 
            "entity-type": "TITLE", 
            "existing-entity-type": "PER"
        }, 
        {
            "entity-id": "M2E2-instance-25-VOA_EN_NW_2016.04.19.3291980_32-entity-2", 
            "start": 1,
            "end": 2,
            "text": "Mississippi",
            "entity-type": "STATE_OR_PROVINCE",
            "existing-entity-type": "GPE"
        },
        {
            "entity-id": "M2E2-instance-25-VOA_EN_NW_2016.04.19.3291980_32-entity-3", 
            "start": 16, 
            "end": 17, 
            "text": "Mississippi", 
            "entity-type": "STATE_OR_PROVINCE", 
            "existing-entity-type": "GPE"
        },
        {
            "entity-id": "M2E2-instance-25-VOA_EN_NW_2016.04.19.3291980_32-entity-4", 
            "start": 10, 
            "end": 12, 
            "text": "Phil Bryant", 
            "entity-type": "PERSON", 
            "existing-entity-type": "PER"
         }
    ], 
    "golden-event-mentions": [
        {
            "arguments": [
                {
                    "start": 16,
                    "end": 17,
                    "text": "Mississippi",
                    "role": "place",
                    "entity-type": "STATE_OR_PROVINCE",
                    "existing-entity-type": "GPE"
                }
            ], 
            "trigger": 
                {
                    "start": 3,
                    "end": 4, 
                    "text": "protests"
                }, 
             "event-type": "conflict.demonstrate.n/a"}
    ], 
    "penn-treebank": [
        "(ROOT  (S  (PP (IN In)  (NP (NNP Mississippi)))  (, ,)  (NP (NNS protests))  (VP (VBD greeted)  (NP  (NP (DT a) (NN law))  (VP (VBN signed)  (PP (IN by)  (NP  (NP (NN Governor) (NNP Phil) (NNP Bryant))  (VP (VBG allowing)  (NP (NN business) (NNS owners))  (PP (IN in)  (NP (NNP Mississippi)))  (S  (VP (TO to)  (VP (VB refuse)  (NP (NN service))  (PP (TO to)  (NP (JJ same)))  (: -)  (NP (NN sex) (NNS couples)))))))))))))"
    ], 
    "dependency-parsing": [
        ["ROOT/dep=4/gov=-1", "case/dep=0/gov=1", "nmod:in/dep=1/gov=4", "punct/dep=2/gov=4", "nsubj/dep=3/gov=4", "det/dep=5/gov=6", "dobj/dep=6/gov=4", "acl/dep=7/gov=6", "case/dep=8/gov=11", "compound/dep=9/gov=11", "compound/dep=10/gov=11", "nmod:by/dep=11/gov=7", "acl/dep=12/gov=11", "compound/dep=13/gov=14", "dobj/dep=14/gov=12", "nsubj:xsubj/dep=14/gov=18", "case/dep=15/gov=16", "nmod:in/dep=16/gov=12", "mark/dep=17/gov=18", "xcomp/dep=18/gov=12", "dobj/dep=19/gov=18", "case/dep=20/gov=21", "nmod:to/dep=21/gov=18", "punct/dep=22/gov=18", "compound/dep=23/gov=24", "parataxis/dep=24/gov=18"]
    ], 
    "chunks": [
        [["IN", "O"], ["NNP", "B-NP"], [",", "O"], ["NNS", "B-NP"], ["VBD", "O"], ["DT", "B-NP"], ["NN", "I-NP"], ["VBN", "O"], ["IN", "O"], ["NN", "B-NP"], ["NNP", "I-NP"], ["NNP", "I-NP"], ["VBG", "O"], ["NN", "B-NP"], ["NNS", "I-NP"], ["IN", "O"], ["NNP", "B-NP"], ["TO", "O"], ["VB", "O"], ["NN", "B-NP"], ["TO", "O"], ["JJ", "B-NP"], [":", "O"], ["NN", "B-NP"], ["NNS", "I-NP"]]
    ]
}

```
