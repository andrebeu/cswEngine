import re
import json
from numpy import random
import itertools

QUESTION_PR = 0.6
FILLER_QUESTION_PR = 0.15
CONDITIONED = False
NUM_BURNIN = 5

# see experiment for more options
SCH_FPATH="csw_condloc.sch"
RFC_FPATH='csw.rfc'

PARAMS = [QUESTION_PR,FILLER_QUESTION_PR,CONDITIONED,NUM_BURNIN,SCH_FPATH,RFC_FPATH]

""" NOTES
  
how does learning regime interact with structure of graph to be learned? blocked-interleaved continuum

features of current paradigm that could make generative structure more complex: 
	higher filler complexity, multistep dependence, multiple conditioning factors, 
	wider layers, independent tracks, 

currently there is a fine distinction between 'edge' and 'edges'.
  edges = {cond:edge,cond:edge}
  edge = {tonode1:pr,tonode2:pr}

---

- immediate next: run N=3 on exp1
launch N=3 to check data is being recorded
launch N=27 analyze learning
conditioning experiment
launch N=3 to check data is being recorded
launch N=27 analyze learning
change schema to subj and loc cond
launch N=3 to check data is being recorded
launch N=27 analyze learning

- next: code up blocking

---


MURI deadline 19 aug (~ 3 weeks)

exp1: unconditioned
exp2: conditioned on location only. 
exp3: cond on subj and loc
exp4: blocking


block versus interleaved functionality
integrate human-networks

"""




### helper methods


def read_json(path):
  """ load schema files"""
  with open(path) as f:
    schema_info_L = json.load(f)
  return schema_info_L


def get_all_edge_conditions(schfile_dict):
  """ returns a set of all conditioning factors in a schema file
  ['loc.latent.true','loc.latent.false',...]
  currently used in construction of unconditioned graphs

  """
  all_conditions = set()
  for node_info in schfile_dict.values():
    all_conditions.update(node_info['edge'].keys())
  return list(all_conditions)


### RFC and ONT


class RFC(dict):

  def __init__(self,rfc_dict):
    """ this class increases the functionality of RFCs
    rfc.dict is {role:filler,...} 
    filler is dict {property:value,...}
    e.g. {subject:{name:bill,...},...}
    """
    self._dict = rfc_dict
    self.id = self.get_id()
  
  def __getitem__(self,key):
    return self._dict[key]

  def __str__(self):
    return str(self._dict)

  __repr__ = __str__ 


  def get_id(self):
    """ 
    returns a string that identifies the statistics of this RFC
    currently subject and location change statistics of graphs,
    so RFC id is "subject-subj_location-loc"
    used to keep track of rfcs in .js mturk script
    """
    rfc_id = "subject-%s_location-%s" %(
      self['subject']['name'],self['location']['name'].split()[0])
    return rfc_id

  def assert_cond_met(self,cond):
    """ 
    given a cond "role.property.value" e.g. "subject.latent.true"
    returns bool indicating if condition is met in this rfc
    currently only checked with bool values 
    extend this 
    """
    if cond=='uncond':
      return True
    role,prop,value = cond.split('.')
    # NB value in RFC has bool type, whereas in cond has string type
    if value.lower() == 'true': 
      value = True
    elif value.lower() == 'false': 
      value = False
    cond_met = self[role][prop] == value
    return cond_met

  def assert_roles_differ(self,other_rfc,role):
    """
    given a role, check if self and other rfc have same value for that role
    """
    other_role = other_rfc[role]
    self_role = self[role]
    return other_role != self_role



class Ontology(list):

  def __init__(self,full=True):
    if full:
      self._list = self.get_full_rfcbag()
      self._name = 'full'
  
  def __str__(self):
    return self._name + 'OntObj'

  __repr__ = __str__

  def __getitem__(self,key):
    """ implements self[key] """
    return self._list[key]

  def get_full_rfcbag(self,rfc_fpath=RFC_FPATH):
    """ returns a list of rfcs:
    using itertools.product makes an rfcbag with 
    every possible combination of fillers for available roles"""
    rfcfile_dict = read_json(rfc_fpath)
    roles = [*rfcfile_dict.keys()]
    filler_product = itertools.product(*rfcfile_dict.values())
    rfcbag = []
    for fillers in filler_product:
      rfc = RFC({x:y for x,y in zip(roles,fillers)})
      rfcbag.append(rfc)
    return rfcbag

  def sample_rfc(self,cond=None):
    """ samples RFC from ontology 
    if condition is specified, samples from subset of ontology
      that satisfies condition
    if no condition is specified, samples from full ontology
      required because np.random.choice(ont) does not work 
      due to custom class implementation of list
    """
    # initial sample from ontology
    random_rfc = random.choice(self._list) 
    if cond:
      while not random_rfc.assert_cond_met(cond):
        random_rfc = random.choice(self._list)
    return random_rfc
    


