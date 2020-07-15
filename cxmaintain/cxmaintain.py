#!/usr/bin/env python3

'''Usage: 
{0} init [--verbose]
{0} login [--save] [--verbose]
{0} checktoken [--verbose]
{0} dryrun [--days=days] [--verbose]
{0} retention [--days=days] [--verbose]
{0} (-h | --help)
{0} version

Commands:
init            Create OR Reinitialize a configuration file to connect to Checkmarx cxsast v9.0
login           Authenticate user on Checkmarx
checktoken      Check token as unexpired. (Requires login --save to be used prior.)
retention       Check for CxSAST directories that can be deleted.

Options:
-s, --save               Save OAuth Token into configuration directory.
-h, --help               Help.
--delete                 Delete directories.
-v, --verbose            Display version of CxDir.
--days=days              Number of days to retain.

Report bugs to Checkmarx (Cx TS-APAC) <TS-APAC-PS@checkmarx.com>
'''
import docopt
import sys
from cxdir.auth.auth import Auth
from cxdir.config import Config
from cxdir.retention.retention import Retention


__version__ = '0.0.1'

def main(sysargv=None):
    argv = docopt.docopt(
        doc=__doc__.format('cxaccess'),
        argv=sysargv,
        version=__version__
    )
    if argv['version']:
        print("CxAccess version: {0}".format(__version__))
        sys.exit(0)
    
    # Default to 
    verbose = False
    if argv['--verbose']:
        verbose = True
    # We are defaulting to little more than 3 years as default
    daylimit = 1100
    if argv['--days']:
        try:
            daylimit = int(argv['--days'])
        except Exception as e:
            print("Please enter a number for days.")


    config = Config(verbose)
    config_checked = None


    if argv['init']:
        if not config_checked:
            config_checked = config.check_path()
    
    # Perform Authentication and Save token
    if argv['login'] and argv['--save']:
        authy = Auth(verbose)
        authy.perform_auth(save_config=True)
    
    if argv['login'] and not argv['--save']:
        authy = Auth(verbose)
        authy.perform_auth()
    
    if argv['checktoken']:
        config.read_token()
    
    if argv['dryrun']:
        delete_dir = False
        chkdir = Retention(verbose, daylimit, delete_dir)
        chkdir.perform_delete()

    if argv['retention']:
        delete_dir = True
        print("deleting directories")
        chkdir = Retention(verbose, daylimit, delete_dir=True)
        chkdir.perform_delete()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    sys.exit(main(sys.argv[1:]))
