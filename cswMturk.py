import re
import os
from numpy import random
import cswEngine

""" NB 
lack of symmetry between question and story nodes:
question nodes are equipped with rfcs at construction
story nodes are all assembled at the beginning and 
when iterating through graph rfc does not get attached to
story node
"""


CSW_DIR_PATH = "/Users/abeukers/wd/csw/"

# psiturk snippets

def get_snippet(exp_idx,node,rfc):
	""" wrapper: decides whether story_node or question_node
			returns snippet for appending into code_body str
			and pointer for appending into timeline str
	"""
	if node.type == "story_node":
		snippet,pointer = story_snippet(exp_idx,node,rfc)
	elif (node.type == "fillerQ") or (node.type == "transQ"):
		snippet,pointer = question_snippet(exp_idx,node)
	else:
		assert False, 'unknown node.type %s for node.name:' % (node.type,node)
	return snippet,pointer


def story_snippet(exp_idx,story_node,rfc):
	pointer = "s_%i" % exp_idx
	snippet = \
	"""
	var %s = {
		type: "html-keyboard-response",
		stimulus: "%s",
		labels: ["", ""],
		choices: jsPsych.NO_KEYS,
		trial_duration: MIN_STORY_ITI,
		data: {"type": "instruction"}
	}

	var %s_ = {
		type: "html-keyboard-response",
		stimulus: "%s",
		labels: ["", ""],
		choices: ['space'],
		data: { "state": "%s",
						"rfc": "%s",
						"type": "story" }
	} """ % (
		pointer,story_node.get_filled_sent(rfc),
		pointer,story_node.get_filled_sent(rfc),story_node.name,str(rfc.id))

	pointer += ",s_%i_" % exp_idx

	return snippet,pointer


def question_snippet(exp_idx,qnode):
	
	# from node
	frnode_sent = qnode.frnode.get_filled_sent(qnode.true_rfc)
	# list with states of false and true next nodes
	next_state_options = [qnode.get_filled_sent()['false_next'], 
												qnode.get_filled_sent()['true_next']]
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
		stimulus: "<p> %s <br><br><br> what happens next? <p>",
		labels: ["%s", "%s"],
		choices: jsPsych.NO_KEYS,
		trial_duration: MIN_QUESTION_ITI
	}

	var %s_ = {
		type: "html-keyboard-response",
		stimulus: "<p> %s <br><br><br> what happens next? <p>",
		labels: ["%s", "%s"],
		choices: ["leftarrow", "rightarrow"],""" % (
			pointer,frnode_sent,left_choice,right_choice,
			pointer,frnode_sent,left_choice,right_choice)
	
	pointer += ",q_%i_" % exp_idx

	snippet += \
	"""
		data: { "true_on_right": "%s",
						"type":"question",
						"qtype":"%s",
						"fromnode": "%s",
						"true_tonode": "%s",
						"false_tonode": "%s",
						"true_rfc":"%s",
						"false_rfc":"%s" }
			} """ % (true_on_right,
							str(qnode.type),
							qnode.frnode.name,
							qnode.true_tonode.name,
							qnode.false_tonode.name,
							str(qnode.true_rfc.id),
							str(qnode.false_rfc.id))
	return snippet,pointer


def endstory_snippet(exp_idx):
	pointer = "betweenstory_%s" % exp_idx
	snippet = \
	"""\n
	var %s = {
		type: 'instructions',
		pages: ['<h1 style="color:white; background-color:black"><br><br><br> ** ~ NEW STORY ~ ** <br><br><br><br><br></h1>'],
		data: {"type": "between_story_marker"}
	} \n""" % pointer
	return snippet,pointer


## MAIN

# generates strings for inserting into task script .js file 

def make_mturk_taskscript(path_L,rfc_L):
	""" 
	creates the body of the .js taskscript
	"""
	code_body = ""
	timeline = ""
	exp_idx = 0
	node_idx = 0
	for path,rfc in zip(path_L,rfc_L):
		exp_idx += 1
		for node in path:
			node_idx += 1 
			snippet,pointer = get_snippet(node_idx,node,rfc)
			code_body += snippet
			timeline += "%s," % pointer
		snippet,pointer = endstory_snippet(exp_idx)
		code_body += snippet
		timeline += "%s," % pointer
	return code_body,timeline


# write taskscript of single subject to disk


def write_mturk_taskscript(code_body,timeline,fpath):
	""" 
	"""
	# read template
	jsexp_template_file = open(CSW_DIR_PATH+'experiments/csw_mturk_template/exp_template.js')
	jsexp_template_str = jsexp_template_file.read()
	jsexp_template_file.close()
	# fill in codebody to template
	jsexp_str = re.sub("<<insert-code-body-here>>",code_body,jsexp_template_str)
	jsexp_str = re.sub("<<insert-timeline-here>>",timeline,jsexp_str)
	# write taskscript
	jsexp_file_out = open(fpath,'w')
	jsexp_file_out.write(jsexp_str)
	jsexp_file_out.close()
	return None


# wrapper loop through N subjects

def write_N_mturk_taskscripts(N,k):
	"""
	"""
	from shutil import copy
	path = "/Users/abeukers/wd/csw/experiments/task_scripts/"
	print('making %i scripts with %i stories to:\n'% (N,k),path)
	print('qpr','fillerpr','cond','burnin')
	print(cswEngine.PARAMS)
	for sid in range(N):
		print(sid)
		# csw 
		graph = cswEngine.Graph()
		ont = cswEngine.Ontology()
		exp = cswEngine.Exp(graph,ont)
		path_L,rfc_L = exp.gen_k_paths(k)
		# script
		code_body,timeline = make_mturk_taskscript(path_L,rfc_L)
		fpath = path + "csw_task-S%i.js" % sid
		write_mturk_taskscript(code_body,timeline,fpath)
	copy(path+"csw_task-S0.js","/Users/abeukers/wd/csw/experiments/csw_mturk_template/static/js/task/")
	return None



