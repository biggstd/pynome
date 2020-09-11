"""
Contains all global setting for this application.
"""
import os


#
# The file name used for generating pynome job files.
#
JOB_NAME = "pynome_work_%05d.txt"


#
# The number of threads used when running index applications such as hisat2 and
# salmon.
#
cpuCount = os.cpu_count()


#
# The root path where the local species database is stored.
#
rootPath = os.path.join(os.path.expanduser("~"),"species")
