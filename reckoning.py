import datetime, hashlib, logging, random, sys, time
import mechanize

QUEUE_URL = 'https://appraisalzone.lendervend.com/SECURE/plus/pfac/QueuePage.aspx'
LOGIN_URL = 'https://appraisalzone.lendervend.com/Default.aspx'
USERNAME = 'kcnorris'
PASSWORD = 'Remember1!'

FORM_NAME = 'aspnetForm'
USERNAME_FIELD = 'ctl00$cph_content$tb_username'
PASSWORD_FIELD = 'ctl00$cph_content$tb_password'

USER_AGENT = 'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)'

EMPTY_CHECKSUM = '256f163a93109a1b99b178adeeb7d209'

JOB_LIMIT = 5
JOB_COUNT = 0

def get_browser():
	browser = mechanize.Browser()

	# I'm not sure which of these are required
	browser.addheaders = [
		('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.11) Gecko/2009060214 Firefox/3.0.11'),
		('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
		('Accept-Language', 'en-us,en;q=0.5'),
		('Accept-Encoding', 'gzip,deflate'),
		('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
		('Keep-Alive', '300'),
		('Connection', 'keep-alive')
		]

	browser.set_handle_robots(False)
	return browser

def setup_debug(browser):
	browser.set_debug_redirects(True)
	# browser.set_debug_responses(True)
	browser.set_debug_http(True)

	logger = logging.getLogger("mechanize")
	logger.addHandler(logging.StreamHandler(sys.stdout))
	logger.setLevel(logging.DEBUG)

	return browser

def login(browser):
	print 'Logging in...'
	browser.open(LOGIN_URL)
	# TODO: browser.form = list(browser.forms())[0] ?
	browser.select_form(nr=0)
	browser[USERNAME_FIELD] = USERNAME
	browser[PASSWORD_FIELD] = PASSWORD
	browser.submit()
	return browser

def job_filter(control):
	return control.type == 'radio'

def check_queue(browser):
	print 'Checking queue...'
	browser.open(QUEUE_URL)
	browser.select_form(nr=0)

	if filter(job_filter, browser.form.controls):
		return get_jobs(browser)
	else:
		print ' - Found no jobs...'

	return browser

def get_jobs(browser):
	job_controls = filter(job_filter, browser.form.controls)
	if len(job_controls) + JOB_COUNT >= JOB_LIMIT:
		job_controls = job_controls[:JOB_LIMIT-JOB_COUNT]

	print ' * Getting %d job(s)...' % len(job_controls)
	for control in job_controls:
		control.value = ['1']

	browser.submit()

	filename = 'response-%s.html' % time.strftime('%Y%m%d-%H%M%S')
	print ' * Writing response to %s...' % filename
	file(filename, 'w').write(browser.response.read())

	JOB_COUNT += len(job_controls)
	if JOB_COUNT >= JOB_LIMIT:
		print ' * Reached job limit for this session.'
		print ' * Exiting.'
		sys.exit()

	return browser

def main():
	start = datetime.datetime.now()
	print 'Starting at %s' % start

	browser = get_browser()
	login(browser)

	while 1:
		try:
			check_queue(browser)
		except Exception, e:
			print ' * Caught exception: %s' % e
			#print ' * Restarting...'
			#login(browser)
			#check_queue(browser)

		delay = random.randint(10, 60)
		print 'Sleeping for %d seconds...\n' % delay
		time.sleep(delay)

if __name__ == '__main__':
	main()
