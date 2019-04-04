import numpy as np
from collections import Counter

import cswMturk 
from cswEngine import *

""" running this script generates a debugging file """
outfile = open('cswTests.out','w') 


# Parameters
outfile.write('\n\n--params--\n\n')
outfile.write('qpr %s\n'%QUESTION_PR) 
outfile.write('filler qpr %s\n'%FILLER_QUESTION_PR) 
outfile.write('cond %s\n'%CONDITIONED) 
outfile.write('burnin %i\n'%NUM_BURNIN)

# CSW objects
graph = Graph()
ont = Ontology()
exp = Exp(graph,ont)




# sample from node transitions

outfile.write('\n\n--conditional node statistics--\n\n')

def write_cond_node_data(node,k=100):
  edges = graph.edge_dict[node.name]
  outfile.write("-nominal: %s\n"%str(edges))
  for cond in edges.keys():
    tonode_counter = Counter()
    rfc = ont.sample_rfc(cond)
    for _ in range(k):
      tonode = graph.sample_tonode(node,rfc)
      tonode_counter.update([tonode.name])
    distr = {n:np.round(c/k,2) for n,c in sorted(tonode_counter.items())}
    outfile.write("-empirical: %s\t"%str(cond))
    outfile.write("%s\n"%str(distr))

def write_avg_node_data(node,k=100):
  edges = graph.edge_dict[node.name]
  tonode_counter = Counter()
  for _ in range(k):
    rfc = ont.sample_rfc()
    tonode = graph.sample_tonode(node,rfc)
    tonode_counter.update([tonode.name])
  distr = {n:np.round(c/k,2) for n,c in sorted(tonode_counter.items())}
  outfile.write("-avg over rfcs: %s\n"%str(distr))

def write_avg_node_visit(node,k=100):
  path_L,rfc_L = exp.gen_k_paths(k)
  node_counter = Counter()
  for path in path_L:
    node_counter.update([n.name for n in path if n.type =='story_node'])
  distr = str({n:np.round(c/k,2) for n,c in sorted(node_counter.items())})
  distr = distr.replace(', ','\n')
  outfile.write("-node visits: \n%s\n"%distr)


for node in graph.node_dict.values():
  print('testing',node)
  if node.name == 'END': continue
  outfile.write('\n%s\n'%node.name)
  write_avg_node_data(node)
  write_cond_node_data(node)
  


outfile.write('\n\n--overall node statistics--\n\n')
write_avg_node_visit(node)



# unfilled
outfile.write('\n\n--unfilled sents from all nodes--\n\n')

for node in graph.node_dict.values():
  outfile.write(node.sent)
  outfile.write('\n')


# filled stories
outfile.write('\n\n--story samples--\n\n')

path_L,rfc_L = exp.gen_k_paths(2)

for path,rfc in zip(path_L,rfc_L):
  for node in path:
    if node.type == 'story_node':
      outfile.write(node.get_filled_sent(rfc))
      outfile.write('\n')


# questions
outfile.write('\n\n--question samples--\n\n')
expq = Exp(graph,ont)
expq.askingQ=True
questionL = []
rfcL = []

for i in range(100):
  path,rfc = expq.gen_path()
  questionL.extend([n for n in path if n.type=='fillerQ' or n.type=='transQ'])
  rfcL.append(rfc)

for rfc,fq in zip(rfcL,questionL):
  fql = str(list(fq.get_filled_sent().values()))
  fql = fql.replace('\n',' ').replace('\', ','\n').replace('", ','\n').replace('<br>','')
  outfile.write(fql)
  outfile.write('\n\n')

outfile.close()



