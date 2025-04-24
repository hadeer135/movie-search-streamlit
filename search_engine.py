# File: search_engine.py

import pandas as pd
import os
import json
from collections import defaultdict

class MovieSearchEngine:
    def __init__(self):
        self.df = pd.read_csv('wiki_movie_plots_deduped.csv')
        self.df.fillna("", inplace=True)
        self.df['processed_plot'] = self.df['Plot'].str.lower()
        
        # Inverted index file path
        self.index_file = 'inverted_index.json'

        if os.path.exists(self.index_file):
            self.inverted_index = self.load_inverted_index()
        else:
            self.inverted_index = self.build_inverted_index()
            self.save_inverted_index()

    def build_inverted_index(self):
        index = defaultdict(set)
        for doc_id, plot in enumerate(self.df['processed_plot']):
            words = plot.split()
            for word in set(words):  # use set to avoid duplicate entries
                index[word].add(doc_id)
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in index.items()}

    def save_inverted_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.inverted_index, f)

    def load_inverted_index(self):
        with open(self.index_file, 'r') as f:
            return json.load(f)

    def boolean_search(self, query, mode='AND'):
        keywords = query.lower().split()
        result_sets = [set(self.inverted_index.get(word, [])) for word in keywords]

        if not result_sets:
            return []

        if mode == 'AND':
            results = set.intersection(*result_sets)
        elif mode == 'OR':
            results = set.union(*result_sets)
        elif mode == 'NOT':
            all_docs = set(range(len(self.df)))
            results = all_docs.difference(set.union(*result_sets))
        else:
            results = set()

        return sorted(results)

    def phrase_search(self, query):
        phrase = query.lower()
        return [idx for idx, plot in enumerate(self.df['processed_plot']) if phrase in plot]

    def biword_search(self, query):
        words = query.lower().split()
        bigrams = [' '.join(pair) for pair in zip(words, words[1:])]
        return [idx for idx, plot in enumerate(self.df['processed_plot']) if all(b in plot for b in bigrams)]

    def get_movie_details(self, doc_id):
        movie = self.df.iloc[doc_id]
        return {
            "title": movie['Title'],
            "original_plot": movie['Plot']
        }
