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

import os
import configparser

import libchannels.common
import libchannels.config

class Provider(configparser.ConfigParser):
	
	"""
	A Provider is a virtual channel that can be used as an alias for a
	set of channels.
	In this way, channels could depend on a provider which in turn can be
	statisfied by one or more channels.
	
	As an example, the "semplice-base" provider is statisfied by both the
	"semplice-current" channel and the "semplice-jessie" channel.
	Another channel may depend on "semplice-base.provider" to ensure
	that the channel is enabled in a Semplice system, without forcing the
	version on it.
	
	Another plus of providers is that they ease the management of channels
	with the same scope.
	Following the previous example, enabling the "semplice-current" channel
	while "semplice-jessie" is already enabled will disable the latter, because
	they refer to the same provider.
	
	Defining a provider is pretty straightforward:
	
		[provider]
		name = My provider
		description = My description
	
	Note that when referring to a provider from the outside (== a channel most
	of the time) the ".provider" extension is needed, otherwise it will be treated
	like a channel.
	
	"""

	def __init__(self, provider_name):
		"""
		Initializes the class.
		"""
		
		super().__init__()
		
		self.repositories = {}
		
		self.provider_name = provider_name
		
		self.read(os.path.join(libchannels.config.CHANNEL_SEARCH_PATH, "%s.provider" % provider_name))
	
	def __str__(self):
		"""
		Returns a stringified version of the object.
		"""
		
		return self["provider"]["name"]
