"""
Contains the WriteCDNATask class.
"""
from . import interfaces
import os
import subprocess








class WriteCDNATask(interfaces.AbstractTask):
    """
    This is the write CDNA task. It implements the abstract task interface. This
    writes the local CDNA Fasta file with gffread.
    """


    def __call__(
        self
        ):
        """
        Implements the pynome.interfaces.AbstractTask interface.

        Returns
        -------
        ret0 : object
               See interface docs.
        """
        basePath = os.path.join(self._workDir_(),self._rootName_())
        if not os.path.isfile(basePath+".fa") or not os.path.isfile(basePath+".gtf"):
            return False
        self._log_("Writing CDNA from GTF")
        cmd = ["gffread","-w",basePath+".cdna.fa","-g",basePath+".fa",basePath+".gtf"]
        assert(subprocess.run(cmd,capture_output=True).returncode==0)
        cmd = ["rm",basePath+".fa.fai"]
        assert(subprocess.run(cmd).returncode==0)
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
        return "write_cdna"
