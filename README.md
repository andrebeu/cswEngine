### This is the first version which found a difference between interleaved and blocked learning. In the current implementation curriculum is controlled by the number of stories within a block. In the next implementation, curriculum will be controlled by the probability of staying versus shifting.


# cswEngine


## CURRENT IMPLEMENTATION
* Objects: Exp, Node, Questions, RFC

* RFC is a dict, RFs are dicts

* Exp has .get_path() which returns a sequence of nodes and an RFC



## NEXT STEP



## NOTES


### current RFC mechanism  
```the RFC file has 
  schema_role_fillers_D, {roles:[fillers] } and 
  filler_properties_D, {filler:{property:value}} 
the get_filler_properties method takes an RFC_str = {"role":"filler"}
  and returns and RFC, which is {"role":filler} = {"role":{"property":"value"}}

make_RFC_bag_full does most of the heavy lifting
it first makes a list of tuples of "role-filler" 
then uses .split('-') method to make a list of RFC_str
then pass these RFC_str to get_filler_properties to make RFC
```


* richly filled

more roles and fillers
roles that alter transition probabilities are consequential, roles that don't are innocuous.

- RFC's will continue to only have two aggressors and one victim 
- now also includes: setting.name, victim.emotion, victim.yell, victim.type, drink1.name, drink2.name, drink3.name, dessert.name

* further ideas 

want .get_info() returns str with info about the entities in RFC
.query(condition) returns true or false.
currently encoding as a string with the info of role.property.bool

node.pr is {subj.viol.true:{nodename:pr,}, subj.viol.false:{nodename:pr,}}
should pr and RFC interact better for querying?


* NB assymetry:
      str(node)=nodeobj.BEGIN 
  and str(question)=transQ_SHOVE 
  and str(RFC)=subj.bill.vict.olivia


