#!/usr/bin/env python3

import json
import os
import base64
from math import floor
from lxml import etree
from jinja2 import Environment, FileSystemLoader

# Open the specified JSON file
jsonfile  = open('test.json', mode='r')
inputdata = json.load(jsonfile)

# Loop through all the links defined in the JSON and deduplicate them, so every link is specified only once
#  This also makes sure the router with the lowest ID is mentioned first in the resulting dict
links = []
linkcounter = 1
for jump in inputdata['jumps']:
	if jump['from'] < jump['to']:
		router1 = jump['from']
		router2 = jump['to']
	else:
		router1 = jump['to']
		router2 = jump['from']
	
	link = {'id': linkcounter, 'router1': router1, 'router2': router2}

	if link not in links:
		links.append(link)

	linkcounter += 1

# Start creating the XML file needed for Eve-NG
lab_element = etree.Element('lab',
	name='Generated lab',
	id='38d9df61-a249-4988-bd4b-4fe5080b2865',
	version=str('1'),
	scripttimeout= str('300'),
	lock=str('0'),
	author='Cybertinus'
)
# Create the needed elements to define the physical topology in the lab
topology_element = etree.SubElement(lab_element, 'topology')
nodes_element = etree.SubElement(topology_element, 'nodes')

# Start to loop through all the nodes defined in the JSON
interfacecounter = {}
for node in inputdata['nodes']:
	# Define the node itself in the lab, a Cisco c7200 is used for this purpose
	node_element = etree.SubElement(nodes_element, 'node',
		id=str(node['id']),
		name=node['name'],
		type='dynamips',
		template='c7200',
		image='c7200-adventerprisek9-mz.152-4.M11.image',
		idlepc='0x62f21000',
		nvram=str('128'),
		ram=str('512'),
		console='',
		delay=str('0'),
		icon='Router.png',
		config=str('1'),
		left=str(node['x']),
		top=str(node['y'])
	)
	# Define which slots are in use in each router, only 1 8 port Ethernet module is used
	slot_element = etree.SubElement(node_element, 'slot',
		id=str('1'),
		module='PA-8E'
	)

	# Loop through all the links found, to have all the interfaces in the topology connect to the correct interface on the correct node
	for link in links:
		if link['router1'] == node['id'] or link['router2'] == node['id']:
			if node['id'] not in interfacecounter:
				interfacecounter[node['id']] = 16
			# The short interface name is needed in the Eve-NG XML, the long name is used in the Cisco configuration
			interface_name_short = 'e1/'+str(interfacecounter[node['id']] - 16)
			interface_name_long = 'Ethernet1/'+str(interfacecounter[node['id']] - 16)
			# Create the actual interface in the Eve-NG XML
			interface_element = etree.SubElement(node_element, 'interface',
				id=str(interfacecounter[node['id']]),
				name=interface_name_short,
				type='ethernet',
				network_id=str(link['id'])
			)
			# Increase the used interface counter for the correct router, so no interface is used twice
			if link['router1'] == node['id']:
				link['router1_interfacename'] = interface_name_long
				interfacecounter[link['router1']] += 1
			elif link['router2'] == node['id']:
				link['router2_interfacename'] = interface_name_long
				interfacecounter[link['router2']] += 1

# Add the networks to the topology
networks_element = etree.SubElement(topology_element, 'networks')
for link in links:
	networkname = 'Net-'
	for node in inputdata['nodes']:
		if node['id'] == link['router1']:
			networkname += node['name']
			break
	networkname += 'iface_'
	networkname += str(link['id'])

	network_element = etree.SubElement(networks_element, 'network',
		id=str(link['id']),
		type='bridge',
		name=networkname,
		left='0',
		top='0',
		visibility='0'
	)

# Create the needed objects to store the configuration for each router in
objects_element = etree.SubElement(lab_element, 'objects')
configs_element = etree.SubElement(objects_element, 'configs')

# Open the config template from the templates subdirectory
templates = Environment(loader=FileSystemLoader('templates'))
template = templates.get_template('baseconfig.j2')
# Generate a config for each defined node
for node in inputdata['nodes']:
	render_info = {}
	render_info['id'] = node['id']
	render_info['hostname'] = node['name']
	# Create a unique routerid for the loopback interface, this supports 256*256=65536 nodes, which is more then enough
	render_info['routerid_third_octet'] = floor(node['id']/256)
	render_info['routerid_fourth_octet'] = node['id'] % 256
	render_info['links'] = []
	# Loop through all the links and find the ones for this node, and send those to the template
	for link in links:
		if link['router1'] == node['id'] or link['router2'] == node['id']:
			render_info['links'].append(link)

	# Add empty interfaces to the template, so there will be a base config to disable unused ports
	render_info['emptyinterfaces'] = []
	emptyinterface_counter = len(render_info['links'])
	while emptyinterface_counter < 8:
		render_info['emptyinterfaces'].append(emptyinterface_counter)
		emptyinterface_counter += 1

	# Actually render the template, so we have a config for the current node
	config = template.render(render_info)
	config_element = etree.SubElement(configs_element, 'config',
		id=str(node['id'])
	)
	# Save the base64-encoded config to the Eve-NG Lab XML, so the node in the lab has the correct config to build the entier network
	config_element.text = base64.b64encode(config.encode('ascii'))

# Write the Eve-NG Lab XML to the .unl file, which is the extension Eve-NG uses for it's labfiles
lab = etree.ElementTree(lab_element)
lab.write('lab.unl', pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone=True)
