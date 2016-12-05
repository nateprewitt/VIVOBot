VIVOBot
--------------

VIVOBot is a simple python class used to perform basic actions in VIVO.

This will allow you to do things like run inference, upload an ontology file, or perform queries with a cronjob.

You can also use this to perform quick data retrievals out of VIVO for data mashups or complex processing that you
would prefer to do in a programming environment.

##Setup
* Install [VIVO](https://github.com/vivo-project/VIVO)
* Download [VIVOBot](https://github.com/nateprewitt/VIVOBot)
* Create your config file. You can see an example [here](https://github.com/nateprewitt/VIVOBot/blob/master/config/vivobot.cfg.example).
* You're ready to start building!

##Usage

VIVOBot currently has a small number of basic functions in the VIVO UI but has helped automate things that otherwise required manual action.

```python
vb = VIVOBot()
vb.login() # in the future this will likely be a startup default.

# get a list of all persons in our VIVO
query_result = vb.query('SELECT ?person WHERE { ?person a foaf:Person }')

# ensure our SOLR instance is up to date
vb.rebuild_search_index()

# update our ontology definitions will the latest MeSH terms
vb.upload_file('/my_terms/MeshTerms.n3')
```
