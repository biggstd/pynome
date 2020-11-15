"""
Contains the WriteGtfTask class.
"""
from . import interfaces
import os
import subprocess








class WriteGtfTask(interfaces.AbstractTask):
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
        if not os.path.isfile(basePath+".gff"):
            return False
        if self._meta_().get("gtf",""):
            return True
        self._log_("Writing GTF from GFF")
        tPath = os.path.join(self._workDir_(),"temp.gff")
        cmd = ["cp",basePath+".gff",tPath]
        assert(subprocess.run(cmd).returncode==0)
        cmd = ["gffread","-T",tPath,"-o",basePath+".gtf"]
        assert(subprocess.run(cmd).returncode==0)
        cmd = ["rm",tPath]
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
        return "write_gtf"
