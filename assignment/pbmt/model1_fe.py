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
german_word_corpus = []

#Build the word vocabularies
#german_word_corpus.append("NULL")

for sent in german_train:
	sent = sent.strip("\n")
	words = sent.split(" ")
	for word in words:
		german_word_corpus.append(word)

#Remove the duplicate entries
german_word_corpus = list(set(german_word_corpus))
german_vocab_size = len(german_word_corpus)

#Get the parallel sentence pairs
training_sentences = [(ger.strip(), eng.strip()) for (ger, eng) in zip(german_train, english_train)]
trans_f_e = defaultdict(lambda: 1.0/(float)(german_vocab_size))

#Perform EM over the training corpus - P(f,a|e)
def PerformEMGerToEng(training_sentences, epochs):
	print "Performing EM for german to english"
	for i in range(0, epochs):
		print "Epoch number : ", i
		count_f_e = defaultdict(lambda: 0)
		total_e = defaultdict(lambda: 0)

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
					val = (float)(trans_f_e[(ger_word, eng_word)])/(float)(s_total_f[ger_word])
					count_f_e[(ger_word, eng_word)] += val
					total_e[eng_word] += val

		#Estimate Probabilities
		for ger,eng in count_f_e.keys():
			trans_f_e[(ger, eng)] = (float)(count_f_e[(ger, eng)])/(float)(total_e[eng])
	#end epoch-for

#Get the alignments for probabilities p(f|e)
def AlignGerToEng(engSent, gerSent):
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
			temp_result = trans_f_e[(eng, ger)]
			if temp_result > max_val:
				max_val = temp_result
				max_pos = i
		alignment.append((max_pos, j))
	return alignment

#Write the alignments for the data to a file
def WriteAlignmentToFile(trainingData):
	f = open(alignment_file, 'w')
	for (ger_sentence, eng_sentence) in trainingData:
		alignment = []
		alignment = AlignGerToEng(eng_sentence, ger_sentence)
		to_write = ""
		for (e_i,f_j) in alignment:
			to_write += str(e_i) + "-" + str(f_j) + " "
		f.write(to_write + "\n")

#Call the EM training for the training corpus for 10 epochs
print "Number of sentence pairs in the training corpus: ", len(training_sentences)
print "Performing EM over the training sentences"
PerformEMGerToEng(training_sentences, 15)
print "Training complete. Computing Alignments"
WriteAlignmentToFile(training_sentences)


