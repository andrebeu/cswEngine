import re
import json
from numpy import random

QUESTION_PR = 0.6
FILLER_QUESTION_PR = 0.3

SCHEMA_FILE_PATH="fight.schema"
STATES_FILE_PATH="fight.states"

""" 

RFC
need to implement RFC object with get_info method which 
returns a string containing the information about the entities in that RFC

PR 
currently node.pr is {subj.viol.true:{nodename:pr,}, subj.viol.false:{nodename:pr,}}

want: pr and RFC interact better for querying 

query method:
RFC.query(condition) returns true or false 
currently encoding as a string with the infor of role.property.bool

NEURAL NET INTEGRATION

assymetry in str(node)=nodeobj.BEGIN 
  and str(question)=transQ_SHOVE 
  and str(RFC)=subj.bill.vict.olivia

"""


class RFC(dict):
  def __init__(self,subject,victim):
    """ RFC implemented as dict object
        each RF is also a dict with arbitrary number of properties
        (e.g. {name:bill,violent:true})
    """
    self['subject'] = subject
    self['victim'] = victim

  def __str__(self):
    """ returns a string that uniquely identifies this RFC 
        e.g. subject-bill_victim-jane 
    """
    return "-".join(["%s.%s" %(k,self[k]['name']) for k in self.keys()]).lower()


def make_RFC_bag():
  Bill_D = {'name':'Bill',
            'violent':True}

  Silvia_D = {'name':'Silvia',
              'violent':True}

  Olivia_D = {'name':'Olivia',
              'violent':False}

  RFC1 = RFC(subject=Olivia_D,victim=Bill_D)
  RFC2 = RFC(subject=Silvia_D,victim=Bill_D)

  RFC_bag = [RFC1,RFC2]
  random.shuffle(RFC_bag)
  return RFC_bag


## helper methods

def read_json(path):
  """ load schema files"""
  with open(path) as f:
    schema_info_L = json.load(f)
  return schema_info_L


## graph constructor 


def assemble_pr(pr_info,nodeD):
  """ given string that encodes trans_prob information in schema file, 
      return a pr object 
      e.g. {subj.viol.true: {tonode1:0.3,tonode2:0.7}, } 
      currently just changes keys of inner dict "tonode1" from string to node object """
  pr = {}
  for cond,cond_dist in pr_info.items():
    pr[cond] = {}
    for tonode_name,probability in cond_dist.items():
      tonode = nodeD[tonode_name]
      pr[cond][tonode] = probability
  return pr

""" eventually* break this into two functions: 
init_nodeD and another function for giving extra structure to the graph
"""

def make_nodeD(schema_fpath=SCHEMA_FILE_PATH,states_fpath=STATES_FILE_PATH):
  """ graph constructor 
      returns nodeD {nodename:node}
  """
  schema_info_D = read_json(schema_fpath)
  node_state_D = read_json(states_fpath)

  ## initialize nodeD with nodes containing name and state
  nodeD = {}
  for node_name in node_state_D.keys():
    node_state = node_state_D[node_name]['state']
    nodeD[node_name] = Node(name=node_name, state=node_state)

  ## include pr in nodes
  for fromnode_name,node_info in schema_info_D.items():
    fromnode = nodeD[fromnode_name]
    fromnode.pr = assemble_pr(node_info['pr'],nodeD)
  return nodeD



## basic objects: nodes, questions


class Node():

  def __init__(self,name,state):
    self.name = name 
    self.state = state
    self.type = "story_node"

  def __str__(self):
    return "NodeObj.%s" % self.name

  __repr__ = __str__

  def check_fillers_differ(self,RFC1,RFC2):
    """ if the node's output sentences look different
        under the two RFCs, return True 
        NB currently, name is only surface property that 
        differs between RFCs. therefore i only check if 
        different names are produced. in the furture RFCs
        should have latent and visible properties and this 
        function would differentiate between them """
    # list of (role,property) tuples in self.state
    roleprop_L = [rp[1:-1].split('.') for rp in re.findall('\[.*?\]',self.state)]
    for rp_tup in roleprop_L:
      role,prop = rp_tup
      if RFC1[role]['name'] != RFC2[role]['name']:
        return True
    return False

  def get_cond_dist(self,RFC):
    """ given an RFC which establishes which conditions are met
        returns a conditional distribution over outgoing edges.
        NB currently only one role.property changes transition probabilities
      """
    if RFC['subject']['violent']:
      cond_dist =  self.pr['subject.violent.true']
    else: 
      cond_dist =  self.pr['subject.violent.false']
    return cond_dist
  
  def get_filled_state(self,RFC):
    """ fills a node's state with given RFC
        returns the resulting string
        NB currently only two fillers
    """
    filled_state = self.state
    filled_state = re.sub('\[subject.name\]',RFC['subject']['name'],filled_state)
    filled_state = re.sub('\[victim.name\]',RFC['victim']['name'],filled_state)
    return filled_state




""" 
two types of questions
implemented with inheritance: b/c of common attributes between qtypes
"""

