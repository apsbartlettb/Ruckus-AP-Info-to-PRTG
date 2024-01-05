# Ruckus-AP-Info-to-PRTG
A python script to get data from Ruckus Zone Director via API, and format it for proper ingestion into PRTG.

---

To install this, you'll need to copy it to the 'PRTG Network Monitor\Custom Sensors\python' folder.

You'll also need to run pip as system, which means you'll need PsExec from SysInternals. You can run 'PsExec64.exe -s -i cmd.exe' to get an interactive console to do this.

You need to install requests and python-dotenv in order for the script to operate properly.

pip install requests
pip install python-dotenv

or alternatively

python -m pip install requests
python -m pip install python-dotenv

Then you install the custom sensor in PRTG. Congrats, you did it.