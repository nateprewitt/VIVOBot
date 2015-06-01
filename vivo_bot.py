import requests
import json
import sys
import urllib
import logging

class VIVOBot(object):

    """ VIVOBot is a simple class to interact with various functionality in
        the vivo siteAdmin console via http requests.
    """
    def __init__(self, filename="config/vivobot.cfg", debug=2):

        self.configfile = filename
        self.set_debug(debug)
        vardict = self.ingest_config()
        self.server = vardict.get('server',"")
        self.cookies = self.login(vardict.get('uname'), vardict.get('pass'))
        
    def ingest_config(self):

        """ Opens configuration file and loads contents as JSON """
        try:
            with open(self.configfile, 'rb') as f:
                return json.loads(f.read())
        except IOError:
            logging.critical("No config file was found, please ensure path " 
                             "is correct.")
            sys.exit(1)
        except ValueError:
            logging.critical("The config file %s is imporperly configured. "
                            "Please ensure it adheres to "
                            "the JSON format.") % self.configfile
            sys.exit(1)

    def set_debug(self, debug):

        """ Convert numerical debugging level to logging variable """
        if debug < 1 :
            logging.basicConfig(level=logging.CRITICAL)
        elif debug == 1:
            logging.basicConfig(level=logging.ERROR)
        elif debug == 2:
            logging.basicConfig(level=logging.WARNING)
        elif debug == 3:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)

    def login(self, uname, passw):

        """ Perform login to VIVO and set cookie for transactions """
        data = {'loginName': uname,
                'loginPassword': passw,
                'loginForm': 'Log in'}

        r1 = requests.get(self.server+"/login")
        c1 = r1.cookies
        r = requests.post(self.server+"/authenticate", data=data, cookies=c1)
        #!!! Possibly handle HTTP 30x redirects here (http v https issue)
        if r.status_code == 200:
            return c1
        else:
            print r.status_code
            raise EnvironmentError("Unable to authenticate user")

    def query_triplestore(self, query, prefixes=None):

        """ Perform SPARQL Query against the VIVO SPARQL console """
        if not prefixes:
            try:
                with open('config/prefixes.txt', 'r') as f:
                    prefixes = f.read()
            except IOError:
                logging.warning("Unable to find prefixes file and no prefixes "
                               "were provided. Running query without prefixes.")
                prefixes = ""

        data = {"query": prefixes+'\n'+query,
                "resultFormat": "application/sparql-results+json",
                "rdfResultFormat": "text/turtle"}

        url = "/admin/sparqlquery?"+urllib.urlencode(data)
        r = requests.get(self.server+url, cookies=self.cookies)
        return r.content

    def rebuild_search_index(self):

        """ Trigger a reload of the search index """
        data = {'rebuild': 'Rebuild'}
        r = requests.post(self.server+"/SearchIndex", data=data, cookies=self.cookies)
        # Possibly try to do a check with status bar until it's done?

    def recompute_inference(self):

        """ Trigger the system to start reinferencing """
        r = requests.post(self.server+"/RecomputeInferences") 

    def upload_file(self, loc, rdftype="file", lang="N3", mode="add", cg=True):
        
        """ Upload an ontology file into VIVO """
        if lang not in ('RDF/XML', 'N3', 'N-TRIPLE', 'TTL'):
            logging.warning("Unrecognized Language Parameter for "
                            "resource request %s") % loc
        if mode not in ('directAddABox', 'add', 'remove'):
            logging.warning("Unrecognized Mode Parameter for "
                           "resource request %s") % loc 
        data = {"mode": mode,
                "language": lang,
                "makeClassgroups": cg}
        if rdftype.lower() == "file":
            data['rdfStream'] = loc
        elif rdftype.lower() == "url":
            data['rdfUrl'] = loc
        else:
            logging.warning("Unrecognized Location Parameter for "
                           "resource request %s") % loc

        headers = {"Content-Type": "multipart/form-data"}
        r = requests.post(self.server+"/uploadRDF", data=filename, headers=headers)
        #Return status code?
