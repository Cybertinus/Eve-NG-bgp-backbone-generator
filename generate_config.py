#!/usr/bin/env python3

import json
import os
import base64
from math import floor
from lxml import etree
from jinja2 import Environment, FileSystemLoader

jsonfile  = open('test.json', mode='r')
inputdata = json.load(jsonfile)

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

lab_element = etree.Element('lab',
	name='Generated lab',
	id='38d9df61-a249-4988-bd4b-4fe5080b2865',
	version=str('1'),
	scripttimeout= str('300'),
	lock=str('0'),
	author='Cybertinus'
)
topology_element = etree.SubElement(lab_element, 'topology')
nodes_element = etree.SubElement(topology_element, 'nodes')

interfacecounter = {}
for node in inputdata['nodes']:
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
	slot_element = etree.SubElement(node_element, 'slot',
		id=str('1'),
		module='PA-8E'
	)
	for link in links:
		if link['router1'] == node['id'] or link['router2'] == node['id']:
			if node['id'] not in interfacecounter:
				interfacecounter[node['id']] = 16
			interface_name_short = 'e1/'+str(interfacecounter[node['id']] - 16)
			interface_name_long = 'Ethernet1/'+str(interfacecounter[node['id']] - 16)
			interface_element = etree.SubElement(node_element, 'interface',
				id=str(interfacecounter[node['id']]),
				name=interface_name_short,
				type='ethernet',
				network_id=str(link['id'])
			)
			if link['router1'] == node['id']:
				link['router1_interfacename'] = interface_name_long
				interfacecounter[link['router1']] += 1
			elif link['router2'] == node['id']:
				link['router2_interfacename'] = interface_name_long
				interfacecounter[link['router2']] += 1

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

objects_element = etree.SubElement(lab_element, 'objects')
configs_element = etree.SubElement(objects_element, 'configs')

templates = Environment(loader=FileSystemLoader('templates'))
template = templates.get_template('baseconfig.j2')
for node in inputdata['nodes']:
	render_info = {}
	render_info['id'] = node['id']
	render_info['hostname'] = node['name']
	render_info['routerid_third_octet'] = floor(node['id']/256)
	render_info['routerid_fourth_octet'] = node['id'] % 256
	render_info['links'] = []
	for link in links:
		if link['router1'] == node['id'] or link['router2'] == node['id']:
			render_info['links'].append(link)
	render_info['emptyinterfaces'] = []
	emptyinterface_counter = len(render_info['links'])
	while emptyinterface_counter < 8:
		render_info['emptyinterfaces'].append(emptyinterface_counter)
		emptyinterface_counter += 1

	config = template.render(render_info)
	config_element = etree.SubElement(configs_element, 'config',
		id=str(node['id'])
	)
	config_element.text = base64.b64encode(config.encode('ascii'))

lab = etree.ElementTree(lab_element)
lab.write('lab.unl', pretty_print=True, xml_declaration=True, encoding='UTF-8', standalone=True)
