"""Retrieves genome data files & metadata form online databases.
In this version (0.1.0) only the Ensembl database is implemented.

**SCIDAS**: On SciDAS pynome is located under:
    /data/ficklin/modulefiles/pynome_deploy

So to run it, and download to a directory on SciDAS storage (from
the pynome dir)::

    $ python3 -m pynome -fdm /scidas/genomes2/genome.db /scidas/genomes2
    $ python3 -m pynome -dm /scidas /scidas/genomes


**Usage Examples**::

    $ python -m pynome -fdm
"""

import os
import logging
import argparse
from pynome.ensembl import EnsemblDatabase


logging.getLogger(__name__)
logging.basicConfig(
    filename='main.log',
    filemode='w',
    level='INFO'
)


def entry_find_genomes(database):
    """The entry point to find genomes with default options. This should
    be called from the command line."""
    # Generate the base uri list:
    uri_list = database.generate_uri()
    database.find_genomes(uri_list=uri_list)


def entry_download_genomes(database):
    print("Downloading in progresss!\n")
    database.download_genomes()


def main():
    """The main command line parser for the Pynome module."""
    parser = argparse.ArgumentParser()  # Create the parser
    parser.add_argument('database_path',   # required positional argument
                        metavar='database-path', nargs=1)
    parser.add_argument('download_path',   # required positional argument
                        metavar='download-path', nargs=1)
    parser.add_argument('-f', '--find-genomes', action='store_true')
    parser.add_argument('-p', '--print-genomes', action='store_true')
    parser.add_argument('-d', '--download-genomes', action='store_true')
    parser.add_argument('-m', '--download-metadata', action='store_true')
    parser.add_argument('-r', '--read-metadata', action='store_true')
    parser.add_argument('-u', '--uncompress', action='store_true')
    parser.add_argument('-v', '--verbose', help='Set output to verbose.',
                        action='store_true')
    args = parser.parse_args()  # Parse the arguments
    logging.info('\nChecking for or creating the database.\n')

    # create the database path if it does not already exist
    if not os.path.exists(args.download_path[0]):
        os.makedirs(args.download_path[0])

    try:
        main_database = EnsemblDatabase(
            database_path=args.database_path[0],
            download_path=args.download_path[0],)
    except:
        print("Unable to create or read the database!")
        print('Database Path: {0}'.format(args.database_path[0]))
        exit()

    if args.verbose:  # Enable verbose logging mode
        logging.basicConfig(level=logging.DEBUG)

    # check if the database is populated:
    # if not, and find gemoes is not enabled
    # exit and print a

    if args.find_genomes:
        print('Finding Genomes!')
        entry_find_genomes(main_database)

    if args.print_genomes:
        print('Printing Genomes!')
        print(main_database.get_found_genomes())

    if args.download_metadata:
        print("Downloading Metadata!")
        main_database.download_metadata()

    if args.download_genomes:
        print('Downloading Genomes!')
        entry_download_genomes(main_database)

    if args.read_metadata:
        try:
            main_database.read_species_metadata()
            main_database.add_taxonomy_ids()
        except:
            print('Unable to read the metadata file: species.txt')

    if args.uncompress:
        main_database.decompress_genomes()

    exit()

if __name__ == '__main__':
    main()
