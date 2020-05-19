"""
Contains the Ensembl class.
"""
import ftplib
import socket
from . import abstract
from . import core








class Ensembl(abstract.AbstractCrawler):
    """
    This is the ensembl class. It implements the abstract crawler interface. The
    remote database is crawled directly through its ftp server to find all valid
    entries. All information can be found within those directories except for
    the taxonomy ID. The taxonomy ID is found in a special text file located in
    the root public folder.
    """


    #######################
    # PUBLIC - Initialize #
    #######################


    def __init__(
        self
        ):
        """
        Initializes a new ensembl crawler.
        """
        abstract.AbstractCrawler.__init__(self)
        self.__text = ""
        self.__taxIds = {}


    ####################
    # PUBLIC - Methods #
    ####################


    def crawl(
        self
        ,species=""
        ):
        """
        Implements the pynome2.abstract.AbstractCrawler interface.

        Parameters
        ----------
        species : object
                  See interface docs.
        """
        self.__ftp = None
        self.__connect_()
        releaseVersion = self.__latestRelease_()
        if releaseVersion:
            self.__getTaxonomyIds_(
                self.__FTP_ROOT_DIR
                + "/"
                + self.__FTP_RELEASE_BASENAME
                + str(releaseVersion)
            )
            fasta = self.__crawlFasta_(
                self.__FTP_ROOT_DIR
                + "/"
                + self.__FTP_RELEASE_BASENAME
                + str(releaseVersion)
                + self.__FTP_FASTA_DIR
            )
            gff3 = self.__crawlGff3_(
                (
                    self.__FTP_ROOT_DIR
                    + "/"
                    + self.__FTP_RELEASE_BASENAME
                    + str(releaseVersion)
                    + self.__FTP_GFF3_DIR
                )
                ,releaseVersion
            )
            self.__mergeResults_(fasta,gff3)


    def name(
        self
        ):
        """
        Implements the pynome2.abstract.AbstractCrawler interface.

        Returns
        -------
        ret0 : object
               See interface docs.
        """
        return "Ensembl"


    #####################
    # PRIVATE - Methods #
    #####################


    def __connect_(
        self
        ):
        """
        Connects this crawler to the ensembl FTP server, continuously retrying a
        connection until one is made successfully.
        """
        while True:
            try:
                self.__ftp = ftplib.FTP(self.__FTP_HOST,timeout=10)
                self.__ftp.login()
            except ftplib.all_errors:
                pass
            else:
                break


    def __crawlFasta_(
        self
        ,directory
        ,depth=0
        ):
        """
        Recursively crawls the given directory, calling this method on any
        subdirectories found. If the FTP connection is lost this crawler's
        connect method is called to reconnect and continue without interruption.

        Parameters
        ----------
        directory : string
                    The directory path that is recursively crawled for valid
                    FASTA files.
        depth : int
                The current subdirectory depth of this recursive scan. Used to
                print output about progress for only the top level call of this
                method.

        Returns
        -------
        ret0 : dictionary
               A lookup table of found valid FASTA files for potential entries
               where the keys are the file name excluding its FASTA extension
               and the values are the full path to the file.
        """
        ret = {}
        try:
            listing = [x.split("/").pop() for x in self.__ftp.nlst(directory)]
        except ftplib.all_errors:
            self.__connect_()
            return self.__crawlFasta_(directory,depth)
        except socket.timeout:
            self.__connect_()
            return self.__crawlFasta_(directory,depth)
        i = 1
        for file_ in listing:
            if not depth:
                core.log.send("Crawling Ensembl FASTA %i/%i"%(i,len(listing)))
            i += 1
            if file_.endswith(self.__FASTA_EXTENSION):
                ret[file_[:-len(self.__FASTA_EXTENSION)]] = directory+"/"+file_
            elif "." not in file_ and file_ not in self.__FTP_IGNORED_DIRS:
                ret.update(self.__crawlFasta_(directory+"/"+file_,depth+1))
        return ret


    def __crawlGff3_(
        self
        ,directory
        ,version
        ,depth=0
        ):
        """
        Recursively crawls the given directory, calling this method on any
        subdirectories found. If the FTP connection is lost this crawler's
        connect method is called to reconnect and continue without interruption.

        Parameters
        ----------
        directory : string
                    The directory path that is recursively crawled for valid
                    GFF3 files.
        version : string
                  The release number of the release directory that is being
                  scanned. This is needed for GFF3 because the release number is
                  part of its valid file name extension.
        depth : int
                The current subdirectory depth of this recursive scan. Used to
                print output about progress for only the top level call of this
                method.

        Returns
        -------
        ret0 : dictionary
               A lookup table of found valid GFF3 files for potential entries
               where the keys are the file name excluding its GFF3 extension and
               the values are the full path to the file.
        """
        ret = {}
        try:
            listing = [x.split("/").pop() for x in self.__ftp.nlst(directory)]
        except ftplib.all_errors:
            self.__connect_()
            return self.__crawlGff3_(directory,version,depth)
        except socket.timeout:
            self.__connect_()
            return self.__crawlGff3_(directory,version,depth)
        i = 1
        for file_ in listing:
            if not depth:
                core.log.send("Crawling Ensembl GFF3 %i/%i ..."%(i,len(listing)))
            i += 1
            ending = "."+str(version)+self.__GFF3_EXTENSION
            if file_.endswith(ending):
                ret[file_[:-len(ending)]] = directory+"/"+file_
            elif "." not in file_:
                ret.update(self.__crawlGff3_(directory+"/"+file_,version,depth+1))
        return ret


    def __getTaxonomyIds_(
        self
        ,directory
        ):
        """
        Downloads and parses the given taxonomy ID file, populating this
        crawlers lookup dictionary of taxonomy IDs.

        Parameters
        ----------
        directory : string
                    The directory on the ensembl FTP server where the special
                    taxonomy ID file is located.
        """
        self.__text = ""
        self.__taxIds = {}
        self.__ftp.retrlines("RETR "+directory+self.__TAXONOMY_FILE,self.__write_)
        for line in self.__text.split("\n")[1:]:
            parts = line.split("\t")
            if len(parts)>=5:
                self.__taxIds[parts[1]+"."+parts[4]] = parts[3]


    def __latestRelease_(
        self
        ):
        """
        Getter method.

        Returns
        -------
        ret0 : int
               The latest release number of all scanned release directories or 0
               if no release directories were found.
        """
        ret = 0
        listing = [x.split("/").pop() for x in self.__ftp.nlst(self.__FTP_ROOT_DIR)]
        for file_ in listing:
            if file_.startswith(self.__FTP_RELEASE_BASENAME):
                version = file_[len(self.__FTP_RELEASE_BASENAME):]
                if version.isdigit():
                    version = int(version)
                    if version > ret:
                        ret = version
        return ret


    def __mergeResults_(
        self
        ,fasta
        ,gff3
        ):
        """
        Merges the given FASTA and GFF3 dictionaries of found possible entries,
        adding an entry to this crawler for any key that both dictionaries
        contain.

        Parameters
        ----------
        fasta : dictionary
                The FASTA lookup dictionary generated by this crawler's crawl
                FASTA method.
        gff3 : dictionary
               The GFF3 lookup dictionary generated by this crawler's crawl GFF3
               method.
        """
        for key in fasta:
            if key in gff3:
                parts = key.split(".")
                names = parts.pop(0).split("_") + [""]
                taxKey = "_".join((n.lower() for n in names if n)) + "." + ".".join(parts)
                self._addEntry_(
                    names[0]
                    ,names[1]
                    ,names[2]
                    ,".".join(parts)
                    ,self.__taxIds.get(taxKey,"")
                    ,"ensembl"
                    ,{"fasta": fasta[key], "gff3": gff3[key]}
                )


    def __write_(
        self
        ,text
        ):
        """
        Callback function for writing to this crawlers special text holder for
        downloading a taxonomy ID file.

        Parameters
        ----------
        text : string
               The string that is appended to this crawlers special placeholder
               text.
        """
        self.__text += text+"\n"


    #######################
    # PRIVATE - Constants #
    #######################


    #
    # The extension of FASTA files that should be flagged as a possible entry
    # for this crawler.
    #
    __FASTA_EXTENSION = ".dna.toplevel.fa.gz"


    #
    # The directory on the ensembl FTP server where FASTA data is stored.
    #
    __FTP_FASTA_DIR = "/fasta"


    #
    # The directory on the ensembl FTP server where GFF3 data is stored.
    #
    __FTP_GFF3_DIR = "/gff3"


    #
    # The URL of the ensembl FTP server.
    #
    __FTP_HOST = "ftp.ensembl.org"


    #
    # A list of directory names that this crawler will ignore when crawling the
    # ensembl FTP server.
    #
    __FTP_IGNORED_DIRS = ["cdna","cds","dna_index","ncrna","pep"]


    #
    # The beginning of the directory name used for releases of data on the
    # ensembl FTP server.
    #
    __FTP_RELEASE_BASENAME = "release-"


    #
    # The root public directory for the ensembl FTP server.
    #
    __FTP_ROOT_DIR = "/pub"


    #
    # The extension of GFF3 files that should be flagged as a possible entry for
    # this crawler.
    #
    __GFF3_EXTENSION = ".gff3.gz"


    #
    # The file name of the special text file that contains all taxonomy IDs on
    # the ensembl FTP server in a release folder.
    #
    __TAXONOMY_FILE = "/species_EnsemblVertebrates.txt"