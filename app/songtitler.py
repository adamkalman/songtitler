from __future__ import division
import nltk
import string
import os
import re
import itertools
from string import maketrans

from collections import Counter
#from nltk.book import *
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
from nltk.collocations import *
from nltk.corpus import brown

lyricsfolder = '/Users/adamkalman/Desktop/mb3/texts'
musicstopwords = ['nah','na','ooh','oh','yeah','yea']
topnwords = 4
stemmer = PorterStemmer()
lyricsdict = {}

def deleteDuplicates(listoflists):
  return list(k for k,_ in itertools.groupby(listoflists))

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    tokens = [word for word in tokens if word != '.'] 
    #stems = stem_tokens(tokens, stemmer) #use this line if stemming
    stems = tokens #use this line if not stemming
    return stems

def titlepicker(inputtext):
  bigram_measures = nltk.collocations.BigramAssocMeasures()
  trigram_measures = nltk.collocations.TrigramAssocMeasures()

  #print filename
  
  for subdir, dirs, files in os.walk(lyricsfolder):
    for file in files:
      file_path = subdir + os.path.sep + file
      if file_path[-4:] == '.txt':
        lyrics = open(file_path, 'r')
        
        no_punctuation = lyrics.read().lower().translate(maketrans('\n,!;()?', '.......'))
        no_punctuation = no_punctuation.replace('.', ' . ')
        no_punctuation = re.sub(r'\s+',r' ', no_punctuation)
        
        lyricsdict[file] = no_punctuation
  
  no_punctuation = inputtext.lower().translate(maketrans('\n,!;()?', '.......'))
  no_punctuation = no_punctuation.replace('.', ' . ')
  no_punctuation = re.sub(r'\s+',r' ', no_punctuation)
  mylyrics = no_punctuation
  lyricsdict['inputtext'] = mylyrics
  bigramfinder = BigramCollocationFinder.from_words(mylyrics.split())
  bigramfinder.apply_word_filter(lambda w: w in stopwords.words('english') or w == '.') #throw away ones with stopwords
  colloc2 = sorted(bigramfinder.nbest(bigram_measures.raw_freq, 2))
  trigramfinder = TrigramCollocationFinder.from_words(mylyrics.split())
  trigramfinder.apply_word_filter(lambda w: w in stopwords.words('english') or w == '.') #throw away ones with stopwords
  colloc3 = sorted(trigramfinder.nbest(trigram_measures.raw_freq, 2))
  
  tfidf = TfidfVectorizer(tokenizer=tokenize)#, stop_words='english')
  tfs = tfidf.fit_transform([lyricsdict.pop('inputtext')]+lyricsdict.values())
  lyricsdict['inputtext'] = mylyrics
  
  feature_names = tfidf.get_feature_names()
  tfidfweights = {}
  for col in tfs.nonzero()[1]:
    tfidfweights[feature_names[col]] = tfs[0, col]
 
  modifiedtfidfweights = {k:(v/5 if k in stopwords.words('english')+musicstopwords else v) for k, v in tfidfweights.items()}
   
  minscore = max(sorted(modifiedtfidfweights.values())[-topnwords],0.01) #weight cutoff for top n words
  topterms = {k:v for (k,v) in modifiedtfidfweights.items() if v >= minscore}
  
  toptermslist = sorted(topterms.items(), key=lambda x: x[1], reverse=True)
  
  phrasescoredict = Counter({})
  phrases = [list(group) for k, group in itertools.groupby(mylyrics.split(), lambda x: x == '.') if not k]
  
  collocsU = [[word.decode() for word in wordlist] for wordlist in colloc2+colloc3]
  ttlist = [[x[0]] for x in toptermslist]
  phrases += ttlist+collocsU

  for phrase in phrases:
    positions = [i for i, word in enumerate(phrase) if word in [x[0] for x in toptermslist]]
    if positions:
      keyphrase = phrase[positions[0]:positions[-1]+1]  
      keyphrasescore = 0
      phraselencoeff = 2**-(len(keyphrase)-3)
      if len(keyphrase) <= 4:
        phraselencoeff = 1
      for word in set(keyphrase):
        if word in modifiedtfidfweights.keys():
          keyphrasescore += modifiedtfidfweights[word]
      phrasescoredict[' '.join(keyphrase)] += phraselencoeff*keyphrasescore 
  
  minscore = sorted(phrasescoredict.values())[-min(4,len(phrasescoredict))] #score cutoff for top 4 phrases
  topphrases = {k:v for (k,v) in phrasescoredict.items() if v >= minscore}
  topphraseslist = sorted(topphrases.items(), key=lambda x: x[1], reverse=True)
  return [x[0] for x in topphraseslist]    

