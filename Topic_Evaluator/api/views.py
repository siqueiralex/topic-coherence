from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .word_count import calculate_word_count
from .observed_coherence import topic_coherence, model_coherence
import json

@csrf_exempt
def topic(request):
    if(request.method == 'POST'):

        if('topic' not in request.POST.keys()):
            return JsonResponse({"message": "Bad Request. Expected 'topic' field."}, status=400)


        topic = request.POST['topic']
        if (type(topic) != str or len(topic.split()) < 2):
            return JsonResponse({"message": "Bad Request. Field 'topic' must must be a string with two or more words separated by spaces."}, status=400)

        if('stemmed' in request.POST.keys()):
            stemmed = request.POST['stemmed']
            if(stemmed == 'false'):
                from nltk.stem.snowball import SnowballStemmer
                stemmer = SnowballStemmer("portuguese")
                stemmed_topic = [stemmer.stem(x) for x in topic.split()]
                topic = " ".join(stemmed_topic)
                

        data = calculate_word_count(topic)
        npmi = topic_coherence(topic,"npmi")
        pmi = topic_coherence(topic,"pmi")


        return JsonResponse({"npmi":npmi,"pmi":pmi}, status=200)


def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

@csrf_exempt
def model(request):
    if(request.method == 'POST'):
        if(not is_json(request.body)):
            return JsonResponse({"message": "Bad Request. Expected a json as request body."}, status=400)

        data = json.loads(request.body)
        if('topics' not in data):
            return JsonResponse({"message": "Bad Request. Expected 'topics' field inside the json."}, status=400)

        topics_field = data['topics']
        if ( type(topics_field) != list ):
            return JsonResponse({"message": "Bad Request. Field 'topics' must be a list of strings, each one containing two or more words separated by spaces."}, status=400)

        topics = []
        for topic in topics_field:
            if (type(topic)!= str):
                return JsonResponse({"message": "Bad Request. Field 'topics' must be a list of strings, each one containing two or more words separated by spaces."}, status=400)                
            topics.append(topic)

        topns = [10] # mudar pra [10,5,...] pra pegar media de top n words
        
        if('topns' in data):
            topns = []
            for n in data['topns']:
                topns.append(int(n))
            print("TOP N WORDS:", str(topns))

        data = calculate_word_count(topics)
        npmi = model_coherence(topics,"npmi", topns=topns)  
        pmi = model_coherence(topics,"pmi", topns=topns)
        info = "Calculated mean of top "+"/".join([str(i) for i in topns])+" words for each topic."

        return JsonResponse({"npmi":npmi,"pmi":pmi, "info": info}, status=200)