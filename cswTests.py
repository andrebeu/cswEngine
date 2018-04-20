import numpy as np
from collections import Counter

import cswMturk 
import cswEngine 



def node_frequency(k=10000,cond=None):
  """ use to check frequency of node-rfc pairs
  cond is tuple (role,property,value)
  returns the fraction of stories in which each of 
  the node-rfc combinations occur
  """
  exp = cswEngine.Exp()
  node_rfc_counter = Counter()
  node_counter = Counter()
  itr = 0
  while itr < k:
    node_seq,RFC = exp.gen_path()
    if cond:
      if not RFC[cond[0]][cond[1]]==cond[2]: continue
    itr += 1
    for node in node_seq:
      if node.type == 'story_node':
        node_rfc_counter.update([node.name + "__" + str(RFC)])
        node_counter.update([node.name])
  node_counter = {n:np.round(v/k,2) for n,v in node_counter.items()}
  node_rfc_counter = {n:np.round(v/k,2) for n,v in node_rfc_counter.items()}
  return node_counter,node_rfc_counter









