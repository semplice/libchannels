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
from libchannels.actions import ActionType

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
	
	def get_channel_solution(self, channel, action=ActionType.ENABLE):
		"""
		Returns a list of key,value pairs containing the steps to
		take to accomplish the given action, or None if nothing could
		be done.
		"""
		
		result = []

		blockers = self.get_channel_blockers(channel, action=action)
		
		for blocker in blockers:
			if type(blocker) == Dependency:
				# Get solution for the given dependency
				solutions = self.get_channel_solution(blocker.get_name(), ActionType.ENABLE)
			if type(blocker) == Conflict:
				# Get solution for the given conflict
				solutions = self.get_channel_solution(blocker.get_name(), ActionType.DISABLE)
			elif type(blocker) == ProviderRelation:
				# Get solution for the given provider relation
				solutions = self.get_channel_solution(blocker.get_current_provider_channel(), ActionType.DISABLE)
		
			if solutions != None:
				result += [solution for solution in solutions if not solution in result]
			else:
				# Nothing to do
				return None		
		
		# Finally add actual action
		result.append((channel, action))
		
		return result
	
	def get_channel_blockers(self, channel, action=ActionType.ENABLE):
		"""
		Returns a list of relations to statisfy before the given channel
		can be marked as "enableable".
		"""
		
		if action == ActionType.ENABLE:
			return [relation for relation in self.relations[channel] if not relation]
		elif action == ActionType.DISABLE:
			compare_relation = Dependency(self.cache[channel])
			
			# Simply build a list of Conflicts for the channels which depend
			# on the one we want to remove
			return [
				Conflict(self.cache[name])
				for name, relations in self.relations.items()
				if compare_relation in relations and self.cache[name].enabled
			]
	
	def is_channel_enableable(self, channel):
		"""
		Returns True it the channel can be enabled, False if not.
		"""
		# Sorry about the "enableable" - I haven't come up with a better word.
		
		return (not (False in self.relations[channel]))
