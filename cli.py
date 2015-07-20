from optparse import OptionParser, OptionGroup
from formatter import Formatter

class Cli:
	__MODULE_NAME = 'msvg'

	def __init__(self, parser):
		self.__parser = parser
		self.__formatter = Formatter(self.__MODULE_NAME)
		self.__option_parser = self.__get_option_parser(self.__parser)

		self.__formatter.option_parser = self.__option_parser
		self.__parser.formatter = self.__formatter

	def run(self):
		options, args = self.__option_parser.parse_args()
		is_valid, validation_message = self.__parser.is_valid_args(args)

		if is_valid:
			self.__parser.parse_args(options, args)
		else:
			self.__formatter.usage_error(validation_message)

	def __get_option_parser(self, parser):
		option_parser = OptionParser(self.__formatter.format(parser.OPTPARSE.usage))

		self.__add_options(parser.OPTPARSE, parser, option_parser)
		self.__add_option_groups(parser.OPTPARSE, option_parser, parser)

		return option_parser

	def __add_options(self, group, parser, option_parser):
		for option in group.options:
			self.__add_option(parser, option, option_parser)

	def __add_option(self, parser, option, option_parser):
		kwargs = self.__get_option_kwargs(parser, option.kwargs)
		option_parser.add_option(*option.argv, **kwargs)

	def __get_option_kwargs(self, parser, kwargs):
		if 'callback' in kwargs:
			kwargs['callback'] = getattr(parser, kwargs['callback'])

		return kwargs

	def __add_option_groups(self, config, option_parser, parser):
		for group in config.groups:
			self.__add_option_group(option_parser, group, parser)

	def __add_option_group(self, option_parser, group, parser):
		option_parser_group = OptionGroup(
			option_parser,
			group.title,
			group.description
		)
		self.__add_options(group, parser, option_parser_group)
		option_parser.add_option_group(option_parser_group)