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

from enum import Enum

class ActionType(Enum):
	"""
	The ActionType enum.
	"""
	
	DISABLE = 1
	ENABLE = 2

class Actions:
	
	"""
	The Actions() class permits to easily handle actions to be taken
	on channels.
	"""
	
	def __init__(self, discovery, resolver):
		"""
		Initializes the class.
		"""
		
		self.discovery = discovery
		self.resolver = resolver
	
	def enable_channel(self, channel):
		"""
		Enables the given channel.
		"""
		
		if self.discovery.cache[channel].enabled:
			# Nothing to do
			return
		
		for child_channel, action in self.resolver.get_channel_solution(channel, ActionType.ENABLE):
			if action == ActionType.ENABLE:
				self.discovery.cache[child_channel].enable()
			elif action == ActionType.DISABLE:
				self.discovery.cache[child_channel].disable()
	
	def disable_channel(self, channel):
		"""
		Disables the given channel.
		"""
		
		if not self.discovery.cache[channel].enabled:
			# Nothing to do
			return
		
		for child_channel, action in self.resolver.get_channel_solution(channel, ActionType.DISABLE):
			if action == ActionType.ENABLE:
				self.discovery.cache[child_channel].enable()
			elif action == ActionType.DISABLE:
				self.discovery.cache[child_channel].disable()
