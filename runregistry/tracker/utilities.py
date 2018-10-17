def transform_lowstat_to_boolean(list_of_run_dict):
    """
    Converts the low_stat properties of the list of run dictionaries into
    a boolean form

    True for low statistics
    False for no low statistics

    :param list_of_run_dict: list of runs (as dictionary)
    :return: list_of_run_dict
    """
    components = ["pixel", "sistrip", "tracking"]
    lowstat_components = ["{}_lowstat".format(component) for component in components]
    for run in list_of_run_dict:
        for component in lowstat_components:
            run[component] = run[component] == "LOW_STATS"
    return list_of_run_dict


def build_dcs_query_string(dcs_list, table, logical_connector="and"):
    """
    Example:
    >>> build_dcs_query_string(["Tibtid","TecM","TecP","Tob"], "r")
    'r.tibtid_ready = 1 and r.tecm_ready = 1 and r.tecp_ready = 1 and r.tob_ready = 1'
    >>> build_dcs_query_string(["BPIX","FPIX"], "l", "or")
    'l.bpix_ready = 1 or l.fpix_ready = 1'

    :param dcs_list: list of Detector Control Systems which should be ready
    :param table: name of the database table
    :param logical_connector: How the attributes dcs should be connected ("AND"/"OR")
    :return: SQL query string
    """
    return " {} ".format(logical_connector).join(
        ["{}.{}_ready = 1".format(table.lower(), dcs.lower()) for dcs in dcs_list]
    )
