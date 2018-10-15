import json

from runregistry.client import RunRegistryClient
from runregistry.utilities import build_list_where_clause


def _construct_query(run_numbers):
    return (
            "select r.rdr_run_number, r.rdr_section_from, r.rdr_section_to "
            "from runreg_tracker.dataset_lumis r "
            "where {} ".format(build_list_where_clause(run_numbers, "r.rdr_run_number"))
            + "and r.beam1_stable = 1 "
              "and r.beam2_stable = 1 "
              "and r.cms_active = 1 "
              "and r.TIBTID_READY = 1 "
              "and r.TOB_READY = 1 "
              "and r.TECP_READY = 1 "
              "and r.TECM_READY = 1 "
              "and r.BPIX_READY = 1 "
              "and r.FPIX_READY = 1 "
              "and r.rdr_rda_name != '/Global/Online/ALL' "
              "and r.rdr_rda_name like '%Collisions%' "
              "and r.rdr_rda_name like '%Prompt%' "
              "order by r.rdr_run_number, r.rdr_rda_name, r.rdr_range"
    )


def _convert_data_to_lumi_section_json(data):
    # element structure: [<run_number>, <section_from>, <section_to>]
    return json.dumps({
        run_number: [
            [element[1], element[2]]
            for element in list(filter(lambda entry: entry[0] == run_number, data))
        ]
        for run_number in {element[0] for element in data}
    })


class LumiSectionsRetriever:
    def get_json(self, run_numbers):
        """
        Example:
        >>> retriever = LumiSectionsRetriever()
        >>> retriever.get_json(["321813", 322222, 324218, 323983, 324075])
        '{"321813": [[20, 31], [32, 37], [38, 51], [52, 254], [255, 257], [258, 352], [353, 433]], "322222": [[1, 526]], "323983": [[1, 188]]}'
        """
        client = RunRegistryClient()
        query = _construct_query(run_numbers)
        response = client.execute_query(query)
        return _convert_data_to_lumi_section_json(response["data"])

