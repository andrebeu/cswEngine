import re
import json
from numpy import random
import itertools

QUESTION_PR = 0.6
FILLER_QUESTION_PR = 0.3

SCHEMA_FILE_PATH="fight.schema"
STATES_FILE_PATH="fight.states"
RFC_FILE_PATH='fight.rfc'


""" 
- NEXT STEP: richly filled experiments


"""


### helper methods

def read_json(path):
  """ load schema files"""
  with open(path) as f:
    schema_info_L = json.load(f)
  return schema_info_L


### RFC initialization

  def sample_fillers(schema_role_fillers_D):
    """ unused - gets a random RFC_str
    given a dict with roles that must be filled by this schema
    and the fillers that could fill that role, return a dict of which
    filler will fill each role. e.g: 
    given schema_role_fillers_D (dict of "role": ["available fillers"])
    returns RFC_str {"role": "filler"}
    """
    RFC_str = {}
    for role,available_fillers in schema_role_fillers_D.items():
      RFC_str[role] = random.choice(available_fillers)
    return RFC_str

  def get_filler_properties(RFC_str,filler_properties_D):
    """ replaces "filler" for {property:value} in RFC_str to make RFC:
    given RFC_str {"role": "filler"} and filler_property_D {"filler":"property_D"}
    returns RFC object {role: {"filler":"proerty"} }
    """
    RFC_dict = {}
    for role,filler in RFC_str.items():
      property_D = filler_properties_D[filler]
      RFC_dict[role] = property_D
    return RFC(**RFC_dict)


class RFC(dict):
  def __init__(self,subject,victim,setting,
                drink1,drink2,drink3,dessert):
    """ RFC implemented as dict object
        each RF is also a dict with arbitrary number of properties
        (e.g. {name:bill,violent:true})
    """
    self['subject'] = subject
    self['victim'] = victim
    self['setting'] = setting
    self['drink1'] = drink1
    self['drink2'] = drink2
    self['drink3'] = drink3
    self['dessert'] = dessert

  # def __str__(self):
  #   """ returns a string that uniquely identifies this RFC 
  #       i think this is used to keep track of RFCs in experiment
  #       e.g. subject-bill_victim-jane 
  #   """
  #   return "-".join(["%s.%s" %(k,self[k]['name']) for k in self.keys()]).lower()


  def make_RFC_bag_full(schema_role_fillers_D,filler_properties_D):
    """ makes every possible RFC
    role_filler_str_L: [["role1-filler1","role1-filler2"],["role2-filler1","role2-filler2"]...]
    all_role_fillers: [("role1-filler1","role2-filler1"),("role1-filler2","role2-filler2")]
    RFC_str: {'role':'filler',}
    which I can pass to get_filler_properties, 
    """
    # 1 make_role_filler_str_L
    role_filler_str_L = []
    for role,filler_L in schema_role_fillers_D.items():
      role_L = []
      for filler in filler_L:
        role_filler_str = "%s-%s"%(role,filler)
        role_L.append(role_filler_str)
      role_filler_str_L.append(role_L)
    # 2 all_role_filers
    all_RFC_tups = list(itertools.product(*role_filler_str_L))
    # 3 RFC_str
    RFC_bag_full = []
    for RFC_str_tup in all_RFC_tups:
      RFC_str = {rf_str.split('-')[0]:rf_str.split('-')[1] for rf_str in RFC_str_tup}
      RFC = get_filler_properties(RFC_str,filler_properties_D) 
      RFC_bag_full.append(RFC)
    return RFC_bag_full


  def get_RFC_bag(require,RFC_FILE_PATH=RFC_FILE_PATH):
    """makes a bag of RFCs 
    given path to roles file, where role-filler information is stored
    and the requirements that need to be met by this bag
    """
    schema_role_fillers_D = read_json(RFC_FILE_PATH)['schema_role_fillers']
    filler_properties_D = read_json(RFC_FILE_PATH)['filler_properties']
    RFC_bag_full = make_RFC_bag_full(schema_role_fillers_D,filler_properties_D)
    random.shuffle(RFC_bag_full)
    if require == 'richly filled':
      # full combinatorials
      RFC_bag = RFC_bag_full
    elif require == 'subject and victim':
      # two subjects and two victims
      RFC_bag = get_subj_vict_bag(RFC_bag_full)
    elif require == 'poorly filled':
      # two subjects one victim
      RFC_bag = get_poor_filled_bag(RFC_bag_full)
    else:
      assert False, "requirement not supported: richly filled, poorly filled, subject and victim"
    random.shuffle(RFC_bag)
    return RFC_bag

  def get_subj_vict_bag(RFC_bag_full):
    """ bag with two subjects two victims
    """
    RFC_bag = []
    vict_names = ['Bill','Silvia']
    subj_names = ['Adam','Olivia']
    random.shuffle(subj_names)

    for i,j in set(itertools.permutations([0,0,1,1],2)):
      for RFC in RFC_bag_full:
        if RFC['subject']['name'] == subj_names[i]: 
            if RFC['victim']['name'] == vict_names[j]:
              RFC_bag.append(RFC)
              break
    return RFC_bag

  def get_poor_filled_bag(RFC_bag_full):
    """ bag with two subjects, same victim
    """
    RFC_bag = []
    vict_names = ['Bill','Silvia']
    subj_names = ['Adam','Olivia']
    random.shuffle(subj_names)

    for i in [0,1]:
      for RFC in RFC_bag_full:
        if RFC['subject']['name'] == subj_names[0]: 
            if RFC['victim']['name'] == vict_names[i]:
              RFC_bag.append(RFC)
              break
    return RFC_bag



