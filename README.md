# topic-coherence

## Installation:

- Setup your Django enviroment using venv and requirements.txt
- Create a folder named "ref_corpus" inside Topic_Evaluator/api/ 
- Inside this folder place your pre-processed reference corpus as text files with one article/document per line (no sub-folders)
- Create a settings.py inside Topic_Evaluator/Topic_Evaluator/ using the example (change only DB information)
- Migrate to create your DB and tables:

```console
user@foo:~$ python manage.py makemigrations
```

```console
user@foo:~$ python manage.py migrate
```


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
