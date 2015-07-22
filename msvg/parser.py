from collections import namedtuple
from cli import CliConfig, CliOption, CliGroup, Cli
from xml.etree import ElementTree
from config import Config
from os import path, listdir, makedirs
from copy import deepcopy

Node = namedtuple('Node', 'value matches')

class ColorOption(CliOption):
	def __new__(self, argv, name):
		return CliOption.__new__(self, argv, {
			'help': 'color for ' + name,
			'metavar': '#HEX',
			'type': 'string',
			'action': 'store',
			'dest': name,
			'default': ''
		})

class Parser:
	__MODULE_NAME = 'msvg'
	__CLI = CliConfig(
		'(input.svg|input/file.svg) (output.svg|output/file.svg) -args', [
			CliOption(['-z', '--zoom'], {
				'help': 'zoom of the svg map',
				'metavar': '(14000|43000)',
				'type': 'choice',
				'action': 'store',
				'dest': 'zoom',
				'choices': ['14000', '43000'],
				'default': '14000'
			}),
			CliOption(['-e', '--expand'], {
				'help': 'expands each file into files for each layer',
				'action': 'store_true',
				'dest': 'expand',
				'default': False
			})
		], [
			CliGroup('Colors', '', [
				ColorOption(['-r', '--roads'], 'roads'),
				ColorOption(['-b', '--buildings'], 'buildings'),
				ColorOption(['-p', '--parks'], 'parks'),
			])
		],
	)
	__NAMESPACE = 'http://www.w3.org/2000/svg'
	__SVG = {'svg': __NAMESPACE}

	def __init__(self):
		self.__cli = Cli(self.__MODULE_NAME, self.__CLI, self)
		self.__xml_tree = ElementTree
		self.__is_expanded = False
		self.__config = {}
		self.__colors = {}
		self.__remove_nodes = []
		self.__replace_nodes = []
		self.__expanded_nodes = []

		self.__xml_tree.register_namespace('', self.__NAMESPACE)

	def cli(self):
		options, args = self.__cli.parse_args()
		is_valid, validation_message = self.__is_valid_args(args)

		if is_valid:
			self.__parse_args(options, args)
		else:
			self.__cli.formatter.usage_error(validation_message)

	def __is_valid_args(self, args):
		if len(args) != 2:
			return (False, 'takes two arguments')

		if not path.isfile(args[0]) and not path.isdir(args[0]):
			return (False, 'argument 1 must be a file or directory')

		return (True, '')

	def __parse_args(self, options, args):
		dest = args[1]

		if path.exists(dest):
			self.__cli.formatter.usage_error(dest + ' already exists')
		else:
			try:
				self.__parse(options, args[0], dest)
			except KeyboardInterrupt, SystemExit:
				self.__cli.formatter.step.finish('Interrupted')

	def __parse(self, options, source, dest):
		self.__set_options(options)
		self.__set_nodes()

		if path.isdir(source):
			self.__parse_dir(source, dest)
		else:
			self.__parse_file(source, dest)

		self.__cli.formatter.step.finish('Finished')

	def __set_options(self, options):
		self.__is_expanded = options.expand
		self.__config = Config().get(options.zoom)
		self.__colors = {
			'buildings': options.buildings,
			'parks': options.parks,
			'roads': options.roads,
		}

	def __set_nodes(self):
		self.__cli.formatter.step.start('Setting up layers', len(self.__config))

		if self.__is_expanded:
			self.__set_nodes_for_expanded()
		else:
			self.__set_nodes_for_layers()

	def __set_nodes_for_expanded(self):
		for node_name, layer in self.__config.iteritems():
			layer_nodes = layer.empty_nodes + layer.remove_nodes + layer.replace_nodes

			self.__expanded_nodes.append(Node(node_name, layer_nodes))

			self.__cli.formatter.step.update()

	def __set_nodes_for_layers(self):
		empty_nodes = []

		for node_name, layer in self.__config.iteritems():
			empty_nodes += layer.empty_nodes
			self.__remove_nodes += layer.remove_nodes

			if node_name in self.__colors and self.__colors[node_name]:
				self.__replace_nodes.append(
					Node(self.__colors[node_name], layer.replace_nodes)
				)
			else:
				self.__remove_nodes += layer.replace_nodes

			self.__cli.formatter.step.update()

		self.__replace_nodes.append(Node('', empty_nodes))

	def __parse_dir(self, source, dest):
		self.__create_dest_dir(dest)

		for file_name in listdir(source):
			if file_name.endswith('.svg'):
				self.__parse_file(
					path.join(source, file_name),
					path.join(dest, file_name)
				)

	def __create_dest_dir(self, dest):
		self.__cli.formatter.step.start('Creating <b>' + dest + '</b> directory')

		makedirs(dest)

	def __parse_file(self, source, dest):
		self.__cli.formatter.step.start('Parsing <b>' + source + '</b>')

		tree = self.__xml_tree.parse(source)
		root = tree.getroot()

		self.__remove_defs(root)

		if not self.__is_expanded:
			self.__create_layer_file(root, dest, tree)
		else:
			self.__create_expanded_files(source, dest, root, tree)

	def __remove_defs(self, root):
		defses = root.findall('svg:defs', self.__SVG)

		self.__cli.formatter.step.start('Removing <defs>', len(defses))

		for defs in defses:
			root.remove(defs)

			self.__cli.formatter.step.update()

	def __create_layer_file(self, root, dest, tree):
		self.__remove_gs(root)
		self.__update_layers(root)
		self.__save_file(dest, tree)

	def __remove_gs(self, root):
		for group in self.__get_groups(root):
			sub_groups = self.__get_groups(group)

			self.__cli.formatter.step.start('Removing <g>', len(sub_groups))

			for sub_group in sub_groups:
				group.remove(sub_group)

				self.__cli.formatter.step.update()

	def __get_groups(self, base):
		return base.findall('svg:g', self.__SVG)

	def __update_layers(self, root):
		self.__for_all_group_nodes(root, self.__update_for_layer, self.__remove_nodes)

	def __for_all_group_nodes(self, root, method, matches):
		for group in self.__get_groups(root):
			nodes = (group.findall('svg:path', self.__SVG) + group.findall('svg:rect', self.__SVG))

			self.__cli.formatter.step.start('Updating layers', len(nodes))

			for node in nodes:
				method(group, node, node.get('style'), matches)

				self.__cli.formatter.step.update()

	def __update_for_layer(self, group, node, style, matches):
		if any(match in style for match in matches):
			group.remove(node)
		else:
			for replace_node in self.__replace_nodes:
				for match in replace_node.matches:
					style = style.replace(match, replace_node.value)

			node.set('style', style)

	def __save_file(self, file_name, tree):
		self.__cli.formatter.step.start('Saving <b>' + file_name + '</b>')
		tree.write(file_name)

	def __create_expanded_files(self, source, dest, root, tree):
		source_file_name = path.basename(source)
		clean_dest = path.splitext(dest)[0]

		self.__create_dest_dir(clean_dest)
		self.__remove_gs(root)

		for expanded_node in self.__expanded_nodes:
			self.__create_expanded_layer_files(clean_dest, expanded_node, source_file_name, deepcopy(tree))

		self.__create_remainder_layer(tree, source_file_name, clean_dest)

	def __create_expanded_layer_files(self, dest, expanded_node, source, tree):
		file_name = path.join(dest, self.__get_expanded_file_name(expanded_node.value, source))

		self.__for_all_group_nodes(tree.getroot(), self.__remove_all_non_matches, expanded_node.matches)
		self.__save_file(file_name, tree)

	def __get_expanded_file_name(self, expanded_node_value, source):
		expanded_node_name = expanded_node_value.replace(' ', '-')

		return ('-' + expanded_node_name + '.svg').join(source.rsplit('.svg'))

	def __remove_all_non_matches(self, group, node, style, matches):
		if not any(match in style for match in matches):
			group.remove(node)

	def __create_remainder_layer(self, tree, source, dest):
		all_matches = [matche for expanded_node in self.__expanded_nodes for matche in expanded_node.matches]

		self.__for_all_group_nodes(tree.getroot(), self.__remove_all_matches, all_matches)
		self.__save_file(path.join(dest, source), tree)

	def __remove_all_matches(self, group, node, style, matches):
		if any(match in style for match in matches):
			group.remove(node)

def cli():
	Parser().cli()