import argparse
import json

from runregistry.client import RunRegistryClient
from runregistry.utilities import media_type_dict


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run Registry command line client.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=35),
    )

    parser.add_argument(
        "-i",
        "--info",
        help="General information about the service",
        action="store_true",
    )

    parser.add_argument(
        "-q", help="SQL query used to access the Run Registry.", metavar="query"
    )

    parser.add_argument(
        "-f",
        help="Specify output format",
        choices=["xml", "json", "json2", "csv"],
        default="csv",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    run_reg = RunRegistryClient()
    if args.info:
        print(json.dumps(run_reg.get_info(), indent=2))
    if args.q:
        try:
            media_type = media_type_dict.get(args.f, None)
            response = run_reg.execute_query(args.q, media_type)
            print(response)
        except ValueError as e:
            print("Error: Your SQL query is invalid")
            print(e)


if __name__ == "__main__":
    main()
