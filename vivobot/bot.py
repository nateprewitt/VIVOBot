import json
import logging
import os

import requests


class VIVOBot(object):
    """VIVOBot is a simple class to interact with various functionality in
    the vivo siteAdmin console via http requests.
    """

    TRIPLE_TYPES = ('RDF/XML', 'N3', 'N-TRIPLE', 'TTL')

    def __init__(self, filename=None, debug=2):

        self.configfile = filename
        self.set_debug(debug)
        vardict = self.initialize_env()
        self.server = vardict.get('server', '')
        self.user = vardict.get('uname', '')
        self.password = vardict.get('pass', '')
        self.cookies = self.login(self.user, self.password)

    def initialize_env(self):
        """Load parameters from environment variables if available, otherwise
        attempt to load them from a supplied config file.
        """
        if self.configfile is None:
            var_dict = {'server': os.environ.get('VIVO_SERVER'),
                        'uname': os.environ.get('VIVO_USER'),
                        'pass': os.environ.get('VIVO_PASS')}

            if not all([v for k, v in var_dict.items()]):
                raise ValueError('VIVO environment variables are not set '
                                 'appropriately, and no config file was '
                                 'supplied.')
        else:
            var_dict = self.ingest_config()

        return var_dict

    def ingest_config(self):
        """Opens configuration file and loads contents as JSON"""
        try:
            with open(self.configfile, 'rb') as f:
                return json.loads(f.read())
        except IOError:
            raise IOError("No config file was found, please ensure path "
                          "is correct.")
        except ValueError:
            raise ValueError("The config file %s is imporperly configured. "
                             "Please ensure it adheres to "
                             "the JSON format." % self.configfile)

    def set_debug(self, debug):
        """Convert numerical debugging level to logging variable"""
        if debug < 1:
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
        """Perform login to VIVO and set cookie for transactions"""
        data = {'loginName': uname,
                'loginPassword': passw,
                'loginForm': 'Log in'}

        resp = requests.head(self.server+"/login")
        cookies = resp.cookies
        r = requests.post(self.server+"/authenticate", data=data, cookies=cookies)
        if r.ok:
            return c1
        else:
            raise EnvironmentError("%s received: Unable to authenticate "
                                   "user" % r.status_code)

    def query_triplestore(self, query, prefixes=None):
        """Perform SPARQL Query against the VIVO SPARQL console"""
        if not prefixes:
            try:
                with open('config/prefixes.txt', 'r') as f:
                    prefixes = f.read()
            except IOError:
                logging.warning("Unable to find prefixes file and no prefixes "
                                "were provided. Running query without "
                                "prefixes.")
                prefixes = ''

        data = {'query': '\n'.join(prefixes, query),
                'resultFormat': 'application/sparql-results+json',
                'rdfResultFormat': 'text/turtle'}

        url = '/admin/sparqlquery'
        r = requests.get(self.server+url, params=data, cookies=self.cookies)
        return r.content

    def rebuild_search_index(self):
        """Trigger a reload of the search index"""
        data = {'rebuild': 'Rebuild'}
        r = requests.post(self.server+'/SearchIndex', data=data, cookies=self.cookies)
        # Possibly try to do a check with status bar until it's done?

    def recompute_inference(self):
        """Trigger the system to start reinferencing"""
        r = requests.post(self.server+'/RecomputeInferences')
        if not r.ok:
            pass # Raise exception?

    def upload_file(self, loc, rdftype="file", lang="N3", mode="add", cg=True):
        """Upload an ontology file into VIVO"""
        if lang not in TRIPLE_TYPES:
            logging.warning("Unrecognized Language Parameter for "
                            "resource request %s") % loc
        if mode not in ('directAddABox', 'add', 'remove'):
            logging.warning("Unrecognized Mode Parameter for "
                            "resource request %s") % loc
        data = {'mode': mode,
                'language': lang,
                'makeClassgroups': cg}
        if rdftype.lower() == 'file':
            data['rdfStream'] = loc
        elif rdftype.lower() == 'url':
            data['rdfUrl'] = loc
        else:
            logging.warning("Unrecognized Location Parameter for "
                            "resource request %s") % loc

        # pretty sure you should be passing this to the `file` param...
        headers = {'Content-Type': 'multipart/form-data'}
        r = requests.post(self.server+"/uploadRDF", data=data, headers=headers)

        return r.ok
