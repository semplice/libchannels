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

import logging

import apt_pkg
import aptsources.sourceslist

logger = logging.getLogger(__name__)

# Sourceslist
sourceslist = aptsources.sourceslist.SourcesList()

def lock(
	lock_failed_callback=None
):
	
	"""
	Function decorator that ease the creation of APT-Locked methods.
	"""
	
	def decorator(obj):
		"""
		Modifies the object.
		"""
		
		def wrapper(self, *args, **kwargs):
			"""
			The function wrapper.
			"""
			
			try:
				with apt_pkg.SystemLock():
					return obj(self, *args, **kwargs)
			except SystemError as e:
				# Lock failed
				logger.error("Unable to create a SystemLock: %s" % e)
				
				# A bit convoluted here, but we should test for both
				# the existence of lock_failed_callback and of the callback
				# it references
				if lock_failed_callback and hasattr(self, lock_failed_callback):
					callback = getattr(self, lock_failed_callback)
					if callback:
						callback()
		
		# Merge metadata
		wrapper.__name__ = obj.__name__
		wrapper.__dict__.update(obj.__dict__)
		
		return wrapper
	
	return decorator
