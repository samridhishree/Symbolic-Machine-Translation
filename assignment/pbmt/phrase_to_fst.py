#Converts a phrases to the WFSTs
import os
import sys
from collections import defaultdict

phrase_txt_file = sys.argv[1]
output_fst_file = sys.argv[2]

#Read the phrases from the phrase file
phrase_file = open(phrase_txt_file, 'r')
phrases = phrase_file.readlines()
output_file = open(output_fst_file, 'w')
print "Number of phrases = ", len(phrases)

eps = '<eps>'
prev_state = 0
next_state = 0
#Dictionary for {state -> {(token:next_state)}}, next_state has the value of len(states).
states = {0:defaultdict(lambda: len(states))}
visited_states = set()
test_state = []

for i in range(len(phrases)):
	phrase = phrases[i]
	phrase = phrase.strip().strip("\n")
	parts = phrase.split("\t")
	print parts
	source_words = parts[0].strip().split()
	target_words = parts[1].strip().split()
	phrase_score = parts[2].strip()
	if i%10000 == 0:
		print "Phrase ", i
		#print "Number of states ", len(states.keys())
	#print "source words = ", source_words
	#print "target words = ", target_words

	#Read the source words
	for word in source_words:
		#Get the next state from the prev_state for the token
		#visited_states.add(prev_state)
		token = word+eps
		next_state = states[prev_state][token]


		if next_state not in states:
			#Add this state to the states list and initialize it to an empty dictionary
			#Write to the output file since this is a new transition
			states[next_state] = defaultdict(lambda: len(states))
			#visited_states.add(next_state)
			#test_state.append(next_state)
			output_file.write('%s %s %s %s\n' % (prev_state, next_state, word, eps))

		prev_state = next_state

	#Read the target words
	for word in target_words:
		#Get the next state from the prev_state for the token
		#visited_states.add(prev_state)
		token = eps+word
		next_state = states[prev_state][token]

		if next_state not in states:
			#Add this state to the states list and initialize it to an empty dictionary
			#Default value for the new entry should be current state length
			states[next_state] = defaultdict(lambda: len(states))
			#test_state.append(next_state)
			#visited_states.add(next_state)
			output_file.write('%s %s %s %s\n' % (prev_state, next_state, eps, word))

		prev_state = next_state

	#Write the last transition <eps>:<eps>/score from last state to state 0
	output_file.write('%s %s %s %s %s\n' % (prev_state, 0, eps, eps, phrase_score))
	prev_state = 0

#Print the loop transitions for </s> <unk> and the starting state
output_file.write('%s %s %s %s\n' % (0, 0, '</s>', '</s>'))
output_file.write('%s %s %s %s\n' % (0, 0, '<unk>', '<unk>'))
output_file.write('0\n')
#print "test_state length = ", len(test_state)
#print "visited_state length = ", len(visited_states)








