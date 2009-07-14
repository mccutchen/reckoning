#!/usr/bin/env python

import datetime
import functools
import hashlib
import logging
import random
import re
import sys
import time

import mechanize

# Reckoning configuration
import config

# Keep track of which job IDs we have seen, so we don't sign up for
# the same one again if it is manually removed from the pipeline
JOB_COUNT = 0
SEEN_JOBS = []

def main():
	"""The program's main loop.  Creates a browser object, signs it in
	to the site, and then polls the queue page at random intervals
	looking for new jobs."""

	start = datetime.datetime.now()
	print 'Starting at %s' % start

	# Get a browser object to work with and log in to the site
	browser = get_browser()
	login(browser)

	# Until an error occurs or the maximum number of jobs have been
	# fetched, check on the job queue at random intervals
	while 1:
		check_queue(browser)

		delay = random.randint(config.min_delay, config.max_delay)
		print 'Sleeping for %d seconds...\n' % delay
		time.sleep(delay)

def login(browser):
	"""Logs the browser object in to the AppraisalZone web site with
	the global credentials."""
	print 'Logging in...'
	browser.open(config.login_url)
	browser.select_form(nr=0)
	browser[config.username_field] = config.username
	browser[config.password_field] = config.password
	browser.submit()
	return browser

def check_queue(browser):
	"""Checks the queue page to see if there are any jobs listed on
	it.  If so, tries to sign up for the first job available."""

	print 'Checking queue...'
	browser.open(config.queue_url)
	browser.select_form(nr=0)
	if filter(job_filter, browser.form.controls):
		return get_job(browser)
	else:
		print ' - Found no jobs...'
	return browser

def get_job(browser):
	"""Signs up for the first job in the queue."""
	global JOB_COUNT, SEEN_JOBS

	timestamp = time.strftime('%Y%m%d-%H%M%S')

	filename = 'output/queue-%s.html' % timestamp
	print ' * Writing queue response to %s...' % filename
	file(filename, 'w').write(browser.response().read())

	# Get the first job control from the list, and determine the job
	# id number and the name of the control expected by the ASP.NET
	# postback machinery.
	job_controls = filter(job_filter, browser.form.controls)
	job_control = job_controls[0]
	control_name, job_id = get_job_id(job_control)

	# Skip jobs we've already signed up for once (for when Kyle
	# manually removes jobs from his pipeline)
	if job_id in SEEN_JOBS:
		print ' * Skipping previously-accepted job #%s...' % job_id
		return browser

	# Set the appropriate values on the form
	job_control.value = ['1']

	# Dumb ASP.NET postback stuff which is set in JavaScript in a real
	# browser.  The fields are hidden, so they need to be marked as
	# not readonly before we can set their values.
	c = browser.form.find_control('__EVENTTARGET')
	c.readonly = False
	c.value = control_name

	c = browser.form.find_control('__EVENTARGUMENT')
	c.readonly = False
	c.value = job_id

	# Submit the form
	print ' * Getting job id %s...' % job_id
	browser.submit()
	JOB_COUNT += 1
	SEEN_JOBS.append(job_id)

	filename = 'output/response-%s.html' % timestamp
	print ' * Writing post-submit response to %s...' % filename
	file(filename, 'w').write(browser.response().read())

	# If we've hit the job limit for this session, exit
	if JOB_COUNT >= config.job_limit:
		print ' * Reached job limit for this session.'
		print ' * Exiting.'
		sys.exit()

	# Check the queue again immediately, to see if there are any more
	# jobs available
	return check_queue(browser)


######################################################################
# Utility functions
######################################################################
def get_job_id(control):
	"""Pulls the ASP.NET postback control name and the job id out of
	the 'onclick' event associated with the given control, which
	should be a radio control representing the yes or no answers for
	signing up for a job in the queue."""
	assert len(control.items) == 2, \
		'Expected 2 items in the radio control, got %d' % len(control.items)
	item = control.items[-1]

	assert 'onclick' in item.attrs, \
		'No onclick handler found for item %s' % item.id
	onclick = item.attrs['onclick']

	job_id_pattern = r"\('([\w$]+)','(\d+)'\)"
	match = re.search(job_id_pattern, onclick)
	assert match is not None, \
		'No job ID found in onclick event: %s' % onclick

	return match.groups()

def job_filter(control):
	"""Filter function used to extract the job controls from the queue
	form."""
	return control.type == 'radio'

def setup_debug(browser):
	"""Makes the browser print debugging information."""
	browser.set_debug_redirects(True)
	# browser.set_debug_responses(True)
	browser.set_debug_http(True)

	logger = logging.getLogger("mechanize")
	logger.addHandler(logging.StreamHandler(sys.stdout))
	logger.setLevel(logging.DEBUG)

	return browser

def get_browser():
	"""Creates a browser object and prepares it to masquerade as a
	real web browser by making it send appropriate headers with its
	requests."""
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
		('Connection', 'keep-alive')]

	browser.set_handle_robots(False)
	return browser


if __name__ == '__main__':
	main()
