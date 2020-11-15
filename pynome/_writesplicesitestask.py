"""
Contains the WriteSpliceSitesTask class.
"""
from . import interfaces
import os
import subprocess








class WriteSpliceSitesTask(interfaces.AbstractTask):
    """
    Detailed description.
    """


    def __call__(
        self
        ):
        """
        Detailed description.
        """
        basePath = os.path.join(self._workDir_(),self._rootName_())
        if not os.path.isfile(basePath+".gtf"):
            return False
        with open(basePath+".Splice_sites",'w') as ofile:
            self._log_("Writing Spice sites from GTF")
            cmd = ['hisat2_extract_splice_sites.py',basePath+".gtf"]
            assert(subprocess.run(cmd,stdout=ofile).returncode==0)
        return True


    def name(
        self
        ):
        """
        Implements the pynome.interfaces.AbstractTask interface.

        Returns
        -------
        ret0 : object
               See interface docs.
        """
        return "write_splice_sites"