class Question():
  """ qinfo contains fromnode,tonode,RFC 
      and depending on qtype false_RFC or false_tonode 
  """

  def __init__(self,**qinfo):
    self.fromnode = qinfo['fromnode']
    self.true_tonode = qinfo['true_tonode']
    self.true_RFC = qinfo['true_RFC']
    self.type = "question_node"

  def __str__(self):
    """ qinfo in common to both questions
    """
    qinfo_str = """%s_%s-%s_%s-%s""" % (
      self.type,self.fromnode.name,self.true_tonode.name,
      self.fromnode.name,self.false_tonode.name)
    return qinfo_str
  
  __repr__ = __str__

  def get_filled_state(self):
    """ fills in the true and false tonodes with the appropriate RFCs"""
    true_next = self.true_tonode.get_filled_state(self.true_RFC)
    false_next = self.false_tonode.get_filled_state(self.false_RFC)
    return {'true_next':true_next,'false_next':false_next}


class FillerQ(Question):
  """ has false RFC 
  """
  def __init__(self,**qinfo):
    """ qinfo: {fromnode,tonode,RFC,false_RFC}
    """
    Question.__init__(self,**qinfo)
    self.type = 'fillerQ'
    self.false_RFC = qinfo['false_RFC']
    self.false_tonode = self.true_tonode


class TransitionQ(Question):
  """ has false tonode 
  """
  def __init__(self,**qinfo):
    """ qinfo: {fromnode,tonode,RFC,false_tonode} 
    """
    Question.__init__(self,**qinfo)
    self.type = 'transQ'
    self.false_tonode = qinfo['false_tonode']
    self.false_RFC = self.true_RFC


## experiemnt


class Exp():

  def __init__(self,nodeD=make_nodeD(),RFC_bag=make_RFC_bag()):
    # initialize nodeD, edgeD and RFC
    self.nodes = nodeD # {nodename:node}
    self.RFC_bag = RFC_bag
    self.fixed_RFC = random.choice(self.RFC_bag)
    
  def get_next_tonode(self,fromnode,RFC):
    """ using current RFC uses conditional distribution of fromnode
        to return next tonode """
    cond_dist = fromnode.get_cond_dist(RFC) # {tonode1:prob,tonode2:prob,...}
    next_tonode = random.choice(list(cond_dist.keys()), p=list(cond_dist.values()))
    return next_tonode

  ## main

  def gen_path(self,prQ=QUESTION_PR):
    """ assembles a single path object:
        currently a list of nodes and questions
        path object would consist of collection of nodes and an RFC
        RFC used for collapsing transition probabilities and later filling states
    """
    # sample True RFC
    RFC = random.choice(self.RFC_bag)
    # start at Begin node
    node = self.nodes['BEGIN']
    path_nodes = [node]
    while node.name != "END":
      # get next tonode
      # self.fixed_RFC used for unconditioned transitions
      next_tonode = self.get_next_tonode(node,RFC)
      # w.p. prQ ask question
      if (random.random() < prQ):
        question = self.get_question(node,next_tonode,RFC) # returns Question or None 
        if question:
          path_nodes.append(question)
      # collect node and walk
      node = next_tonode
      path_nodes.append(node)
    return path_nodes,RFC

  """ 
  Question methods 
  """

  def get_question(self,fromnode,tonode,RFC):
    """ wrapper question getter 
        calls either filler or transition question constructor
        both constructors return None question type not available
        returns question object 
    """
    # w.p. attempt to find valid filler question
    if random.random() < FILLER_QUESTION_PR:
      question = self.get_filler_question(fromnode,tonode,RFC) 
    # o.w. attempt to find transition question
    else: 
      question = self.get_transition_question(fromnode,tonode,RFC)
    return question


  def get_filler_question(self,fromnode,tonode,true_RFC):
    """ fillerQ: same tonode, false_RFC
        check if a valid filler question exists 
        by looking for a false RFC which differs from true RFC
        if exits, return question, else return None
    """
    if fromnode.name == "BEGIN": return None
    random.shuffle(self.RFC_bag)
    # look for RFC which produces different filled sentences for tonode
    for false_RFC in self.RFC_bag:
      if tonode.check_fillers_differ(true_RFC,false_RFC):
        return FillerQ(fromnode=fromnode,true_tonode=tonode,
                       true_RFC=true_RFC,false_RFC=false_RFC)
    return None
    

  def get_transition_question(self,fromnode,true_tonode,true_RFC):
    """ transitionQ: false_tonode, same RFC
        check if valid transition question exists
        by looking for false next tonode that differs from true tonode
        if exists return question, else None
    """
    temp_cond = list(fromnode.pr.keys())[0]
    tonode_L = list(fromnode.pr[temp_cond].keys())
    tonode_L.remove(true_tonode)
    if len(tonode_L) == 0: 
      question = None
    else: 
      false_tonode = random.choice(tonode_L)
      question = TransitionQ(fromnode=fromnode,true_tonode=true_tonode,
                              true_RFC=true_RFC,false_tonode=false_tonode)
    return question
  

  # wrapper 

  def gen_k_paths(self,k):
    RFC_L = []
    path_L = []
    for i in range(k):
      path,RFC = self.gen_path()
      path_L.append(path)
      RFC_L.append(RFC)
    return path_L,RFC_L

