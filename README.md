# topic-coherence

## Installation:

- Setup your Django enviroment using venv and requirements.txt
- Create a folder named "ref_corpus" inside Topic_Evaluator/api/ 
- Inside this folder place your pre-processed reference corpus as text files with one article/document per line (no sub-folders)
- Create a settings.py inside Topic_Evaluator/Topic_Evaluator/ using the example (change only DB information)
- Migrate to create your DB and tables:

``
$ python manage.py makemigrations
``


``
$ python manage.py migrate
``