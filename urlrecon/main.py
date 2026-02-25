########################################################################################################################
#                                                                                                                      #
#                         Main Module — Program that drives the Application                                            #
#                                                                                                                      #
#               AUTHOR: Srinivas Piskala Ganesh Babu                                                                   #
#                                                                                                                      #
#               DESCRIPTION:                                                                                           #
#                   Driver Program — connects and drives all modules to execute the program.                           #
#                                                                                                                      #
#               USAGE:                                                                                                 #
#                   python -m urlrecon.main -i <input_file> [-o <output_dir>]                                          #
#                                           [--format text|sql|kml|all] [--delay <seconds>]                           #
#                                                                                                                      #
########################################################################################################################

import argparse
import datetime
import logging
import os
import sys
import time

try:
    from .modules import restApi, domainInfoApi, reportGenerator
except ImportError:
    # Executed directly: python3 urlrecon/main.py
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "modules"))
    import restApi, domainInfoApi, reportGenerator  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_USAGE_HELP = """
======================================================================================================
+ Usage:                                                                                             +
+   python -m urlrecon.main -i <input_file_or_url> [options]                                         +
+                                                                                                    +
+ Required:                                                                                          +
+   -i / --input    Path to a local file of URLs, one per line.                                      +
+                   Use --url-source if the input is a remote URL to a list of targets.              +
+                                                                                                    +
+ Options:                                                                                           +
+   -o / --output   Output directory (default: current working directory)                            +
+   --format        Report format: text | sql | kml | all  (default: all)                            +
+   --delay         Seconds to pause between each URL (default: 0)                                   +
+   --url-source    Treat --input value as a remote URL that returns a URL list                      +
+   -v / --verbose  Enable debug-level logging                                                        +
======================================================================================================
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="urlrecon",
        description="URL/domain reconnaissance — DNS, WHOIS, geo and server fingerprint.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_USAGE_HELP,
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Local file containing URLs (one per line), or a remote URL when --url-source is set.",
    )
    parser.add_argument(
        "-o", "--output", default=os.getcwd(),
        help="Directory where reports will be written (default: current working directory).",
    )
    parser.add_argument(
        "--format", choices=["text", "sql", "kml", "all"], default="all",
        help="Output format (default: all).",
    )
    parser.add_argument(
        "--delay", type=float, default=0.0,
        help="Seconds to wait between each URL request (default: 0).",
    )
    parser.add_argument(
        "--url-source", action="store_true",
        help="Treat --input as a remote URL that returns a newline-delimited list of target URLs.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable debug-level logging.",
    )
    return parser


def load_urls(input_value, is_url_source):
    """Return a list of URL strings from a local file or a remote URL list."""
    if is_url_source:
        raw = restApi.httpRequest(input_value).get_request()
        if raw is None:
            raise RuntimeError(f"Failed to fetch URL list from: {input_value}")
        return [u for u in raw.splitlines() if u.strip()]
    else:
        with open(input_value, "r") as fh:
            return [line for line in fh.readlines() if line.strip()]


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve report format option
    option = None if args.format == "all" else args.format

    # Load URLs
    try:
        urls_to_test = load_urls(args.input, args.url_source)
    except Exception as e:
        end_time = datetime.datetime.utcnow()
        logger.error("Exception: %s", e)
        logger.error("Program ended at %s", end_time)
        logger.error("Program Finished with Failure!")
        sys.exit(1)

    # Initialise report writers
    report = None
    try:
        report = reportGenerator.reportGen(args.output, option)
    except Exception:
        logger.warning("Report path invalid, falling back to current directory.")
        try:
            report = reportGenerator.reportGen(os.getcwd(), option)
        except Exception as e:
            end_time = datetime.datetime.utcnow()
            logger.error("Exception: %s", e)
            logger.error("Program ended at %s", end_time)
            logger.error("Program Finished with Failure!")
            sys.exit(1)

    start_time = datetime.datetime.utcnow()
    logger.info("Program started at %s", start_time)
    logger.info("Fetching information for %d URL(s) …", len(urls_to_test))

    # Process each URL
    try:
        for i, url in enumerate(urls_to_test):
            url = url.strip()
            if not url:
                continue
            logger.debug("[%d/%d] %s", i + 1, len(urls_to_test), url)
            domain_info = domainInfoApi.domainInfo(url)
            report.push_data_to_report(domain_info)
            if args.delay and i < len(urls_to_test) - 1:
                time.sleep(args.delay)
    except Exception as e:
        end_time = datetime.datetime.utcnow()
        logger.error("Exception: %s", e)
        logger.error("Program ended at %s", end_time)
        logger.error("Program Finished with Failure!")
        if report:
            report.close_all()
        sys.exit(1)

    report.close_all()

    end_time = datetime.datetime.utcnow()
    logger.info("Program ended at %s", end_time)
    logger.info("Output successfully generated at: %s", args.output)
    logger.info("Execution time: %s", end_time - start_time)
    logger.info("Program Finished Successfully!")


if __name__ == "__main__":
    main()
