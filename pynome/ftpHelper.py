"""
========================
Generic Download Helpers
========================
"""
import logging


def crawl_ftp_dir(database, top_dir, parsing_function):
    """Recursively crawl a target directory. Takes as an input a
    target directory and a parsing function. The ftplib.FTP.dir()
    function is used to retrieve a directory listing, line by line,
    in string format. These are appended to a newly generated list.
    Each item in this list is subject to the parsing function.

    :param ftp_instance: An instance of ftplib.FTP()
    :param top_dir: The directory from which contents will be retrieved.
    :param parsing_function: The function to parse each non-directory
                             result.
    """
    logging.debug(
        'FTP CRAWL INITIALIZED WITH\n'
        '\tdatabase: {0}\n'
        '\ttop_dir: {1}\n'
        '\tparsing_function: {2}\n'
        .format(database, top_dir, parsing_function)
    )
    retrieved_dir_list = []  # empty list to hold the callback

    def dir_check(dir_value):
        """Checks if the input: dir_value is a directory. Assumes the input
        will be in the following format:
             ``"drwxr-sr-x  2 ftp   ftp    4096 Jan 13  2015 filename"``
        This works by checking the first letter of the input string,
        and returns True for a directory or False otherwise."""
        if dir_value[0][0] == 'd':
            return True
        else:
            return False

    database.ftp.dir(top_dir, retrieved_dir_list.append)

    for line in retrieved_dir_list:
        if dir_check(line):  # Then the line is a dir and should be crawled.
            target_dir = ''.join((top_dir, line.split()[-1], '/'))
            crawl_ftp_dir(database, target_dir, parsing_function)
        else:  # otherwise the line must be parsed.
            parsing_function(database, line, top_dir)
    return