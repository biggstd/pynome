"""The ensembl database module. A child class of the genome database class,
this module cotains all code directly related to connecting and parsing data
from the ensembl geneome database."""

# Import standard modules
import itertools
from ftplib import FTP
import logging
import logging.config
# Imports from internal modules
from .genomedatabase import GenomeDatabase  # import superclass
from .genome import Genome

ensebml_ftp_uri = 'ftp.ensemblgenomes.org'

# TODO: Add a method to locally store genome information so that it does
#       not have to be re-downloaded or re-scraped with every run.

class EnsemblDatabase(GenomeDatabase):
    """The EnsemblDatabase class. This handles finding and downloading
    genomes from the ensembl genome database.
    
    It does so by recursively walking the ftp directory. It only collects
    those genomes that have a ``*.gff3.gz`` or a ``*.fa.gz`` file.

    - **parameters**::

        :param release_version: The release version specific to ensemble.
                                This should be a number between 1 and 36.
    
    :Example:

    Instructions on how to use this script.
    
    .. seealso:: :class:`GenomeDatabase`
    """

    def __init__(self, release_version=36):
        super(EnsemblDatabase, self).__init__()  # Call parent class init
        self._release_number = None  # set by the release version setter
        self.release_version = release_version
        self._ftp_genomes = []
        self.ftp = FTP()  # the ftp instance for the database
        logging.config.fileConfig('pynome/pynomeLog.conf')
        self.logger = logging.getLogger('pynomeLog')
        # Set up the logger, and note the class initialization.

    # TODO: Change to a yield-based function?
    def _crawl_directory(self, target_dir):
        """Recursively crawl a target directory.
        
        Calls ftplib.dir for the input target_dir.

        - **parameters**::

            :param target_dir: The directory whos contents will be retrieved.

        .. todo:: Refactor so that this function takes a parsing function as
                  an argument. In doing this, an recursive ftp class will
                  likely be factored out.
        
        """
        retrived_dir_list = []  # empty list to hold the callback
        # Get the directory listing for the target directory,
        # and append it to the holder list.
        self.ftp.dir(target_dir, retrived_dir_list.append)
        # Parse this list:
        # TODO: Refactor this out. Have a fn as an input var
        for item in retrived_dir_list:  # For each line retrieved.
            item = item.split()  # split the list by whitespace
            if self._dir_check(item):  # check if it is a directory
                # Create the new target directory by joining the old
                # and the new, which is the last listed item.
                new_target_dir = ''.join((target_dir, item[-1]))
                self.logger.info("Found a new directory:\n\t{}\ncrawling it.".format( \
                new_target_dir))
                self._crawl_directory(new_target_dir)  # crawl that dir
            elif self.genome_check(item[-1]):  # that item is not a dir,
                self.add_genome(item, target_dir)  # if so, add a genome
            else:
                pass
        return

    def add_genome(self, item, uri):
        """Creates a new genome from a dir line list, separated by whitespace"""
        # Did we find a fasta or a gff3?
        filename = item[-1]
        new_genome = Genome()  # create the new genome
        # set the assembly version, taxonomic name and the uri we found it at
        species, assembly = self._parse_species_filename(item[-1])
        new_genome.assembly_version = assembly
        new_genome.taxonomic_name = species
        self.logger.info('checking if this is a fasta or gff3: {}'.format(filename))
        if filename.endswith('fa.gz'):
            new_genome.gff3 = uri  # set the fa.gz url
        elif filename.endswith('gff3.gz'):
            new_genome.fasta = uri  # set the gff3.gz url
        else:  # not a fasta or a gff3! we fucked up!
            # TODO: Raise an error here.
            return
        self._ftp_genomes.append((new_genome, uri))

    def genome_check(self, item):
        """Checks if the incoming item, which is a dir line item separated by
        whitespace, is a 'genome' in that it must:
            + end with fa.gz or gff3.gz
            + not have 'chromosome' in the name
            + must not have 'abinitio' in the name"""
        bad_words = ('chromosome', 'abinitio')
        data_types = ('fa.gz', 'gff3.gz')
        self.logger.debug('GENOME CHECKING: {}'.format(item))
        if item.endswith(data_types) and \
            not any(word in bad_words for word in item):
            return True
        else:
            return False

    def _crawl_ftp(self):
        """
        handler function to crawl the ftp server to find genome files.
        """
        base_uri_list = self._generate_uri()  # Create the generator of uris.
        # ftp = FTP()  # Create the ftp class isntance
        self.ftp.connect(ensebml_ftp_uri)  # connect to the ensemble ftp
        self.ftp.login()  # login with anonomys and no password
        # iterate through those uri generated
        for uri in base_uri_list:
            # Get the directories in the base URI
            print("Going to start a new clade crawl with: {}".format(uri))
            self._crawl_directory(uri)
        self.ftp.quit()  # close the ftp connection

    def _dir_check(self, dir_value):
        """
        @brief      Checks if the input: dir_value is a directory. Assumes
                    the input will be in the following format:
                        'drwxr-sr-x  2 ftp   ftp    4096 Jan 13  2015 filename'
                    This works by checking the first letter of the input string,
                    and returns True or False.
        """
        if dir_value[0][0] == 'd':
            return True
        else:
            return False



    def _generate_uri(self):
        """
        @breif      Generates the uri strings needed to download the genomes
                    from the ensembl datab # Only those attributesase. Dependant on the release
                    version provided.

        @returns    List of Strings of URIs for the ensembl database. eg:

                        "TODO: example uri here"
                        "TODO: format output here"
        """
        __ensembl_data_types = ['gff3', 'fasta']
        __ensembl_kingdoms = ['fungi', 'metazoa', 'plants', 'protists']
        # __ensembl_ftp_uri = 'ftp.ensemblgenomes.org'

        # Unique permutations of data types and kingdoms.
        uri_gen = itertools.product(__ensembl_data_types, __ensembl_kingdoms)

        # For each iteration, return the desired URI.
        for item in uri_gen:
            yield '/'.join(('pub',
                            item[1],  # the clade or kingdom
                            self._release_version,
                            item[0],  # the data type
                            '', ))

    def _parse_species_filename(self, file_name):
        """<species>.<assembly>.<_version>.gff3.gz"""
        # TODO: Generate docstring for parse_species_filename.

        # Create a separator based of the release number.
        version_separator = '.{}'.format(self._release_number)
        # Split by this separator to get the species and assembly number.
        species_assembly_list = file_name.split(version_separator)
        # The first item in the list is the species and assembly.
        species, assembly = species_assembly_list[0].split('.', 1)
        return (species, assembly)

    def _find_genomes(self):
        """
        Private function that handles finding the list of genomes.
        """
        # Start the ftp crawler
        self._crawl_ftp()
        return

    def find_genomes(self):
        """OVERWRITES GENOMEDATABASE FUNCTION. Calls the _find_genomes() private
        function."""
        self._find_genomes()
        return

    @property
    def release_version(self):
        """Release version property. Should be in the form:
            "release-#", "release-36"
        """
        return self._release_version

    @release_version.setter
    def release_version(self, value):
        """Setter for the release_version. Accepts an input integer and returns
        a string in the form: 'release-##' """
        # TODO: Add validation to ensure that the input value is an integer.
        #       Perhaps it should also be limited to the range of available
        #       release verions on the ensembl site. (1 through 36)
        self._release_number = value
        self._release_version = 'release-' + str(value)

    def download_genomes(self):
        """Downloads the genomes in the database that have both fasta and gff3 files."""
        pass
