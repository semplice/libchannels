#!/usr/bin/python3
# -*- coding: utf-8 -*-

import libchannels.channel
import libchannels.discovery

discovery = libchannels.discovery.ChannelDiscovery()

discovery.discover()


print(discovery.channels)

# Disable sample
if ("sample" in discovery.channels):
	print("Disabling sample")
	discovery.channels["sample"].disable()
else:
	print("Enabling sample")
	discovery.cache["sample"].enable()
