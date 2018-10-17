""""
RunRegistry Client
"""
from itertools import groupby
from operator import itemgetter

from runregistry.client import RunRegistryClient
from runregistry.tracker.utilities import (
    transform_lowstat_to_boolean,
    build_dcs_query_string,
)
from runregistry.utilities import (
    list_to_dict,
    build_range_where_clause,
    build_list_where_clause,
)


class TrackerRunRegistryClient(RunRegistryClient):
    """
    Client to access the Tracker Workspace of the Run Registry

    https://cmswbmoffshift.web.cern.ch/cmswbmoffshift/runregistry_offline/index.jsf
    """

    def _get_dataset_runs(self, where_clause):
        query = (
            "select r.run_number, r.run_class_name, r.rda_name, r.rda_state, "
            "r.rda_last_shifter, r.rda_cmp_pixel, r.rda_cmp_strip, "
            "r.rda_cmp_tracking, r.rda_cmp_pixel_cause, r.rda_cmp_strip_cause, "
            "r.rda_cmp_tracking_cause "
            "from runreg_tracker.datasets r "
            "where {} "
            "and r.rda_name != '/Global/Online/ALL'".format(where_clause)
        )

        run_list = self.execute_query(query).get("data", [])

        keys = [
            "run_number",
            "run_class",
            "dataset",
            "state",
            "shifter",
            "pixel",
            "sistrip",
            "tracking",
            "pixel_lowstat",
            "sistrip_lowstat",
            "tracking_lowstat",
        ]

        run_dicts = list_to_dict(run_list, keys)
        transform_lowstat_to_boolean(run_dicts)

        return run_dicts

    def _get_dataset_lumis_runs(self, where_clause):
        query = (
            "select r.rdr_run_number, r.lhcfill, r.rdr_rda_name, r.rdr_section_from, "
            "r.rdr_section_to, r.rdr_section_count, "
            "r.cms_active, r.beam1_stable, r.beam2_stable, r.beam1_present, "
            "r.beam2_present, r.tibtid_ready, r.tob_ready, r.tecp_ready, "
            "r.tecm_ready, r.bpix_ready, r.fpix_ready "
            "from runreg_tracker.dataset_lumis r "
            "where r.rdr_rda_name != '/Global/Online/ALL' "
            "and {} "
            "order by r.rdr_run_number, r.rdr_rda_name, r.rdr_range".format(
                where_clause
            )
        )

        run_list = self.execute_query(query).get("data", [])

        keys = [
            "run_number",
            "lhcfill",
            "dataset",
            "section_from",
            "section_to",
            "section_count",
            "cms_active",
            "beam1_stable",
            "beam2_stable",
            "beam1_present",
            "beam2_present",
            "tibtid",
            "tob",
            "tecp",
            "tecm",
            "bpix",
            "fpix",
        ]

        return list_to_dict(run_list, keys)

    def _get_dataset_runs_with_active_lumis(self, where_clause):
        dcs_list = ["Tibtid", "TecM", "TecP", "Tob", "Bpix", "Fpix"]
        query = (
            "select r.run_number, r.run_class_name, r.rda_name, "
            "sum(l.rdr_section_count) as lumi_sections, "
            "r.rda_state, r.rda_last_shifter, r.rda_cmp_pixel, r.rda_cmp_strip, "
            "r.rda_cmp_tracking, r.rda_cmp_pixel_cause, r.rda_cmp_strip_cause, "
            "r.rda_cmp_tracking_cause "
            "from runreg_tracker.dataset_lumis l, runreg_tracker.datasets r "
            "where l.rdr_run_number = r.run_number "
            "and l.rdr_rda_name = r.rda_name "
            "and l.rdr_rda_name != '/Global/Online/ALL' "
            "and l.cms_active = 1 "
            "and (l.beam1_stable = 1 "
            "and l.beam2_stable = 1 "
            "or l.rdr_rda_name LIKE '%Cosmics%') "
            "and ({}) ".format(build_dcs_query_string(dcs_list, "l", "or"))
            + "and {} ".format(where_clause)
            + "group by r.run_number, r.rda_name, r.run_class_name, "
            "r.rda_state, r.rda_last_shifter, r.rda_cmp_pixel, r.rda_cmp_strip, "
            "r.rda_cmp_tracking, r.rda_cmp_pixel_cause, r.rda_cmp_strip_cause, "
            "r.rda_cmp_tracking_cause "
        )

        run_list = self.execute_query(query).get("data", [])

        keys = [
            "run_number",
            "run_class",
            "dataset",
            "lumi_sections",
            "state",
            "shifter",
            "pixel",
            "sistrip",
            "tracking",
            "pixel_lowstat",
            "sistrip_lowstat",
            "tracking_lowstat",
        ]

        run_dict = list_to_dict(run_list, keys)
        transform_lowstat_to_boolean(run_dict)

        return run_dict

    def get_runs_by_list(self, list_of_run_numbers):
        """
        Get list of run dictionaries from the Tracker workspace in the Run Registry

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> runs = client.get_runs_by_list(["323423"])
        >>> runs[0]["state"]
        'COMPLETED'

        :param list_of_run_numbers: list of run numbers
        :return: dictionary containing the queryset
        """
        if not list_of_run_numbers:
            return []

        where_clause = build_list_where_clause(list_of_run_numbers, "r.run_number")
        return self._get_dataset_runs(where_clause)

    def get_runs_by_range(self, min_run_number, max_run_number):
        """
        Get list of run dictionaries from the Tracker workspace in the Run Registry

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> runs = client.get_runs_by_range("323471", "323475")
        >>> runs[0]["run_class"]
        'Collisions18'

        :param min_run_number: first run number
        :param max_run_number: last run number
        :return: dictionary containing the queryset
        """
        where_clause = build_range_where_clause(
            min_run_number, max_run_number, "r.run_number"
        )
        return self._get_dataset_runs(where_clause)

    def get_lumi_sections_by_list(self, list_of_run_numbers):
        """
        Get list of lumisections for the given run number list

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> lumis = client.get_lumi_sections_by_list(["323471"])
        >>> lumis[0]["lhcfill"]
        7217

        :param list_of_run_numbers:
        :return:
        """
        where_clause = build_list_where_clause(list_of_run_numbers, "r.rdr_run_number")
        return self._get_dataset_lumis_runs(where_clause)

    def get_lumi_sections_by_range(self, min_run_number, max_run_number):
        """
        Get list of lumisections for the given run number range

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> lumis = client.get_lumi_sections_by_range("323472", "323485")
        >>> lumis[0]["section_count"]
        94

        :param min_run_number: first run number
        :param max_run_number: last run number
        :return: dictionary containing the queryset
        """
        where_clause = build_range_where_clause(
            min_run_number, max_run_number, "r.rdr_run_number"
        )
        return self._get_dataset_lumis_runs(where_clause)

    def get_active_lumi_runs_by_list(self, list_of_run_numbers):
        """
        Get list of runs with certification status and active lumi sections

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> runs = client.get_active_lumi_runs_by_list(["321777"])
        >>> runs[0]["lumi_sections"]
        279
        >>> client.get_active_lumi_runs_by_list(["324021"])[0]["lumi_sections"]
        777
        >>> client.get_active_lumi_runs_by_list(["323829"])[0]["lumi_sections"]
        456
        """
        where_clause = build_list_where_clause(list_of_run_numbers, "r.run_number")
        return self._get_dataset_runs_with_active_lumis(where_clause)

    def get_active_lumi_runs_by_range(self, min_run_number, max_run_number):
        """
        Get list of runs with certification status and active lumi sections

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> runs = client.get_active_lumi_runs_by_range("323472", "323485")
        >>> runs[0]["pixel"]
        'GOOD'
        """
        where_clause = build_range_where_clause(
            min_run_number, max_run_number, "r.run_number"
        )
        return self._get_dataset_runs_with_active_lumis(where_clause)

    def get_fill_number_by_run_number(self, list_of_run_numbers):
        """
        Retrieve a list of fill numbers by the given run numbers

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> client.get_fill_number_by_run_number([321177, 321178, 321218])
        [{'run_number': 321177, 'fill_number': 7048}, {'run_number': 321178, 'fill_number': 7048}, {'run_number': 321218, 'fill_number': 7052}]

        :param list_of_run_numbers:
        :return: list of dictionaries containing run number and corresponding fill number
        """
        where_clause = build_list_where_clause(list_of_run_numbers, "r.runnumber")
        query = (
            "select r.runnumber, r.lhcfill "
            "from runreg_tracker.runs r "
            "where {} "
            "order by r.runnumber".format(where_clause)
        )
        items = self.execute_query(query).get("data", [])
        keys = ["run_number", "fill_number"]
        return list_to_dict(items, keys)

    def get_unique_fill_numbers_by_run_number(self, list_of_run_numbers):
        """
        Retrieve a list of unique fill numbers by the given run numbers

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> client.get_unique_fill_numbers_by_run_number([321177, 321178, 321218])
        [7048, 7052]

        :param list_of_run_numbers:
        :return: list of dictionaries containing run number and corresponding fill number
        """

        where_clause = build_list_where_clause(list_of_run_numbers, "r.runnumber")
        query = (
            "select r.lhcfill "
            "from runreg_tracker.runs r "
            "where {} "
            "order by r.runnumber".format(where_clause)
        )
        return sorted({item[0] for item in self.execute_query(query).get("data", [])})

    def get_run_numbers_by_fill_number(self, list_of_fill_numbers):
        """
        Retrieve a list of run numbers by the given fill numbers

        Example:
        >>> client = TrackerRunRegistryClient()
        >>> client.get_run_numbers_by_fill_number([7048, 7049])
        [{'fill_number': 7048, 'run_number': [321171, 321174, 321175, 321177, 321178, 321179, 321181]}, {'fill_number': 7049, 'run_number': [321182, 321185, 321189]}]

        :param list_of_fill_numbers:
        :return: list of dictionaries containing fill number and corresponding
        list of run numbers
        """
        where_clause = build_list_where_clause(list_of_fill_numbers, "r.lhcfill")
        query = (
            "select r.lhcfill, r.runnumber "
            "from runreg_tracker.runs r "
            "where {} "
            "order by r.runnumber".format(where_clause)
        )
        response = self.execute_query(query).get("data", [])
        groups = groupby(response, itemgetter(0))
        items = [(key, [item[1] for item in value]) for key, value in groups]
        keys = ["fill_number", "run_number"]
        return list_to_dict(items, keys)

    def get_grouped_fill_numbers_by_run_number(self, list_of_run_numbers):
        """
        Example:
        >>> client = TrackerRunRegistryClient()
        >>> client.get_grouped_fill_numbers_by_run_number([321171, 321179, 321181, 321182, 321185])
        [{'fill_number': 7048, 'run_number': [321171, 321179, 321181]}, {'fill_number': 7049, 'run_number': [321182, 321185]}]
        """
        where_clause = build_list_where_clause(list_of_run_numbers, "r.runnumber")
        query = (
            "select r.lhcfill, r.runnumber "
            "from runreg_tracker.runs r "
            "where {} "
            "order by r.runnumber".format(where_clause)
        )
        response = self.execute_query(query).get("data", [])
        groups = groupby(response, itemgetter(0))
        items = [(key, [item[1] for item in value]) for key, value in groups]
        keys = ["fill_number", "run_number"]
        return list_to_dict(items, keys)
