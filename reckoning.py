import datetime, random, sys, time
import mechanize

LOGIN_URL = 'https://appraisalzone.lendervend.com/Default.aspx'
USERNAME = 'kcnorris'
PASSWORD = 'Remember1!'

FORM_NAME = 'aspnetForm'
USERNAME_FIELD = 'ctl00$cph_content$tb_username'
PASSWORD_FIELD = 'ctl00$cph_content$tb_password'

USER_AGENT = 'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)'

def login(browser):
	print 'Logging in...'
	browser.open(LOGIN_URL)
	# TODO: browser.form = list(browser.forms())[0] ?
	browser.select_form(name=FORM_NAME)
	browser[USERNAME_FIELD] = USERNAME
	browser[PASSWORD_FIELD] = PASSWORD
	browser.submit()
	return browser

def check_queue(browser, reload=False):
	print 'Checking queue...'
	if reload:
		browser.reload()
	browser.select_form(name=FORM_NAME)

	filename = '%s.html' % time.strftime('%Y%m%d-%H%M%S')
	fp = file(filename, 'w')
	fp.write(browser.response().read())
	fp.close()

	if len(browser.form.controls) > 1:
		print ' - Multiple form controls found.  Saving to %s...' % filename
		print ' - Exiting.'
		sys.exit()
	else:
		print ' - Nothing to see here...'
	return browser

def main():
	start = datetime.datetime.now()
	print 'Starting at %s' % start

	browser = mechanize.Browser()
	browser.addheaders = [('User-Agent', USER_AGENT)]

	login(browser)
	check_queue(browser)

	while 1:
		delay = random.randint(30, 90)
		print 'Sleeping for %d seconds...\n' % delay
		time.sleep(delay)
		try:
			check_queue(browser, reload=True)
		except mechanize._response.httperror_seek_wrapper:
			print ' * Caught exception, restarting.'
			login(browser)
			check_queue(browser)


if __name__ == '__main__':
	main()