### GRAPH



class Graph():


  def __init__(self,schfile_path=SCH_FPATH):
    self.sch_fpath = schfile_path
    self.schfile_dict = read_json(schfile_path)
    self.conditioned = CONDITIONED
    if not self.conditioned:
      self.random_condition = random.choice(get_all_edge_conditions(self.schfile_dict))
    # initialize_nodes
    self.node_dict = {} # {node.name:nodeObj}
    self.initialize_nodes()
    # initialize edges
    self.edge_dict = {} # {frnode.name:{tonode.name:pr}}
    self.initialize_edges()

  def __getitem__(self,key):
    return self.node_dict[key]


  def initialize_nodes(self):
    """ initialize graph with {nodename:nodeobj}
    """
    for node_name,node_info in self.schfile_dict.items():
      node_sent = node_info['sent']
      self.node_dict[node_name] = Node(name=node_name, sent=node_sent)
    return None

  def initialize_edges(self):
    """ edges are placed in edge_dict
    """
    assert len(self.node_dict), 'node_dict must be initialized first'
    for node in self.node_dict.values():
      if node.name == 'END': continue
      self.edge_dict[node.name] = self.assemble_edge(node)
    return None

  def assemble_edge(self,node):
    """ edges is a dict of {cond:edge}, an edge is a dict of {tonode:pr}
    currently just changes keys of inner dict from string "tonode1" to node object
    given edge info {"cond": {"tonode1": 0.8, "tonode2": 0.2},} from sch file
    return an edge object. e.g. {"cond1": {tonode1:0.3,tonode2:0.7}, "cond2": ...} 
    """
    edge = {}
    edge_info = self.schfile_dict[node.name]['edge'] # {"cond": {"tonode1": 0.8, "tonode2": 0.2},}
    # conditioned
    if self.conditioned:
      for cond,cond_dist in edge_info.items():
        edge[cond] = {}
        for tonode_name,probability in cond_dist.items():
          tonode = self.node_dict[tonode_name]
          edge[cond][tonode] = probability
    # unconditioned
    else:
      edge['uncond'] = {}
      cond_dist = edge_info[self.random_condition]
      for tonode_name,probability in cond_dist.items():
          tonode = self.node_dict[tonode_name]
          edge['uncond'][tonode] = probability
    return edge

  def get_edge(self,frnode,rfc):
    """ 
    first checks if uncond, returns edge
    if conditioned, given an rfc, which establishes which conditions are met,
    returns an edge, i.e. a conditional distribution {tonode1:pr,tonode2:pr,...}
    """
    edges = self.edge_dict[frnode.name]
    # check if uncond
    if self.conditioned:
      # look for first condition met
      for cond in edges.keys():
        if rfc.assert_cond_met(cond):
          edge = edges[cond] 
          break
      else:
        assert False,'Failed to find edge. No conditions in edge met.'
    else:
      assert len(edges) == 1, 'assuming unconditioned but found more than one condition'
      edge = edges['uncond'] 
    return edge

  def sample_tonode(self,frnode,rfc):
    """  
    """
    # check what conditioning factor is met by given rfc
    # e.g. "subject.latent.false" 
    # draw next tonode from corresponding edge
    cond_dist = self.get_edge(frnode,rfc) # {tonode1:prob,tonode2:prob,...}
    next_tonode_L = list(cond_dist.keys())
    next_tonode_pr = list(cond_dist.values())
    next_tonode = random.choice(next_tonode_L,p=next_tonode_pr)
    return next_tonode


### NODE


class Node():

  def __init__(self,name,sent):
    self.name = name 
    self.sent = sent
    self.type = "story_node"
    self.edges = None # {cond:{tonode:pr}}, assigned at graph consutrction

  def __str__(self):
    return "NodeObj.%s" % self.name

  __repr__ = __str__


  def get_filled_sent(self,rfc):
    """ fills a node's sent with given rfc
        returns the resulting string
    """
    filled_sent = self.sent
    role_property_L = re.findall("\[.*?\]",filled_sent)
    for rp in role_property_L:
      r,p = rp[1:-1].split('.')
      filled_sent = re.sub("\\"+rp,rfc[r][p],filled_sent)
    return filled_sent

  def assert_sents_differ(self,rfc1,rfc2):
    """ 
    if the node's output sentences have different 
    sentences under the two rfcs, return True
    """
    return self.get_filled_sent(rfc1) != self.get_filled_sent(rfc2)



### QUESTIONS


