import datetime, hashlib, logging, random, re, sys, time
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

JOB_LIMIT = 3
JOB_COUNT = 0

JOB_ID_RE = r"\('([\w$]+)','(\d+)'\)"

def get_browser():
	browser = mechanize.Browser()

	# I'm not sure which of these are required
	browser.addheaders = [
		('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X '
		 '10.5; en-US; rv:1.9.0.11) Gecko/2009060214 Firefox/3.0.11'),
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
		return get_job(browser)
	else:
		print ' - Found no jobs...'

	return browser

def get_job_id(control):
	assert len(control.items) == 2, \
		'Expected 2 items in the radio control, got %d' % len(control.items)
	item = control.items[-1]

	assert 'onclick' in item.attrs, \
		'No onclick handler found for item %s' % item.id
	onclick = item.attrs['onclick']

	match = re.search(JOB_ID_RE, onclick)
	assert match is not None, \
		'No job ID found in onclick event: %s' % onclick

	return match.groups()

def get_job(browser):
	global JOB_LIMIT, JOB_COUNT
	if JOB_COUNT >= JOB_LIMIT:
		print ' * Reached job limit for this session.'
		print ' * Exiting.'
		sys.exit()

	timestamp = time.strftime('%Y%m%d-%H%M%S')

	filename = 'queue-%s.html' % timestamp
	print ' * Writing queue response to %s...' % filename
	file(filename, 'w').write(browser.response().read())

	job_controls = filter(job_filter, browser.form.controls)
	job_control = job_controls[0]
	control_name, job_id = get_job_id(job_control)

	# Set the appropriate values on the form
	job_control.value = ['1']

	# Dumb ASP.NET postback stuff
	c = browser.form.find_control('__EVENTTARGET')
	c.readonly = False
	c.value = control_name

	c = browser.form.find_control('__EVENTARGUMENT')
	c.readonly = False
	c.value = job_id

	print ' * Getting job id %s...' % job_id
	browser.submit()
	JOB_COUNT += 1

	filename = 'response-%s.html' % timestamp
	print ' * Writing post-submit response to %s...' % filename
	file(filename, 'w').write(browser.response().read())

	# Check the queue again, to see if there are any more jobs
	# available
	return check_queue(browser)

def main():
	start = datetime.datetime.now()
	print 'Starting at %s' % start

	browser = get_browser()
	login(browser)

	while 1:
		check_queue(browser)

		delay = random.randint(10, 60)
		print 'Sleeping for %d seconds...\n' % delay
		time.sleep(delay)

if __name__ == '__main__':
	main()
