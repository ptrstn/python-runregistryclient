def transform_lowstat_to_boolean(list_of_run_dict):
    """
    Converts the low_stat properties of the list of run dictionaries into
    a boolean form

    True for low statistics
    False for no low statistics

    :param list_of_run_dict: list of runs (as dictionary)
    :return: list_of_run_dict
    """
    for run in list_of_run_dict:
        run["pixel_lowstat"] = run["pixel_lowstat"] == "LOW_STATS"
        run["sistrip_lowstat"] = run["sistrip_lowstat"] == "LOW_STATS"
        run["tracking_lowstat"] = run["tracking_lowstat"] == "LOW_STATS"
    return list_of_run_dict
