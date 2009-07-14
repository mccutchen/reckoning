# Configuration file for Reckoning

# Login information
username = 'kcnorris'
password = 'Remember1!'

# The maximum number of jobs to get in one session
job_limit = 5

# The minimum and maximum number of seconds to wait before rechecking
# the job queue
min_delay = 30
max_delay = 120


# IGNORE EVERYTHING BELOW THIS LINE
queue_url = 'https://appraisalzone.lendervend.com/SECURE/plus/pfac/QueuePage.aspx'
login_url = 'https://appraisalzone.lendervend.com/Default.aspx'

username_field = 'ctl00$cph_content$tb_username'
password_field = 'ctl00$cph_content$tb_password'

verbose = False
