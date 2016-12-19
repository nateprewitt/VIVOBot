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
        self.server = None
        self.username = None
        self.password = None
        self.session = requests.Session()
        self.initialize_env()

    def initialize_env(self):
        """Load parameters from environment variables if available, otherwise
        attempt to load them from a supplied config file.
        """
        if self.configfile is None:
            self.server = os.environ.get('VIVO_SERVER')
            self.username = os.environ.get('VIVO_USER')
            self.password = os.environ.get('VIVO_PASS')

            if not all((self.username, self.server, self.password)):
                raise ValueError('VIVO environment variables are not set '
                                 'appropriately, and no config file was '
                                 'supplied.')
        else:
            config = self.ingest_config()
            self.server = config['server']
            self.username = config['username']
            self.password = config['password']

        self.login(self.username, self.password)

    def ingest_config(self):
        """Opens configuration file and loads contents as JSON"""
        try:
            with open(self.configfile, 'r') as f:
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

    def login(self, username, password):
        """Perform login to VIVO and set cookie for transactions"""
        data = {'loginName': username,
                'loginPassword': password,
                'loginForm': 'Log in'}

        # Get a new JSESSIONID
        self.session.head(self.server+"/login")

        # Authenticate
        r = self.session.post(self.server+"/authenticate", data=data)

        if not r.request.url.endswith('siteAdmin'):
            # We didn't succesfully login but VIVO sends a 200 OK on failure
            r.status_code = 403
        if not r.ok:
            r.raise_for_status()

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
        r = self.session.get(self.server+url, params=data)
        return r.content

    def rebuild_search_index(self):
        """Trigger a reload of the search index"""
        data = {'rebuild': 'Rebuild'}
        r = self.session.post(self.server+'/SearchIndex', data=data)
        # Possibly try to do a check with status bar until it's done?

    def recompute_inference(self):
        """Trigger the system to start reinferencing"""
        r = self.session.post(self.server+'/RecomputeInferences')
        if not r.ok:
            r.raise_for_status()

    def upload_file(self, loc, rdftype="file", lang="N3", mode="add", cg=True):
        """Upload an ontology file into VIVO

        :param str loc: file path to the location of the file to upload.
        :param str rdftype: type of resource being uploaded, typically
            a file.
        :param str lang: the format of the triples in the file to be
            uploaded.
        :param str mode: action to be performed with uploaded file.
        :param str cg: class group to be created around the files
            contents.
        """
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
        r = self.session.post(self.server+"/uploadRDF", data=data, headers=headers)

        if not r.ok:
            r.raise_for_status()
