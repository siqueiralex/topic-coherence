# Topic Coherence Evaluation API

Rest API for semantic coherence evaluation of sets of words (topics). Calculated based on the co-occurrence of word pairs (pmi, npmi) inside a (big and good enough) reference corpus, usually Wikipedia or/and News Articles. 

This project is based on the work developed by Lau, Jey Han [[1]](#1), [Github](https://github.com/jhlau/topic_interpretability)

New features developed here:
- Evaluation available through simple REST API
- Past calculations are stored in database, avoiding recalculations.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You'll nedd `Python 3.7`, `Django`, `MySQL DB` and a good Reference Corpus.

### Installation:

* Setup your virtual enviroment

```sh
user@foo:~$ virtualenv venv -p python3.7 
```
```sh
user@foo:~$ source venv/bin/activate 
```

* Install depedencies

```sh
user@foo:~$ (venv) pip install requirements.txt 
```

* Create the `settings.py` file using the given example (adding DB information)

```
Topic_Evaluator/
  Topic_Evaluator/
    settings-example.py <-- use this one
    settings.py <-- to create this one
```

*  Migrate to create your Database Tables
```sh
user@foo:~$ cd Topic_Evaluator/
user@foo:~$ (venv) python manage.py migrate
```

* Create your Reference Corpus folder

```
Topic_Evaluator/
  api/
    ref_corpus/ <-- create this folder and put your corpus inside it

Important: The reference corpus must be formed by multiple text files 
with one document per line (no sub-folders), for example:

Topic_Evaluator/
  api/
    ref_corpus/
      Wikipedia/
        AA.txt
        AB.txt
        (...)
      NewYorkTimes/
        Jan.txt
        Fev.txt
        (...)

```

* Run your project and test it:
```sh
user@foo:~$ (venv) python manage.py runserver
(...)
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
Now check if your Project is up and running in your Browser.

## Web Browser Interface
<p align="center">
<img style="border: 1px solid"src="https://github.com/siqueiralex/topic-coherence/blob/master/User-Interface-Example.png" alt="User Interface" width="700px">
</p>
This Web interface is intended only for simple demonstration of topic evaluation process. Note that you should use at least two words separated by spaces. Works better if the topic words are well represented in the Reference Corpus.


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

## References
<a id="1">[1]</a> 
Lau, Jey Han e David Newman (2014)
Machine Reading Tea Leaves: Automatically Evaluating Topic Coherence and Topic Model Quality. 
abril 2014. ix, 3, 10, 11, 21, 25,26, 30, 32,
