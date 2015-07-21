from collections import namedtuple
from optparse import OptionParser, OptionGroup
from formatter import Formatter

CliConfig = namedtuple('CliConfig', 'usage options groups')

CliOption = namedtuple('CliOption', 'argv kwargs')

CliGroup = namedtuple('CliGroup', 'title description options')

class Cli:
	def __init__(self, module_name, config, parser):
		self.__parser = parser
		self.formatter = Formatter(module_name)
		self.__option_parser = self.__get_option_parser(config, parser)

		self.formatter.option_parser = self.__option_parser

	def parse_args(self):
		return self.__option_parser.parse_args()

	def __get_option_parser(self, config, parser):
		option_parser = OptionParser(self.formatter.format(config.usage))

		self.__add_options(config, parser, option_parser)
		self.__add_option_groups(config, option_parser, parser)

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