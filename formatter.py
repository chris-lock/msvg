from optparse import OptionParser
from collections import namedtuple
from sys import stdout

Step = namedtuple('Step', 'start update finish')

class Formatter:
	def __init__(self, module_name = ''):
		self.__step_started = False
		self.__step_name = ''
		self.__step_index = 1
		self.__step_total = 1
		self.__prefix = self.__output_format('<b>' + module_name + '</b>: ')
		self.option_parser = OptionParser()
		self.step = Step(
			self.__step_start,
			self.__step_update,
			self.__step_finish
		)

	def usage_error(self, message):
		self.option_parser.print_usage()
		self.error(message)

	def error(self, message):
		self.message('\a' + message)

	def message(self, message):
		print self.format(message)

	def format(self, message):
		return self.__output(self.__prefix + message)

	def __output(self, message):
		return u'' + self.__output_format(message)

	def __output_format(self, message):
		return message.replace('<b>', '\033[1m').replace('</b>', '\033[0m')

	def __step_start(self, name, total = 1):
		if self.__step_started:
			self.__step_finish()
		else:
			self.__step_started = True

		self.__step_name = name
		self.__step_total = total
		self.__print(name)

		return self.step

	def __print(self, message):
		stdout.write('')
		stdout.flush()
		stdout.write(self.__output(message) + '\r')

	def __step_update(self):
		self.__print(self.__step_name + ' (' + str(self.__step_index) + '/' + str(self.__step_total) + ')')
		self.__step_index += 1

		return self.step

	def __step_finish(self, message = ''):
		if message:
			message += '\n'

		self.__step_index = 1
		self.__print('\n' + message)

		return self.step