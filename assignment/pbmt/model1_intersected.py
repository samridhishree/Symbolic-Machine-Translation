#! /usr/local/bin/python
import os
import sys
from collections import defaultdict

#Get the training files
german_train_file = sys.argv[1]
english_train_file = sys.argv[2]
alignment_file = sys.argv[3]
german_file = open(german_train_file, "r")
english_file = open(english_train_file, "r")
german_train = german_file.readlines()
english_train = english_file.readlines()
english_word_corpus = []
german_word_corpus = []

#Build the word vocabularies
german_word_corpus.append("NULL")
english_word_corpus.append("NULL")

for sent in german_train:
	sent = sent.strip("\n")
	words = sent.split(" ")
	#print words
	for word in words:
		german_word_corpus.append(word)

for sent in english_train:
	sent = sent.strip("\n")
	words = sent.split(" ")
	for word in words:
		english_word_corpus.append(word)

#Remove the duplicate entries
german_word_corpus = list(set(german_word_corpus))
english_word_corpus = list(set(english_word_corpus))
eng_vocab_size = len(english_word_corpus)
german_vocab_size = len(german_word_corpus)

#Get the parallel sentence pairs
training_sentences = [(ger.strip(), eng.strip()) for (ger, eng) in zip(german_train, english_train)]
trans_e_f = defaultdict(lambda: 1.0/(float)(german_vocab_size))
trans_f_e = defaultdict(lambda: 1.0/(float)(eng_vocab_size))


#Perform EM over the training corpus - P(e,a|f)
def PerformEMEngToGer(training_sentences, epochs):
	print "In EM function"
	count_e_f = defaultdict(lambda: 0)
	total_f = defaultdict(lambda: 0)

	print "Performing EM for english to german"
	for i in range(0, epochs):
		print "Epoch number : ", i

		for (ger_sentence, eng_sentence) in training_sentences:
			eng_words = eng_sentence.split(" ")
			ger_words = ger_sentence.split(" ")
			#ger_words.append("NULL")
			s_total_e = defaultdict(lambda: 0)
			
			#Compute Normalization
			for eng_word in eng_words:
				for ger_word in ger_words:
					s_total_e[eng_word] += trans_e_f[(eng_word, ger_word)]

			#Collect Counts
			for eng_word in eng_words:
				for ger_word in ger_words:
					count_e_f[(eng_word, ger_word)] += (float)(trans_e_f[(eng_word, ger_word)])/(float)(s_total_e[eng_word])
					total_f[ger_word] += (float)(trans_e_f[(eng_word, ger_word)])/(float)(s_total_e[eng_word])

		#Estimate Probabilities
		for eng,ger in count_e_f.keys():
			trans_e_f[(eng, ger)] = (float)(count_e_f[(eng, ger)])/(float)(total_f[ger])
	#end epoch-for

#Perform EM over the training corpus - P(f,a|e)
def PerformEMGerToEng(training_sentences, epochs):
	print "In EM function"
	count_f_e = defaultdict(lambda: 0)
	total_e = defaultdict(lambda: 0)

	print "Performing EM for german to english"
	for i in range(0, epochs):
		print "Epoch number : ", i

		for (ger_sentence, eng_sentence) in training_sentences:
			eng_words = eng_sentence.split(" ")
			ger_words = ger_sentence.split(" ")
			#eng_words.append("NULL")
			s_total_f = defaultdict(lambda: 0)
			
			#Compute Normalization
			for ger_word in ger_words:
				for eng_word in eng_words:
					s_total_f[ger_word] += trans_f_e[(ger_word, eng_word)]

			#Collect Counts
			for ger_word in ger_words:
				for eng_word in eng_words:
					count_f_e[(ger_word, eng_word)] += (float)(trans_f_e[(ger_word, eng_word)])/(float)(s_total_f[ger_word])
					total_e[eng_word] += (float)(trans_f_e[(ger_word, eng_word)])/(float)(s_total_f[ger_word])

		#Estimate Probabilities
		for ger,eng in count_f_e.keys():
			trans_f_e[(ger, eng)] = (float)(count_f_e[(ger, eng)])/(float)(total_e[eng])
	#end epoch-for

#Get the alignments for probabilities p(e|f)
def AlignEngToGer(engSent, gerSent):
	eng_words = engSent.split(" ")
	ger_words = gerSent.split(" ")
	#ger_words.append("NULL")

	alignment = []
	for j in range(0, len(ger_words)):
		ger = ger_words[j]
		max_val = float("-inf")
		max_pos = -1
		for i in range(0, len(eng_words)):
			eng = eng_words[i]
			temp_result = trans_e_f[(eng, ger)]
			if temp_result > max_val:
				max_val = temp_result
				max_pos = i
		alignment.append((max_pos, j))
	return alignment

#Get the alignments for probabilities p(f|e)
def AlignGerToEng(engSent, gerSent):
	eng_words = engSent.split(" ")
	ger_words = gerSent.split(" ")
	#ger_words.append("NULL")

	#For each english word find the max_prob german word
	alignment = []
	for i in range(0, len(eng_words)):
		eng = eng_words[i]
		max_val = float("-inf")
		max_pos = -1
		for j in range(0, len(ger_words)):
			ger = ger_words[j]
			temp_result = trans_f_e[(ger, eng)]
			if temp_result > max_val:
				max_val = temp_result
				max_pos = j
		alignment.append((i, max_pos))
	return alignment

#Write the alignments for the data to a file
def WriteAlignmentToFile(trainingData):
	f = open(alignment_file, 'w')
	for (ger_sentence, eng_sentence) in trainingData:
		alignment_e_f = []
		alignment_f_e = []
		alignment_e_f = AlignEngToGer(eng_sentence, ger_sentence)
		alignment_f_e = AlignGerToEng(eng_sentence, ger_sentence)
		intersected = set(alignment_e_f).intersection(alignment_f_e)
		to_write = ""
		for (e_i,f_j) in intersected:
			to_write += str(e_i) + "-" + str(f_j) + " "
		f.write(to_write + "\n")

#Call the EM training for the training corpus for 10 epochs
print "Number of sentence pairs in the training corpus: ", len(training_sentences)
print "Performing EM english to german"
PerformEMEngToGer(training_sentences, 10)
print "Performing EM german to english"
PerformEMGerToEng(training_sentences, 10)
print "Training complete. Computing Alignments"
WriteAlignmentToFile(training_sentences)


