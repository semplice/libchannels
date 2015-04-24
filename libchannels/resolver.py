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

from libchannels.relations import Dependency, Conflict, ProviderRelation

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
			if not channel.endswith(".provider"):
				self.build_relations(channel)
	
	def build_relations(self, channel):
		"""
		Builds the relations links of a channel.
		"""
		
		# Create the list where storing relations at
		self.relations[channel] = []
		
		for dependency in self.cache[channel].get_dependencies():
			self.relations[channel].append(
				Dependency(
					self.cache[dependency]
				)
			)
		
		for conflict in self.cache[channel].get_conflicts():
			self.relations[channel].append(
				Conflict(
					self.cache[conflict]
				)
			)
		
		# Handle provider relation
		for provider in self.cache[channel].get_providers():
			self.relations[channel].append(
				ProviderRelation(
					self.cache[channel],
					self.cache[provider],
					self.cache
				)
			)
	
	def get_channel_blockers(self, channel):
		"""
		Returns a list of relations to statisfy before the given channel
		can be marked as "enableable".
		"""
		
		result = []
		for relation in self.relations[channel]:
			if not relation:
				result.append(relation)
		
		return result
	
	def is_channel_enableable(self, channel):
		"""
		Returns True it the channel can be enabled, False if not.
		"""
		# Sorry about the "enableable" - I haven't come up with a better word.
		
		return (not (False in self.relations[channel]))
