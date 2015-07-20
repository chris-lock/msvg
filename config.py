from collections import namedtuple

MapLayer = namedtuple('MapLayer', 'empty_nodes replace_nodes remove_nodes')

class MapRemoveLayer(MapLayer):
	def __new__(self, remove):
		return MapLayer.__new__(self, [], [], remove)

class Config:
	__BASE = {
		'roads': MapLayer([
			], [
				'rgb(53.72549%,64.313725%,79.607843%)',			# blue road
				'rgb(58.039216%,83.137255%,58.039216%)',		# green road
				'rgb(60%,60%,60%)',								# road at Yeshiva University
				'rgb(60%,80%,80%)',								# light grey roads
				'rgb(66.666667%,66.666667%,66.666667%)',		# grey roads
				'rgb(86.666667%,62.352941%,62.352941%)',		# red road
				'rgb(86.666667%,86.666667%,86.666667%)',		# cul de sac in NJ
				'rgb(88.627451%,90.980392%,94.901961%)',		# light blue roads (tunnels)
				'rgb(94.901961%,94.901961%,94.901961%)',		# light grey roads
				'rgb(97.254902%,97.254902%,72.941176%)',		# yellow road
				'rgb(97.647059%,83.921569%,66.666667%)',		# brown road
				'rgb(98.039216%,98.039216%,81.960784%)',		# light yellow road
				'rgb(100%,100%,100%)',							# white roads
			], [
				'rgb(46.666667%,53.333333%,63.137255%)',		# blue road underside
				'rgb(49.411765%,68.235294%,49.411765%)', 		# green road underside
				'rgb(73.333333%,73.333333%,73.333333%)',		# white road underside
				'rgb(77.254902%,48.235294%,49.411765%)',		# red road underside
				'rgb(77.647059%,77.647059%,54.117647%)',		# yellow road underside
				'rgb(80%,63.137255%,41.568627%)', 				# brown road underside
				'rgb(91.764706%,77.254902%,77.254902%)',		# blue road underside
		]),
		'buildings': MapLayer([
				'stroke:rgb(72.54902%,66.27451%,61.176471%);',	# grey building outline
			], [
				'rgb(68.627451%,61.176471%,55.294118%)',		# buildings
				'rgb(83.137255%,66.666667%,66.666667%)',		# grand central
				'rgb(94.901961%,85.490196%,85.098039%)',		# buildings
				'rgb(92.941176%,86.666667%,78.823529%)',		# buildings
				'rgb(81.960784%,77.647059%,74.117647%)',		# buildings
				'rgb(85.098039%,81.568627%,78.823529%)',		# buidlings
				'rgb(71.372549%,70.980392%,57.254902%)',		# construction
			], [
		]),
		'parks': MapLayer([
			], [
				'rgb(20%,80%,60%)',								# field on Hudson pier and Central Park squares
				'rgb(54.117647%,82.745098%,68.627451%)',		# Pier 40 soccer field
				'rgb(62.745098%,81.176471%,52.156863%)',		# parks near UN
				'rgb(70.980392%,89.019608%,70.980392%)',		# parks in NJ
				'rgb(80%,100%,94.509804%)',						# grey squares in Stuy Town
				'rgb(80.392157%,96.862745%,78.823529%)',		# parks
				'rgb(92.941176%,92.941176%,92.941176%)',		# highline and park paths
			], [
				'rgb(45.490196%,86.27451%,72.941176%)',			# stadiums
				'rgb(66.666667%,79.607843%,68.627451%)',		# sports fields
				'rgb(68.235294%,81.960784%,62.745098%)',		# second layer of Byrant Square Park
				'rgb(81.176471%,92.54902%,65.882353%)',			# central park patches
				'rgb(93.72549%,83.921569%,70.980392%)',			# weird parks in NJ
		]),
		'city blocks': MapRemoveLayer([
				'rgb(88.235294%,88.235294%,88.235294%)',		# city blocks like Stuy Town
				'rgb(91.372549%,90.588235%,88.627451%)',		# docks
				'rgb(92.156863%,85.882353%,90.980392%)',		# city blocks
				'rgb(94.901961%,93.72549%,91.372549%)',			# city blocks piers and paths
		]),
		'water': MapRemoveLayer([
				'rgb(70.980392%,81.568627%,81.568627%)',		# water
		]),
		'trains': MapRemoveLayer([
				'rgb(47.45098%,50.588235%,69.019608%)',			# subway stations
				'rgb(52.54902%,52.54902%,52.54902%)',			# trains in NJ
		]),
		'labels': MapRemoveLayer([
				'fill:rgb(100',
				'fill:rgb(46.666',
				'rgb(0%,57.254902%,85.490196%)',				# parking
				'rgb(30.196078%,30.196078%,30.196078%)',
				'rgb(52.941176%,67.058824%,52.941176%)',
				'rgb(73.333333%,48.235294%,49.803922%)',
				'rgb(76.862745%,77.647059%,56.078431%)',
				'rgb(77.647059%,67.843137%,51.764706%)',
				'rgb(81.568627%,56.078431%,33.333333%)',
				'rgb(85.490196%,0%,57.254902%)',				# hospital
		]),
		'misc': MapRemoveLayer([
				'opacity:0',
				'rgb(0%,0%,0%)',								# underside
				'rgb(17.254902%,55.294118%,55.294118%)',
				'rgb(33.333333%,33.333333%,33.333333%)',
				'rgb(46.666667%,46.666667%,46.666667%)',		# shipping yard
				'rgb(50.196078%,50.196078%,50.196078%)',
				'rgb(64.705882%,16.470588%,16.470588%)',
				'rgb(80%,80%,80%)',								# hidden under George Washington Bridge ramp
				'rgb(80.392157%,80%,78.823529%)',				# underside of buildings
				'rgb(87.058824%,96.470588%,75.294118%)',		# stoke: none
				'rgb(94.117647%,94.117647%,84.705882%)',		# underside of buildings
				'rgb(96.862745%,93.72549%,71.764706%)',			# patches under Lincoln Center
				'rgb(98.431373%,88.235294%,76.078431%)',		# Columbia University concourse
				'stroke:rgb(0%,60%,43.529412%)',
		]),
	}
	__ZOOM = {
		'14000': {
			'lines': MapRemoveLayer([
					'dasharray',
					'stroke-width:0.2',								# dock outlines
					'stroke-width:0.3',								# park outlines
					'stroke-width:0.5', 							# stadium outlines
					'url(#pattern',
					'stroke-width:2;stroke-linecap:butt;'			# road labels
					'stroke-linejoin:round;'						#
					'stroke:rgb(100%,100%,100%);',					#
			]),
		},
		'43000': {
			'lines': MapRemoveLayer([
					'dasharray',
					'stroke-width:0.2',								# dock outlines
					'stroke-width:0.3',								# park outlines
					'stroke-width:0.5', 							# stadium outlines
					'url(#pattern',
			]),
		},
	}

	def get(self, key):
		config = self.__BASE.copy()
		config.update(self.__ZOOM[key])

		return config