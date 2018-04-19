# cswEngine


## objects:
* Exp
* Path
* RFC 
* 


## CURRENT IMPLEMENTATION
Graph and Experiment
Graph has Node objects
Experiment has Question objects

RFC is a dict, RF are dicts


## NEXT STEP

richly filled experiments \
1) work on Node object to make filling smooth \
2) make sure questions are being easily filled


## NOTES

* RFC
want .get_info() returns str with info about the entities in RFC
.query(condition) returns true or false.
currently encoding as a string with the info of role.property.bool

* PR 
node.pr is {subj.viol.true:{nodename:pr,}, subj.viol.false:{nodename:pr,}}
want: pr and RFC interact better for querying 


* NB assymetry:
      str(node)=nodeobj.BEGIN 
  and str(question)=transQ_SHOVE 
  and str(RFC)=subj.bill.vict.olivia


