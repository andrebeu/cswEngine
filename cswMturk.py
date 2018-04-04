import re
from numpy import random
import cswEngine

""" NB 
lack of symmetry between question and story nodes:
question nodes are equipped with RFCs at construction
story nodes are all assembled at the beginning and 
when iterating through graph RFC does not get attached to
story node
"""

""" TODO
implement end of story marker

"""

# psiturk snippets

def get_snippet(exp_idx,node,RFC):
	""" wrapper: decides whether story_node or question_node
			returns snippet for appending into code_body str
			and pointer for appending into timeline str
	"""
	if node.type == "story_node":
		snippet,pointer = story_snippet(exp_idx,node,RFC)
		# if node.name == "END": # end of story marker
		# 	snippet = endstory_snippet(exp_idx)
		# 	pointer = "betweenstory_%i," % exp_idx
	elif (node.type == "fillerQ") or (node.type == "transQ"):
		snippet,pointer = question_snippet(exp_idx,node)
	else:
		assert False, 'unknown node.type %s for node.name:' % (node.type,node)
	return snippet,pointer


def story_snippet(exp_idx,story_node,RFC):
	pointer = "s_%i" % exp_idx
	snippet = \
	"""
	var %s = {
		type: 'instructions',
		pages: ["%s"],
		data: { "state": "%s",
						"RFC": "%s",
						"type": "story" }
	} """ % (pointer,story_node.get_filled_state(RFC),story_node.name,str(RFC))
	return snippet,pointer


def question_snippet(exp_idx,question_node):
	
	# list with states of false and true next nodes
	next_state_options = [question_node.get_filled_state()['false_next'], 
												question_node.get_filled_state()['true_next']]
	# randomizing left/right presentation
	idx = [0,1]
	random.shuffle(idx) # inplace shuffle
	# [0,1] -> true on right
	# [1,0] -> true on left 
	left_choice = next_state_options[idx[0]]
	right_choice = next_state_options[idx[1]]
	# record if correct response on right 
	true_on_right = (idx[1] == 1)
	# assemble snippet
	pointer = "q_%i" % exp_idx
	snippet = \
		"""
		var %s = {
			type: "html-keyboard-response",
			stimulus: "<p> 'What happens next?' <p>",
			labels: ["%s", "%s"],
			choices: ["leftarrow", "rightarrow"],""" % (
				pointer,left_choice,right_choice)
		
	snippet += \
		"""
		data: { "true_on_right": "%s",
						"type":"question",
						"qtype":"%s",
						"fromnode": "%s",
						"true_tonode": "%s",
						"false_tonode": "%s",
						"true_RFC":"%s",
						"false_RFC":"%s" }
			} """ % (true_on_right,
								str(question_node.type),
								question_node.fromnode.name,
								question_node.true_tonode.name,
								question_node.false_tonode.name,
								str(question_node.true_RFC),
								str(question_node.false_RFC))
	return snippet,pointer


def endstory_snippet(exp_idx):
	pointer = "betweenstory_%s" % exp_idx
	snippet = \
	"""\n
	var %s = {
		type: 'instructions',
		pages: [' ** ~ NEW STORY ~ ** '],
		data: {"type": "instruction"}
	} \n""" % pointer
	return snippet,pointer


## MAIN

# generates strings for inserting into task script .js file 

def make_mturk_taskscript(path_L,RFC_L):
	""" creates the body of the .js taskscript
	"""
	code_body = ""
	timeline = ""
	exp_idx = 0
	node_idx = 0
	for path,RFC in zip(path_L,RFC_L):
		exp_idx += 1
		for node in path:
			node_idx += 1 
			snippet,pointer = get_snippet(node_idx,node,RFC)
			code_body += snippet
			timeline += "%s," % pointer
	return code_body,timeline


# write taskscript of single subject to disk

def write_mturk_taskscript(code_body,timeline,fpath):
	""" 
	"""
	# read template
	jsexp_template_file = open('exp_template.js')
	jsexp_template_str = jsexp_template_file.read()
	jsexp_template_file.close()
	# fill in codebody to template
	jsexp_str = re.sub("<<insert-code-body-here>>",code_body,jsexp_template_str)
	jsexp_str = re.sub("<<insert-timeline-here>>",timeline,jsexp_str)
	# write taskscript
	jsexp_file_out = open(fpath,'w')
	jsexp_file_out.write(jsexp_str)
	return None


# wrapper loop through N subjects

def write_N_mturk_taskscripts(N,k):
	"""
	"""
	path = "/Users/abeukers/wd/csw/experiments/task_scripts/"
	print('making %i scripts with %i stories to:\n'% (N,k),path)
	for sid in range(N):
		exp = cswEngine.Exp()
		fname = "csw_task-S%i.js" % sid
		path_L,RFC_L = exp.gen_k_paths(k)
		code_body,timeline = make_mturk_taskscript(path_L,RFC_L)
		fpath = path + fname
		write_mturk_taskscript(code_body,timeline,fpath)
		
	return None



