import datetime, logging, random, sys, time
import mechanize

QUEUE_URL = 'https://appraisalzone.lendervend.com/SECURE/plus/pfac/QueuePage.aspx'
LOGIN_URL = 'https://appraisalzone.lendervend.com/Default.aspx'
USERNAME = 'kcnorris'
PASSWORD = 'Remember1!'

FORM_NAME = 'aspnetForm'
USERNAME_FIELD = 'ctl00$cph_content$tb_username'
PASSWORD_FIELD = 'ctl00$cph_content$tb_password'

USER_AGENT = 'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)'

def get_browser():
	browser = mechanize.Browser()
	# browser.addheaders = [('User-Agent', USER_AGENT)]
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
	#browser.set_handle_refresh(False)
	#browser.set_debug_redirects(True)
	# browser.set_debug_responses(True)
	#browser.set_debug_http(True)

	#logger = logging.getLogger("mechanize")
	#logger.addHandler(logging.StreamHandler(sys.stdout))
	#logger.setLevel(logging.DEBUG)

	return browser

def login(browser):
	print 'Logging in...'
	browser.open(LOGIN_URL)
	# TODO: browser.form = list(browser.forms())[0] ?
	browser.select_form(name=FORM_NAME)
	browser[USERNAME_FIELD] = USERNAME
	browser[PASSWORD_FIELD] = PASSWORD
	browser.submit()
	return browser

def check_queue(browser):
	print 'Checking queue...'
	browser.open(QUEUE_URL)

	filename = 'output/%s.html' % time.strftime('%Y%m%d-%H%M%S')
	fp = file(filename, 'w')
	fp.write(browser.response().read())
	fp.close()

	browser.select_form(name=FORM_NAME)

	if len(browser.form.controls) > 3:
		print ' - Extra form controls found.  Saving to %s...' % filename
		print ' - Fields: %s' % ', '.join(c.name for c in browser.form.controls)
		print ' - Exiting.'
		sys.exit()
	else:
		print ' - Nothing to see here...'
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

		delay = random.randint(30, 90)
		print 'Sleeping for %d seconds...\n' % delay
		time.sleep(delay)

if __name__ == '__main__':
	main()
