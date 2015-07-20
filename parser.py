from collections import namedtuple
from formatter import Formatter
from xml.etree import ElementTree
from config import Config
from os import path, listdir, makedirs
from copy import deepcopy

Optparse = namedtuple('Optparse', 'usage options groups')

Option = namedtuple('Option', 'argv kwargs')

OptionGroup = namedtuple('OptionGroup', 'title description options')

Node = namedtuple('Node', 'value matches')

class ColorOption(Option):
	def __new__(self, argv, name):
		return Option.__new__(self, argv, {
			'help': 'color for ' + name,
			'metavar': '#NNNNNN',
			'type': 'string',
			'action': 'store',
			'dest': name,
			'default': ''
		})

class Parser:
	OPTPARSE = Optparse(
		'(input.svg|input/file.svg) (output.svg|output/file.svg) -args', [
			Option(['-z', '--zoom'], {
				'help': 'zoom of the svg map',
				'metavar': '(14000|43000)',
				'type': 'choice',
				'action': 'store',
				'dest': 'zoom',
				'choices': ['14000', '43000'],
				'default': '14000'
			}),
			Option(['-e', '--expand'], {
				'help': 'expands each file into files for each layer',
				'action': 'store_true',
				'dest': 'expand',
				'default': False
			})
		], [
			OptionGroup('Colors', '', [
				ColorOption(['-r', '--roads'], 'roads'),
				ColorOption(['-b', '--buildings'], 'buildings'),
				ColorOption(['-p', '--parks'], 'parks'),
			])
		],
	)
	__NAMESPACE = 'http://www.w3.org/2000/svg'
	__SVG = {'svg': __NAMESPACE}

	def __init__(self):
		self.__xml_tree = ElementTree
		self.__is_expanded = False
		self.__config = {}
		self.__colors = {}
		self.__remove_nodes = []
		self.__replace_nodes = []
		self.__expanded_nodes = []
		self.formatter = Formatter()

		self.__xml_tree.register_namespace('', self.__NAMESPACE)

	def is_valid_args(self, args):
		if len(args) != 2:
			return (False, 'takes two arguments')

		if not path.isfile(args[0]) and not path.isdir(args[0]):
			return (False, 'argument 1 must be a file or directory')

		return (True, '')

	def parse_args(self, options, args):
		dest = args[1]

		if path.exists(dest):
			self.formatter.usage_error(dest + ' already exists')
		else:
			try:
				self.__parse(options, args[0], dest)
			except KeyboardInterrupt, SystemExit:
				self.formatter.step.finish('Interrupted')

	def __parse(self, options, source, dest):
		self.__set_options(options)
		self.__set_nodes()

		if path.isdir(source):
			self.__parse_dir(source, dest)
		else:
			self.__parse_file(source, dest)

		self.formatter.step.finish('Finished')

	def __set_options(self, options):
		self.__is_expanded = options.expand
		self.__config = Config().get(options.zoom)
		self.__colors = {
			'buildings': options.buildings,
			'parks': options.parks,
			'roads': options.roads,
		}

	def __set_nodes(self):
		self.formatter.step.start('Setting up layers', len(self.__config))

		if self.__is_expanded:
			self.__set_nodes_for_expanded()
		else:
			self.__set_nodes_for_layers()

	def __set_nodes_for_expanded(self):
		for node_name, layer in self.__config.iteritems():
			layer_nodes = layer.empty_nodes + layer.remove_nodes + layer.replace_nodes

			self.__expanded_nodes.append(Node(node_name, layer_nodes))

			self.formatter.step.update()

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

			self.formatter.step.update()

		self.__replace_nodes.append(Node('', empty_nodes))

	def __parse_dir(self, source, dest):
		makedirs(dest)

		for file_name in listdir(source):
			if file_name.endswith('.svg'):
				self.__parse_file(
					path.join(source, file_name),
					path.join(dest, file_name)
				)

	def __parse_file(self, source, dest):
		self.formatter.step.start('Parsing <b>' + source + '</b>')

		tree = self.__xml_tree.parse(source)
		root = tree.getroot()

		self.__remove_defs(root)

		if not self.__is_expanded:
			self.__create_layer_file(tree, root, dest)
		else:
			self.__create_expanded_files(tree, root, dest)

	def __remove_defs(self, root):
		defses = root.findall('svg:defs', self.__SVG)

		self.formatter.step.start('Removing <defs>', len(defses))

		for defs in defses:
			root.remove(defs)

			self.formatter.step.update()

	def __create_layer_file(self, tree, root, dest):
		self.__update_groups_for_layers(root)

		self.formatter.step.start('Saving <b>' + dest + '</b>')
		tree.write(dest)

	def __update_groups_for_layers(self, root):
		groups = root.findall('svg:g', self.__SVG)

		for group in groups:
			self.__remove_gs(group)
			self.__update_layers(group)

	def __remove_gs(self, group):
		sub_groups = group.findall('svg:g', self.__SVG)

		self.formatter.step.start('Removing <g>', len(sub_groups))

		for sub_group in sub_groups:
			group.remove(sub_group)

			self.formatter.step.update()

	def __update_layers(self, group):
		self.__for_all_group_nodes(group, self.__update_node_for_layer, self.__remove_nodes)

	def __for_all_group_nodes(self, group, method, matches):
		nodes = (group.findall('svg:path', self.__SVG) + group.findall('svg:rect', self.__SVG))

		self.formatter.step.start('Updating layers', len(nodes))

		for node in nodes:
			method(group, node, node.get('style'), matches)

			self.formatter.step.update()

	def __update_node_for_layer(self, group, node, style, matches):
		if any(match in style for match in matches):
			group.remove(node)
		else:
			for replace_node in self.__replace_nodes:
				for match in replace_node.matches:
					style = style.replace(match, replace_node.value)

			node.set('style', style)

	def __create_expanded_files(self, tree, root, dest):
		groups = root.findall('svg:g', self.__SVG)

		for group in groups:
			self.__remove_gs(group)

		for expanded_node in self.__expanded_nodes:
			self.__create_expanded_layer_files(deepcopy(tree), expanded_node, dest)

	def __create_expanded_layer_files(self, tree, expanded_node, dest):
		expanded_dest = self.__get_expanded_dest(expanded_node.value, dest)

		for group in tree.getroot().findall('svg:g', self.__SVG):
			self.__for_all_group_nodes(group, self.__update_node_for_expanded, expanded_node.matches)

		self.formatter.step.start('Saving <b>' + expanded_dest + '</b>')
		tree.write(expanded_dest)

	def __get_expanded_dest(self, expanded_node_value, dest):
		expanded_node_name = expanded_node_value.replace(' ', '-')

		return('-' + expanded_node_name + '.svg').join(dest.rsplit('.svg'))

	def __update_node_for_expanded(self, group, node, style, matches):
		if not any(match in style for match in matches):
			group.remove(node)