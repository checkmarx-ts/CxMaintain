import json
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from PyInquirer import prompt
import yaml
from cxmaintain.config import Config
from dateutil.parser import parse

class Retention(Config):
    """
    Check for directories that can be deleted.
    """
    def __init__(self, verbose, daylimit, delete_dir):
        super().__init__(verbose)
        self.daylimit = daylimit
        self.delete = delete_dir
        config = self.read_cx_config()
        self.host = config['host']
        self.verify = config['ssl_verify']
        self.token = "Bearer {0}".format(self.read_token())
        self.payload = {}
        self.scans_url = "https://{0}/CxRestApi/sast/scans?scanStatus=Finished".format(self.host)
        self.headers = {'Authorization': self.token, 'Accept': 'application/json;v=1.0'}
        self.scans_data = None
        self.delete_dirs_list = []
        self.get_scans()
        self.current_time = datetime.now()
        self.get_directories_for_delete()

    def get_scans(self):
        """
        Get All Scans
        """
        response = self.session.request('GET', self.scans_url, data=self.payload, headers=self.headers, verify=self.verify)
        if response.ok:
            self.scans_data = response.json()
        else:
            if self.verbose:
                print("Failed fetching scan data")
            self.logger.error("error in fetching scan data", response.text)

    def check_delete_eligibility(self, scan_data):
        """
        Check if a scan is eligible for deletion
        """
        if not scan_data or scan_data == {}:
            return False

        diff = (self.current_time - parse(scan_data['dateAndTime']['finishedOn'])).days
        # Scan is not locked
        if not scan_data['isLocked'] and diff > self.daylimit:
            return True

    def get_directories_for_delete(self):
        for scan in self.scans_data:
            if self.check_delete_eligibility(scan_data=scan):
                self.logger.info('scan_id: {0}, lock status: {1}'.format(scan['id'], scan['isLocked']))
                self.delete_dirs_list.append("{0}_{1}".format(scan['project']['id'], scan['scanState']['sourceId']))

                if self.verbose:
                    print('scan_id: {0}, lock status: {1}'.format(scan['id'], scan['isLocked']))

    def perform_delete(self):
        if not self.delete:
            for d in self.delete_dirs_list:
                print("Mock Delete: {0}".format(d))
                self.logger.info("Mock Delete: {0}".format(d))
        if self.delete:
            for d in self.delete_dirs_list:
                self.logger.info("Deleteing", d)
                if self.verbose:
                    print("Deleting directory: ", d)
                try:
                    rmtree(Path(d))
                except Exception as err:
                    self.logger.error(err)
                    self.logger.error('Cannot delete directory', d)
