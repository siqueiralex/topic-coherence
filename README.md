# Topic Coherence Evaluation API

## Installation:

#### Setup your virtual enviroment (recommended python version=3.7)

```sh
user@foo:~$ virtualenv venv -p python3.7 
```
```sh
user@foo:~$ source venv/bin/activate 
```

#### Install depedencies

```sh
user@foo:~$ (venv) pip install requirements.txt 
```

#### Create `settings.py` file using the given example (adding DB information)

```
Topic_Evaluator/
  Topic_Evaluator/
    settings-example.py <-- use this one
    settings.py <-- to create this one
```

#### Migrate to create your Database Tables:
* (inside Topic_Evaluator folder)
```sh
user@foo:~$ python manage.py migrate
```

#### Create your Reference Corpus folder

```
Topic_Evaluator/
  api/
    ref_corpus/ <-- create this folder and put your corpus inside it
```

- Obs: The reference corpus must be formed by multiple text files with one document per line (no sub-folders)


## API end-points:

### /api/topic/ (POST): 

Request body:
- topic (string, required): space separated topic words
- stemmed (boolean, optional): True if topic words are already stemmed. Default: True

Response:
- pmi: mean of the Pointwise Mutual Information of each pair of topic words
- npmi: mean of the Normalized Pointwise Mutual Information of each pair of topic words

### /api/model/ (POST): 

Expect as request body a json containing one single field named "topics" consisting of a list of strings. Example:

```js
{
    topics: ["first topic", "second topic"]
}
```

Response:
- pmi: PMI results for each topic followed by mean and median of entire model. 
- npmi: NPMI results for each topic followed by mean and median of entire model.
  
Example:

```js
{
    "npmi": {
        "first topic": 0.03744432236391448,
        "secon topic": 0.09581050534215818,
        "mean": 0.12076177801136062,
        "median": 0.10742810941196021
    },
    "pmi": {
        "first topic": 0.16460474798134597,
        "second topic": 0.37554670802735235,
        "mean": 0.466311314109751,
        "median": 0.39846612997353675
    }
}
```
