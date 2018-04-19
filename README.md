# cswEngine


## CURRENT IMPLEMENTATION
* Objects: Exp, Node, Questions, RFC

RFC is a dict, RFs are dicts

Exp has .get_path() which returns a sequence of nodes and an RFC



## NEXT STEP

richly filled experiments 
* improve RFC generation
	- RFC's will continue to only have two aggressors and one victim 
	- now also includes: setting.name, victim.emotion, victim.yell, victim.type, drink1.name, drink2.name, drink3.name, dessert.name
* work on Node object to automate filling 
* make sure questions are being appropriately filled


## NOTES

* RFC
now there are only two fillers victim and aggressor 
want richly filled

```
richly filled: more roles and fillers
roles that alter transition probabilities are consequential, roles that don't are innocuous.

```

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


