import os
import shutil
import subprocess
import schedule
import time
import datetime
import ConfigParser
from glob import glob

inifile = ConfigParser.SafeConfigParser()
inifile.read('./config.ini')

# define
DOWNLOAD_SCRIPTS = 'python ./simplenote-backup.py'.split()
BACKUP_FILE_DIR = inifile.get('settings', 'backupdir')
BACKUP_FILES_DIR = 'simplenote-backup-files/'
MAX_FILE_COUNT = inifile.get('settings', 'savecount')
RUN_TIME = inifile.get('settings', 'run_time')

# download and zip
def job():
	
	now = datetime.datetime.now()
	fileName = now.strftime("%Y%m%d-%H%M%S")
	
	# Start processing time
	now = datetime.datetime.now()
	print("[Start] " + now.strftime("%Y/%m/%d %H:%M:%S"))

	# download backup files
	isSuccessDownload = False
	try:
	    subprocess.call(DOWNLOAD_SCRIPTS)
	    isSuccessDownload = True
	    os.remove("dump")
	    print("Success download.")
	except:
	    print("Failure download.")

	# Processing after download
	if isSuccessDownload:

		# Zip file
		if not os.path.exists(BACKUP_FILES_DIR):
			os.makedirs(BACKUP_FILES_DIR)
		shutil.make_archive(BACKUP_FILES_DIR + fileName, 'zip', root_dir=BACKUP_FILE_DIR)
		print("Zipped.")

		# Remove temporary dir
		shutil.rmtree(BACKUP_FILE_DIR)
		print("Removed temporary dir.")

		# Remove old ZIP if it exceeds 100
		path = BACKUP_FILES_DIR + "/*.zip"
		files = glob(path)

		if len(files) > MAX_FILE_COUNT:
			files.sort(cmp=lambda x, y: int(os.path.getctime(x) - os.path.getctime(y)))

			for i in range(0, len(files) - MAX_FILE_COUNT):
				os.remove(files[i])
		print("Since 100 backups exceeded, the oldest ZIP was deleted.")

	# End processing time
	now = datetime.datetime.now()
	print("[End] " + now.strftime("%Y/%m/%d %H:%M:%S"))

# Entry point
if __name__=='__main__':

	# Test job
	job()

	# Run the job at {HH:MM}
	schedule.every().day.at(RUN_TIME).do(job)

	# Wait for run
	while True:
	    schedule.run_pending()
	    time.sleep(1)
