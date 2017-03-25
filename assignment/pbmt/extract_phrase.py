#Usage python extract_phrase.py <german_train> <english_train> <alignment.txt> <phrase_output.txt>
import os
import sys
import math
from collections import defaultdict

german_train_file = sys.argv[1]
english_train_file = sys.argv[2]
alignment_file = sys.argv[3]
phrase_file = sys.argv[4]
max_phrase_len = int(sys.argv[5])
count_f_e = defaultdict(int)
count_e = defaultdict(int)
#score_f_e = defaultdict(float)
align_file = open(alignment_file, 'r')
alignments = align_file.readlines()

#Function to create the alignment dictionary (eng->[german]) and (ger->[english]) for ith sentence
def CreateAlignments(i):
	sentence_alignments = alignments[i].strip().strip("\n").split(" ")
	e_align_dict = defaultdict(list)
	f_align_dict = defaultdict(list)
	for align_pair in sentence_alignments:
		eng_idx = int(align_pair.split("-")[0])
		ger_idx = int(align_pair.split("-")[1])
		e_align_dict[eng_idx].append(ger_idx)
		f_align_dict[ger_idx].append(eng_idx)
	return e_align_dict, f_align_dict

#Boolean function that returns if a list is quasi-consecutive
def IsQuasiConsecutive(index_list, f_align_dict):
	index_list.sort()
	start = index_list[0]
	for i in range(1, len(index_list)):
		nxt = index_list[i]
		if (nxt != start+1):
			if (len(f_align_dict[nxt]) != 0):
				return False
		start = start+1
	return True

#Update the counts for the phrase pairs and the target phrases
def UpdatePhraseCounts(phrase_list):
	for (e,f) in phrase_list:
		count_f_e[(f,e)] += 1
		count_e[e] += 1
		# score_f_e[(f, e)] = math.log((float)(count_f_e[(f, e)])/(float)(count_e[e]))
		# if score_f_e[(f,e)] != 0.0:
		# 	score_f_e[(f,e)] = -score_f_e[(f,e)]

#Extract phrases for the given sentence pair
def PhraseExtract(eng_sentence, ger_sentence, e_align_dict, f_align_dict):
	#print "in extract phrase"
	eng_words = eng_sentence.split(" ")
	ger_words = ger_sentence.split(" ")
	eng_len = len(eng_words)
	ger_len = len(ger_words)
	BP = set()

	for i1 in range(0, eng_len):
		for i2 in range(i1, eng_len):
			if i2-i1 > max_phrase_len-1:
				continue
			TP = []

			for i in range(i1, i2+1):
				TP.extend(e_align_dict[i])
				#print "i = ", i
			#Remove duplicate entries
			TP = list(set(TP))

			#No target alignments for this substring
			if len(TP) == 0:
				continue

			if(IsQuasiConsecutive(TP, f_align_dict) == True):
				j1 = min(TP)
				j2 = max(TP)

				if j2-j1 > max_phrase_len-1:
					continue

				SP = []
				for j in range(j1, j2+1):
					SP.extend(f_align_dict[j])
				#Remove duplicate entries
				SP = list(set(SP))
				SP.sort()
				#if (set(SP) <= set(range(i1, i2+1))):
				if len(SP) !=0 and min(SP) >= i1 and max(SP) <= i2:
					eng_phrase = " ".join(eng_words[i1:(i2+1)])
					ger_phrase = " ".join(ger_words[j1:(j2+1)])
					BP.add((eng_phrase, ger_phrase))
					while ((j1 > 0) and (len(f_align_dict[j1]) == 0)):
						j_dash = j2
						if j_dash-j1 > max_phrase_len-1:
							continue
						while ((j_dash < ger_len) and (len(f_align_dict[j_dash]) == 0)):
							ger_phrase = " ".join(ger_words[j1:(j_dash+1)])
							BP.add((eng_phrase, ger_phrase))
							j_dash = j_dash + 1
						j1 = j1 - 1
	return list(BP)

german_file = open(german_train_file, "r")
english_file = open(english_train_file, "r")
german_train = german_file.readlines()
english_train = english_file.readlines()
#Get the parallel sentence pairs
training_sentences = [(ger.strip("\n"), eng.strip("\n")) for (ger, eng) in zip(german_train, english_train)]
w = open(phrase_file, 'w')

#Extract phrases and store in a file
for i in range(len(training_sentences)):
	ger_sent, eng_sent = training_sentences[i]
	e_align_dict, f_align_dict = CreateAlignments(i)
	if i%1000 == 0:
		print "Phrase for alignment ", i
	phrases = PhraseExtract(eng_sent, ger_sent, e_align_dict, f_align_dict)
	UpdatePhraseCounts(phrases)

#Write to the file
for ger_phrase, eng_phrase in count_f_e:
	#print('%s\t%s\t%.4f\n' % (ger_phrase, eng_phrase, score_f_e[(ger_phrase, eng_phrase)]))
	score_f_e = math.log((float)(count_f_e[(ger_phrase, eng_phrase)])/(float)(count_e[eng_phrase]))
	if score_f_e != 0.0:
		score_f_e = -score_f_e
	w.write('%s\t%s\t%.4f\n' % (ger_phrase, eng_phrase, score_f_e))












