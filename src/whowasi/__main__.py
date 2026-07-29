# whowasi: a tool to record source version information into binaries.
#
# Copyright (c) 2026 Institut des Géosciences de l'Environnement, Grenoble.
#
# License: BSD 3-clause "new" or "revised" license (BSD-3-Clause).

import argparse
import os

parser = argparse.ArgumentParser(
    prog="whowasi",
    description="Record source version information into binaries.",
    epilog="This programme is released under the BSD-3-Clause license.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument(
    "-r",
    "--repository",
    help="Path to the repository",
    default=".",
)
parser.add_argument(
    "-c",
    "--version-control",
    help="Version control system used by the repository.",
    default="git",
)
parser.add_argument(
    "-l",
    "--language",
    help="Programming language to use (case-insensitive).",
    required=True,
)
parser.add_argument(
    "-o",
    "--output",
    help=("Output file where to write the code. A relative path is "
          "interpreted as relative to the root of given repository, not "
          "relative to current working directory (default=whowasi.*)."
          ),
    default=None,
)
parser.add_argument(
    "-n",
    "--name",
    help="Name of the whowasi function",
    default="whowasi",
)

args = parser.parse_args()

language = args.language.lower()
output_file = args.output
if output_file is None:
    extensions = {"c": "c"}
    output_file = f"whowasi.{extensions[language]}"
routine_name = args.name
