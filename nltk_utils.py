import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()


def tokenize(sentence):
    """
    Splits the string into a list of its meaningful parts
    Ex. "U.S. is worth $100000" -> [U.S., is, worth, $, 100000]
    """
    return nltk.word_tokenize(sentence)


def stem(word):
    """"
    Converts the word into its stem
    Ex. Gone, Going, Goes -> Go
    """
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence, all_words):
    tokenized_sentence = [stem(w) for w in tokenized_sentence]

    bag = np.zeros(len(all_words), dtype=np.float32)
    for i, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[i] = 1.0

    return bag


