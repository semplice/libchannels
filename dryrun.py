#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

import libchannels.channel
import libchannels.discovery
import libchannels.resolver

discovery = libchannels.discovery.ChannelDiscovery()

discovery.discover()


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

sys.exit(0)

# Disable sample
if ("sample" in discovery.channels):
	print("Disabling sample")
	discovery.channels["sample"].disable()
else:
	print("Enabling sample")
	discovery.cache["sample"].enable()
