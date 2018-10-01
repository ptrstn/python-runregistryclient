""""
RunRegistry Client
"""
import requests


class RunRegistryClient:
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

    def __get_json_response(self, resource):
        response = requests.get(self.url + resource)
        return response.json()

    def __get_query_id(self, query):
        """
        Converts a SQL query string into a query id (qid), that will be used to access
        the RunRegistry.

        GET: /query/{query_id}

        :param query: SQL query string
        :return: query id
        """
        response = requests.post(self.url + "/query?", data=query)
        return response.text

    def execute_query(self, query):
        """
        Executes an arbitrary SQL query

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

        :param query: SQL query string
        :return: JSON dictionary
        """
        query_id = self.__get_query_id(query)
        resource = "/query/" + query_id + "/data"
        return self.__get_json_response(resource)

    def get_table_description(self, namespace=DEFAULT_NAMESPACE, table=DEFAULT_TABLE):
        """
        Table description in JSON

        :param namespace: runreg_{workspace}, e.g. runreg_tracker
        :param table: runs, run_lumis, datasets, dataset_lumis
        :return: json containing the table description
        """
        resource = "/table/{}/{}".format(namespace, table)
        return self.__get_json_response(resource)

    def get_queries(self):
        """
        GET /query/{query_id}

        :return: list of queries
        """
        return self.__get_json_response("/queries")

    def get_query_description(self, query_id):
        """
        GET /query/{query_id}

        :return: json dictionary with query description
        """
        return self.__get_json_response("/query/{}".format(query_id))

    def get_info(self):
        """
        GET /info

        Contains a list of supported functions and the version numbers.

        :return json with general information about the service
        """
        return self.__get_json_response("/info")