class Question():
  """ qinfo contains frnode,tonode,rfc 
      and depending on qtype false_rfc or false_tonode 
  """

  def __init__(self,**qinfo):
    self.frnode = qinfo['frnode']
    self.true_tonode = qinfo['true_tonode']
    self.true_rfc = qinfo['true_rfc']
    self.type = "question_node"

  def __str__(self):
    """ qinfo in common to both questions
    """
    qinfo_str = """%s_%s-%s_%s-%s""" % (
      self.type,self.frnode.name,self.true_tonode.name,
      self.frnode.name,self.false_tonode.name)
    return qinfo_str
  
  __repr__ = __str__

  def get_filled_sent(self):
    """ fills in the true and false tonodes with the appropriate rfcs"""
    true_next = self.true_tonode.get_filled_sent(self.true_rfc)
    false_next = self.false_tonode.get_filled_sent(self.false_rfc)
    return {'true_next':true_next,'false_next':false_next}

class FillerQ(Question):
  """ has false rfc 
  """
  def __init__(self,**qinfo):
    """ qinfo: {frnode,tonode,rfc,false_rfc}
    """
    Question.__init__(self,**qinfo)
    self.type = 'fillerQ'
    self.false_rfc = qinfo['false_rfc']
    self.false_tonode = self.true_tonode

class TransitionQ(Question):
  """ has false tonode 
  """
  def __init__(self,**qinfo):
    """ qinfo: {frnode,tonode,rfc,false_tonode} 
    """
    Question.__init__(self,**qinfo)
    self.type = 'transQ'
    self.false_tonode = qinfo['false_tonode']
    self.false_rfc = self.true_rfc



### EXPERIMENT


class Exp():
  def __init__(self,graph,ont):
    self.graph = graph # {nodename:node}
    self.ont = ont
    self.askingQ = False # used for burnin period

  ## main

  def gen_path(self,cond=None,qpr=QUESTION_PR):
    """ assembles a path [node,question,]
    """
    # sample filling rfc from ontology 
    rfc = self.ont.sample_rfc(cond)
    # start at Begin node
    frnode = self.graph.node_dict['BEGIN']
    path = [frnode]
    while frnode.name != "END":
      # draw next tonode
      next_tonode = self.graph.sample_tonode(frnode,rfc) 
      # w.p. qpr ask question
      if (random.random() < qpr) and self.askingQ:
        question = self.get_question(frnode,next_tonode,rfc) # returns Question or None 
        if question:
          path.append(question)
      # collect node and walk
      frnode = next_tonode
      path.append(frnode)
    return path,rfc


  # Question methods 

  def get_question(self,frnode,tonode,rfc):
    """ wrapper question getter 
    calls either filler or transition question constructor
    both constructors return None when question type not available
    otherwise returns question object 
    """
    # w.p. attempt to find valid filler question
    if random.random() < FILLER_QUESTION_PR:
      question = self.get_filler_question(frnode,tonode,rfc) 
    # o.w. attempt to find transition question
    else: 
      question = self.get_transition_question(frnode,tonode,rfc)
    return question

  def get_filler_question(self,frnode,tonode,true_rfc):
    """ fillerQ: same tonode, false_rfc (different subject)
    check if a valid filler question exists 
    by looking for a false rfc which 
    gives a different sentence and which has a different subject
    if exits, return question, else return None
    """
    if frnode.name == "BEGIN": 
      return None
    random.shuffle(self.ont._list)
    # look for rfc which produces sentences filled with different subjects
    for false_rfc in self.ont._list:

      if tonode.assert_sents_differ(true_rfc,false_rfc)\
      and true_rfc.assert_roles_differ(false_rfc,'subject'):
        return FillerQ(frnode=frnode,true_tonode=tonode,
                       true_rfc=true_rfc,false_rfc=false_rfc)
    return None

  def get_transition_question(self,frnode,true_tonode,true_rfc):
    """ transitionQ: false_tonode, same rfc
    check if valid transition question exists
    by looking for false_tonode that differs from true tonode
    if exists return question, else None
    """
    edge = self.graph.get_edge(frnode,true_rfc) # {tonode1:pr,tonode2:pr,}
    tonode_L = list(edge.keys()) 
    tonode_L.remove(true_tonode)
    if len(tonode_L) == 0: 
      question = None
    else: 
      false_tonode = random.choice(tonode_L)
      question = TransitionQ(
                  frnode=frnode,true_tonode=true_tonode,
                  true_rfc=true_rfc,false_tonode=false_tonode)
    return question

  # wrapper: controls blocking

  def gen_k_paths(self,num_paths,cond_L=[None]):
    """ cond controls ont-blocking, set to none for no blocking
    """
    self.askingQ = False 
    path_L,rfc_L = [],[]

    for path_num in range(num_paths):
      # burnin
      if path_num == NUM_BURNIN: 
        self.askingQ = True
      # if blocking
      cond = None
      # generate path and moveon
      path,rfc = self.gen_path(cond) # for no blocking set cond=None
      path_L.append(path)
      rfc_L.append(rfc)
    return path_L,rfc_L












