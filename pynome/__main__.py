"""
This contains the main entry point function of this application. It also
contains functions that execute a specific operation.
"""
import argparse
from . import core
from . import crawlers
from . import processes
from . import settings
from . import tasks




def index(
    path
    ):
    """
    Indexes an assembly from the given job file path. The given path must be a
    generated pynome job file with the taxonomy ID and assembly name.

    Parameters
    ----------
    path : object
           Path to a generated pynome job file used to index its referenced
           assembly.
    """
    with open(path,"r") as ifile:
        parts = [x.strip() for x in ifile.read().split("\n") if x]
        assert(len(parts)==2)
        taxId = parts[0]
        assemblyName = parts[1]
        core.assembly.index(taxId,assemblyName)




def listAll():
    """
    Generates a list of new pynome job files, each one representing one assembly
    whose indexes need to be updated. The file output is the taxonomy ID and
    assembly name separated by a new line.
    """
    i = 0
    for (taxId,assemblyName) in core.assembly.listAllWork():
        with open(settings.JOB_NAME%(i,),"w") as ofile:
            ofile.write(taxId+"\n"+assemblyName+"\n")
        i += 1




def main():
    """
    Starts execution of this application.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",dest="crawl",action="store_true")
    parser.add_argument("-m",dest="mirror",action="store_true")
    parser.add_argument("-i",dest="index",action="store_true")
    parser.add_argument("-f",dest="indexFile",default=None)
    parser.add_argument("-I",dest="listAll",action="store_true")
    parser.add_argument("-t",dest="species",default="")
    parser.add_argument("-d",dest="rootPath",default=None)
    parser.add_argument("-q",dest="notEcho",action="store_true")
    parser.add_argument("-n",dest="cpuCount",type=int,default=0)
    args = parser.parse_args()
    if args.cpuCount > 0:
        settings.cpuCount = args.cpuCount
    if args.rootPath:
        settings.rootPath = args.rootPath
    core.log.setEcho(not args.notEcho)
    core.assembly.registerCrawler(crawlers.EnsemblCrawler())
    core.assembly.registerCrawler(crawlers.Ensembl2Crawler())
    core.assembly.registerCrawler(crawlers.NCBICrawler())
    core.assembly.registerProcess(processes.EnsemblProcess())
    core.assembly.registerProcess(processes.NCBIProcess())
    core.assembly.registerTask(tasks.DownloadCDNATask)
    core.assembly.registerTask(tasks.DownloadFastaTask)
    core.assembly.registerTask(tasks.DownloadGffTask)
    core.assembly.registerTask(tasks.DownloadGtfTask)
    core.assembly.registerTask(tasks.IndexHisatTask)
    core.assembly.registerTask(tasks.IndexKallistoTask)
    core.assembly.registerTask(tasks.IndexSalmonTask)
    core.assembly.registerTask(tasks.WriteCDNATask)
    core.assembly.registerTask(tasks.WriteGtfTask)
    core.assembly.registerTask(tasks.WriteSpliceSitesTask)
    if args.listAll:
        listAll()
    else:
        if not args.crawl and not args.mirror and not args.index:
            core.assembly.crawl(args.species)
            core.assembly.mirror(args.species)
            if args.indexFile is not None:
                index(args.indexFile)
            else:
                core.assembly.indexSpecies(args.species)
        else:
            if args.crawl:
                core.assembly.crawl(args.species)
            if args.mirror:
                core.assembly.mirror(args.species)
            if args.index:
                if args.indexFile is not None:
                    index(args.indexFile)
                else:
                    core.assembly.indexSpecies(args.species)








if __name__ == "__main__":
    main()
