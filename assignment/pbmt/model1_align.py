#! /usr/local/bin/python
import os
import sys

#Get the training files
german_train_file = sys.argv[1]
english_train_file = sys.argv[2]
alignment_file = sys.argv[3]
german_file = open(german_train_file, "r")
english_file = open(english_train_file, "r")
german_train = german_file.readlines()
english_train = english_file.readlines()
german_word_corpus = []
english_word_corpus = []

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
trans_e_f = dict()

#Initialize the t(e,f) values
def InitializeProbabilities():
	for eng in english_word_corpus:
		for ger in german_word_corpus:
			trans_e_f[(eng, ger)] = 1.0/(float)(german_vocab_size)
	print "Number of pairs = ", len(trans_e_f.keys())

#Perform EM over the training corpus - P(e,a|f)
def PerformEMEngToGer(training_sentences, epochs):
	print "Initializing probabilities"
	InitializeProbabilities()
	count_e_f = dict()
	total_f = dict()

	print "Performing EM for english to german"
	for i in range(0, epochs):
		print "Epoch number : ", i

		#Initialize count_e_f and total_f to zero
		for ger in german_word_corpus:
			total_f[ger] = 0.0
			for eng in english_word_corpus:
				count_e_f[(eng, ger)] = 0.0

		for (ger_sentence, eng_sentence) in training_sentences:
			eng_words = eng_sentence.split(" ")
			ger_words = ger_sentence.split(" ")
			ger_words.append("NULL")
			s_total_e = dict()

			#Compute Normalization
			for eng_word in eng_words:
				s_total_e[eng_word] = 0.0
				for ger_word in ger_words:
					#print "trans_e_f[(" + eng_word + "," + ger_word + ")] ", str(trans_e_f[(eng_word, ger_word)])
					s_total_e[eng_word] += trans_e_f[(eng_word, ger_word)]

			#Collect Counts
			for eng_word in eng_words:
				for ger_word in ger_words:
					count_e_f[(eng_word, ger_word)] += (float)(trans_e_f[(eng_word, ger_word)])/(float)(s_total_e[eng_word])
					total_f[ger_word] += (float)(trans_e_f[(eng_word, ger_word)])/(float)(s_total_e[eng_word])

		#Estimate Probabilities
		for ger in german_word_corpus:
			for eng in english_word_corpus:
				trans_e_f[(eng, ger)] = (float)(count_e_f[(eng, ger)])/(float)(total_f[ger])
	#end epoch-for

#Get the alignments for the sentence pair
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

#Write the alignments for the data to a file
def WriteAlignmentToFile(trainingData):
	f = open(alignment_file, 'w')
	for (ger_sentence, eng_sentence) in trainingData:
		alignment = []
		alignment = AlignEngToGer(eng_sentence, ger_sentence)
		to_write = ""
		for (e_i,f_j) in alignment:
			to_write += str(e_i) + "-" + str(f_j) + " "
		f.write(to_write + "\n")

#Call the EM training for the training corpus for 10 epochs
print "Number of sentence pairs in the training corpus: ", len(training_sentences)
print "Performing EM over the training sentences"
PerformEMEngToGer(training_sentences, 10)
print "Training complete. Computing Alignments"
WriteAlignmentToFile(training_sentences)















