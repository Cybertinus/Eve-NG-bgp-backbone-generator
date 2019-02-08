# Eve-NG-bgp-backbone-generator
A Python script to generate an Eve-NG Lab file with a BGP backbone already integrated in it.

## Description ##
This script has been based on [a blog posted written by Ben Jojo](https://blog.benjojo.co.uk/post/eve-online-bgp-internet), in which he builds a virtual BGP network which emulates the world created in the [MMO](https://en.wikipedia.org/wiki/Massively_multiplayer_online_game) [Eve Online](https://www.eveonline.com/). Later on in his post he does the same thing for the London underground, in which every station is a BGP router.

He created a very small Linux image in which he runs Bird 2, to build his routers. My idea is to do the same thing as he did, but I will do this with virtual Cisco routers in an [Eve-NG](https://www.eve-ng.net/) lab. This script generates a complete lab for Eve-NG, including a configuration on all the routers to get the network up-and-running when you start the nodes.
The script uses a JSON file as input. In this JSON file is described which nodes/stations/planets there are in your world and how they are connected. The format of this JSON file is what Ben has created for his project, so my code should be compatible with whatever input files he has.

## How to use the program ##
At the moment you just have to create a JSON file with the correct syntax and run the script. At the moment there aren't any commandline options to tweak things. This is on the ToDo list to fix, because it makes no sense that my nickname is hardcoded in the script, to be placed as Author in the Eve-NG Lab file. This will be fixed.