### GRAPH


class Node():

  def __init__(self,name,state):
    self.name = name 
    self.state = state
    self.type = "story_node"

  def __str__(self):
    return "NodeObj.%s" % self.name

  __repr__ = __str__

  """ use node.get_filled_state(RFC) here """
  def check_filled_states_differ(self,RFC1,RFC2):
    """ if the node's output sentences look different
        under the two RFCs, return True 
        NB currently, name is only surface property that 
        differs between RFCs. therefore i only check if 
        different names are produced. in the furture RFCs
        should have latent and visible properties and this 
        function would differentiate between them """
    # list of (role,property) tuples in self.state
    return self.get_filled_state(RFC1) == self.get_filled_state(RFC2)

    # roleprop_L = [rp[1:-1].split('.') for rp in re.findall('\[.*?\]',self.state)]
    # for rp_tup in roleprop_L:
    #   role,prop = rp_tup
    #   if RFC1[role]['name'] != RFC2[role]['name']:
    #     return True
    # return False

  def get_cond_dist(self,RFC):
    """ given an RFC, which establishes which conditions are met,
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
    role_property_L = re.findall("\[.*?\]",filled_state)
    for rp in role_property_L:
      r,p = rp[1:-1].split('.')
      filled_state = re.sub("\\"+rp,RFC[r][p],filled_state)
    return filled_state


## graph constructing: graph is just a dict of nodes

  def assemble_pr(pr_info,nodeD):
    """ given string that encodes trans_prob information in schema file, 
        return a pr object. e.g. {subj.viol.true: {tonode1:0.3,tonode2:0.7}, } 
        currently just changes keys of inner dict from string "tonode1" to node object """
    pr = {}
    for cond,cond_dist in pr_info.items():
      pr[cond] = {}
      for tonode_name,probability in cond_dist.items():
        tonode = nodeD[tonode_name]
        pr[cond][tonode] = probability
    return pr


  def make_nodeD(schema_fpath=SCHEMA_FILE_PATH,states_fpath=STATES_FILE_PATH):
    """ graph constructor 
      returns nodeD {nodename:node}

        break this into two functions?
      init_nodeD and another function for giving extra structure to the graph
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



### EXPERIMENT


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

  def __init__(self,nodeD=make_nodeD(),RFC_bag=None):
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
    """ assembles a single path object: sequence of nodes and questions
        RFC used for collapsing transition probabilities and later filling states
    """
    # sample True RFC
    RFC = random.choice(self.RFC_bag)
    # start at Begin node
    frnode = self.nodes['BEGIN']
    node_seq = [frnode]
    while frnode.name != "END":
      # get next tonode
      # self.fixed_RFC used for unconditioned transitions
      next_tonode = self.get_next_tonode(frnode,RFC)
      # w.p. prQ ask question
      if (random.random() < prQ):
        question = self.get_question(frnode,next_tonode,RFC) # returns Question or None 
        if question:
          node_seq.append(question)
      # collect node and walk
      frnode = next_tonode
      node_seq.append(frnode)
    return node_seq,RFC

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
      if tonode.check_filled_states_differ(true_RFC,false_RFC):
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












