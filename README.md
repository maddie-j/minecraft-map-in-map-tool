# Minecraft Map-in-Map tool

This handy-dandy little script is designed to hide existing Minecraft maps
within a newly created Minecraft map. This can create some organic story-telling
moments as players stumble upon familiar worlds from years gone by.

Note that this script just hides the worlds (for the time being). Any hints to
get the player _to_ those worlds are left as an excercise for the admin.

## What you'll need

- python3
- Minecraft Java Edition
- At least one save file from an old Minecraft world

This script has been developed against Windows CMD, under the assumption most of the 
people running it will be using Windows machines. However, it should theoretically be
usable on both Linux and Mac too. 

Instructions on how the script works are printed out when you run the script, so I won't
repeat them here. But the TL;DR is that it will as for the input paths of the save files
of the relevant Minecraft worlds, first the world that will house the other worlds
followed by the other worlds that are to be hidden within the first. The script will
then randomly fit the worlds together, giving you a visualisation of what it's found
to fit, and if you like it, it will copy the files from the old worlds into the new
with the relevant offsets.

If you're moving pre-1.18 worlds into a post 1.18 world, Minecraft should do some
automatic terrain smoothing to make sure the edges between the old and new terrain
is ok. In my own testing, trees and ice may be left oddly cut off, but the terrain 
itself was mostly seemless.

Note that the script should always leave a large, clear radius around spawn so you
have plenty of space to play on your actual world seed. This is of course unless
one of your merged in worlds is _super_ weirdly shaped. If not enough space is left
in the preview the first time you run the script, just exit out and run it again 
for a new random configuration.

## Making it work for you

My own testing of this script has been against the Hermitcraft world downloads found
on hermitcraft.com. I recommend tweaking the constants at the top of the script to fit
if your worlds are of a different size. You'll most likely want a much shorter 
`MOVE_DISTANCE` for your friends' more casual world!

Also, can 10/10 recommend pruning your world saves before merging, both to save on the 
overall save size but also so there are fewer regions that could get in the way of other 
regions that we're trying to merge together.
