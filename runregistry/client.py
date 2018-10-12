""""
RunRegistry Client
"""
import logging
from json import JSONDecodeError

import requests

logger = logging.getLogger(__name__)


class Singleton(type):
    """
    Allow only one instance of a class
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RunRegistryClient(metaclass=Singleton):
    """
    Implements a simple client that accesses the RunRegistry through the resthub API

    See:
    https://github.com/valdasraps/resthub
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/DqmRrApi
    """

    DEFAULT_URL = "http://vocms00170:2113"
    ALTERNATIVE_URL = "http://cmsrunregistryapi.cern.ch:2113"

    DEFAULT_NAMESPACE = "runreg_tracker"
    DEFAULT_TABLE = "dataset_lumis"

    def __init__(self, url=DEFAULT_URL):
        self.url = url
        self._connection_successful = None  # Lazy

    def _test_connection(self):
        try:
            requests.get(self.url)
            return True
        except requests.ConnectionError:
            return False

    def retry_connection(self):
        """
        Retry to connect to Run Registry.
        Updates return value of the connection_possible method.
        """
        self._connection_successful = self._test_connection()

    def connection_possible(self):
        """
        Check if the connection to the Run Registry is possible.

        Example:
        >>> client = RunRegistryClient()
        >>> client.connection_possible()
        True

        :return: True when connection to Run Registry was successful
        """
        if self._connection_successful is None:
            self.retry_connection()
        return self._connection_successful

    def _get_json_response(self, resource, media_type=None):
        if not self.connection_possible():
            logger.error("Connection to {} not possible".format(self.url))
            return {}

        if media_type:
            headers = {"Accept": media_type}
            response = requests.get(self.url + resource, headers=headers)
            return response.content.decode("utf-8")

        try:
            response = requests.get(self.url + resource)
            return response.json()
        except JSONDecodeError as e:
            logger.error(e)
            return {}

    def _get_query_id(self, query):
        """
        Converts a SQL query string into a query id (qid), that will be used to access
        the RunRegistry.

        POST: /query

        :param query: SQL query string
        :return: query id
        """
        response = requests.post(self.url + "/query?", data=query)
        if response.status_code == 400:
            raise ValueError(response.text)
        return response.text

    def execute_query(self, query, media_type=None):
        """
        Executes an arbitrary SQL query

        GET: /query/{query_id}

        Limitations:
         - tables referred by namespace.table
         - all tables used must have the unique alias in a query
         - only tables that share the same connection can be used in a query
         - named parameters are supported, i.e. :name
         - by default named parameter is considered of string type
         - named parameter type can be changed with prefix:
           - s__{parameter name} string type, i.e. s__name, s__country
           - n__{parameter name} number type, i.e. n__id, n__voltage
           - d__{parameter name} date type, i.e. d__from, d__to
         - supported functions can be found under /info

        Example:
        >>> client = RunRegistryClient()
        >>> query = "select r.runnumber from runreg_global.runs r " \
                    "where r.run_class_name = 'Collisions15'" \
                    "and r.runnumber > 247070 and r.runnumber < 247081"
        >>> client.execute_query(query)
        {'data': [[247073], [247076], [247077], [247078], [247079]]}

        :param media_type: Desired media type, e.g. application/xml, text/json
        :param query: SQL query string
        :return: JSON dictionary
        """
        if not self.connection_possible():
            logger.error("Connection to {} not possible".format(self.url))
            return {}
        query_id = self._get_query_id(query)
        resource = "/query/" + query_id + "/data"
        return self._get_json_response(resource, media_type)

    def get_table_description(self, namespace=DEFAULT_NAMESPACE, table=DEFAULT_TABLE):
        """
        Table description in JSON

        Example:
        >>> client = RunRegistryClient()
        >>> client.get_table_description("runreg_tracker", "dataset_lumis")["metadata"]["description"]
        'Dataset lumisections including exceptions'

        :param namespace: runreg_{workspace}, e.g. runreg_tracker
        :param table: runs, run_lumis, datasets, dataset_lumis
        :return: json containing the table description
        """
        resource = "/table/{}/{}".format(namespace, table)
        return self._get_json_response(resource)

    def get_queries(self):
        """
        GET /queries/

        :return: list of queries
        """
        return self._get_json_response("/queries")

    def get_query_description(self, query_id):
        """
        GET /query/{query_id}

        :return: json dictionary with query description
        """
        return self._get_json_response("/query/{}".format(query_id))

    def get_info(self):
        """
        GET /info

        Contains a list of supported functions and the version numbers.

        Example:
        >>> client = RunRegistryClient()
        >>> client.get_info()["version"]["resthub"]
        '0.6.18'

        :return json with general information about the service
        """
        return self._get_json_response("/info")
