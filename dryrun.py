#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

import libchannels.channel
import libchannels.discovery
import libchannels.resolver

from libchannels.actions import ActionType

discovery = libchannels.discovery.ChannelDiscovery()

discovery.discover()

if (not "semplice-devel" in discovery.channels):
	discovery.cache["semplice-devel"].enable()

print(discovery.channels)

resolver = libchannels.resolver.DependencyResolver(discovery.cache)
print(resolver.relations)
print(resolver.relations["semplice-jessie"][0])
if resolver.relations["semplice-jessie"][0]:
	print("NO")
else:
	print("YE")
print("semplice-current", not (False in resolver.relations["semplice-current"]))
print(resolver.is_channel_enableable("semplice-jessie"))

print("semplice-current enabled: %s" % discovery.cache["semplice-current"].enabled)

# Print blockers for some channels
for channel in ["semplice-current", "semplice-jessie"]:
	print("%s blockers: %s" % (channel, resolver.get_channel_blockers(channel)))
	print("%s solution: %s" % (channel, resolver.get_channel_solution(channel, ActionType.ENABLE)))

print("%s blockers: %s" % ("sid", resolver.get_channel_blockers("sid", ActionType.DISABLE)))
print("%s solution: %s" % ("sid", resolver.get_channel_solution("sid", ActionType.DISABLE)))

sys.exit(0)

# Disable sample
if ("sample" in discovery.channels):
	print("Disabling sample")
	discovery.channels["sample"].disable()
else:
	print("Enabling sample")
	discovery.cache["sample"].enable()
