# aws_ddns
A quick script for achieving dynamic DNS with AWS' Route 53 service.

To run this script every hour using a cronjob:

- crontab -e
- 0 * * * * /usr/bin/python3 /path_of_script/main.py
