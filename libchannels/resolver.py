# -*- coding: utf-8 -*-
#
# libchannels - update channels management library
# Copyright (C) 2015 Eugenio "g7" Paolantonio
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

from libchannels.relations import Dependency

class DependencyResolver:
	
	"""
	The DependencyResolver() object handles relations between more
	channels and providers.
	"""
	
	relations = {}
	
	def __init__(self, cache):
		"""
		Initializes the object.
		"""
		
		self.cache = cache
		
		# Build relations for every channel
		for channel in self.cache:
			self.build_relations(channel)
	
	def build_relations(self, channel):
		"""
		Builds the relations links of a channel.
		"""
		
		# Create the list where storing relations at
		self.relations[channel] = []
		
		for dependency in self.cache[channel].get_dependencies():
			print("Channel %s depends on %s" % (channel, dependency))
			self.relations[channel].append(Dependency(self.cache[dependency]))
	
	def is_channel_enableable(self, channel):
		"""
		Returns True it the channel can be enabled, False if not.
		"""
		# Sorry about the "enableable" - I haven't come up with a better word.
		
		return (not (False in self.relations[channel]))
