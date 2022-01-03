import os
import random
import math
import shutil
import re

## Constants
MOVE_DISTANCE = 30
MOVE_VARIANCE = 10
MOVE_STEP = 10

OVERWORLD_REGION = "\\region"
POI_REGION = "\\poi"


## I caved and decided to orient some objects
class WorldBoundary:
    def __init__(self, region_list) :
        x_coords = [region[0] for region in region_list]
        z_coords = [region[1] for region in region_list]

        x_coords.sort()
        z_coords.sort()

        self._original_min_x = x_coords[0]
        self._original_max_x = x_coords[-1]
        self._original_min_z = z_coords[0]
        self._original_max_z = z_coords[-1]

        self.min_x = self._original_min_x
        self.max_x = self._original_max_x
        self.min_z = self._original_min_z
        self.max_z = self._original_max_z


    def adjust_boundary(self, new_origin) :
        self.min_x = self._original_min_x + new_origin[0]
        self.max_x = self._original_max_x + new_origin[0]
        self.max_z = self._original_max_z + new_origin[1]
        self.max_z = self._original_max_z + new_origin[1]

class World:
    def __init__(self, path) :
        self.path: str                     = path
        self.region_files                  = self._get_region_files(self.path)
        self.original_region_list          = self._region_files_to_list(self.region_files)
        self.region_list                   = self.original_region_list
        self.region_bounds: WorldBoundary  = WorldBoundary(self.region_list)
        self.new_origin: tuple             = (0, 0)

    def _filename_to_coords(self, filename) : 
        name_parts = filename.split(".")
        return (int(name_parts[1]), int(name_parts[2]))

    def _get_region_files(self, path) :
        region_files_all = os.listdir(path + OVERWORLD_REGION)
        region_files = []
        
        for region in region_files_all :
            if re.match(r"^r\.-?\d+\.-?\d+\.mc[ra]$", region):
                region_files.append(region)

        return region_files

    def _region_files_to_list(self, region_files) :
        region_list = []

        for region in region_files :
            region_list.append(filename_to_coords(region))

        region_list.sort()

        return region_list


    def get_origin_coords(self) :
        blocks_in_region_length = 32 * 16

        return (
            self.new_origin[0] * blocks_in_region_length, 
            self.new_origin[1] * blocks_in_region_length
        )

    def move_origin(self, new_origin) :
        self.new_origin = new_origin
        new_region_list = []

        for region in self.original_region_list:
            new_region_list.append(
                (
                    region[0] + self.new_origin[0],
                    region[1] + self.new_origin[1],
                )
            )

        self.region_bounds.adjust_boundary(new_origin)
        self.region_list = new_region_list


    def print_world(self) : ## TODO
        ## The +1 is because the region bounds are inclusive bounds
        size_x = self.region_bounds.max_x - self.region_bounds.min_x + 1
        size_z = self.region_bounds.max_z - self.region_bounds.min_z + 1

        region_matrix = [
            [
                "." for x in range(size_x)
            ] for z in range(size_z)
        ]

        for region in self.region_list :
            matrix_x = region[0] - self.region_bounds.min_x
            matrix_z = region[1] - self.region_bounds.min_z

            region_matrix[matrix_z][matrix_x] = str(id)

        for line in region_matrix :
            print('|' + ''.join(line) + '|')
    
    

    
## Now back to normal script whatevers
def main() :
    print_intro()

    world_list = []

    world_id = 0
    path = get_world_from_user(world_id)
    dest_path = path

    while path != "":
        
        region_files = get_region_files(path)
        region_list = get_region_coords(region_files)

        region_bounds = find_region_bounds(region_list)
        draw_map_of_regions(region_list, region_bounds, world_id)

        if world_id == 0 :
            new_origin = (0,0) ## No movement for new world
        else :
            new_origin = choose_new_location(region_bounds, world_list)
            new_origin_coords = (new_origin[0]*512, new_origin[1]*512)

            print("The new centre for world {} will be region {}, which is around coords {}".format(world_id, new_origin, new_origin_coords))

            region_bounds = get_new_region_bounds(new_origin, region_bounds)


        world_list.append({
            "path": path,
            "region_files": region_files,
            "region_list": region_list,
            "region_bounds": region_bounds,
            "new_origin": new_origin
        })

        world_id += 1
        path = get_world_from_user(world_id)

    print("""
===============
   Final Map
===============
    """)
    draw_final_map(world_list)

    print()
    confirmation = input("Are you happy with this map? Type 'yes' to apply: ")

    if confirmation.strip().lower() == "yes" :
        ## TODO: Move region files
        pass

    # move_region_files(
    #     new_origin, 
    #     region_files, 
    #     path + OVERWORLD_REGION, 
    #     DEST_SAVE + OVERWORLD_REGION
    # )


def get_world_from_user(world_id) :
    if (world_id == 0) :
        save_path = input("What's the path to your new world? ")
    else: 
        save_path = input("\nWhat's the path to old world {}? (leave blank when done) ".format(world_id))

    return save_path.strip()


def filename_to_coords(filename) : 
    name_parts = filename.split(".")
    return (int(name_parts[1]), int(name_parts[2]))


def get_region_files(path) :
    region_files_all = os.listdir(path + OVERWORLD_REGION)
    region_files = []
    
    for region in region_files_all :
        if re.match(r"^r\.-?\d+\.-?\d+\.mc[ra]$", region):
            region_files.append(region)

    return region_files


def get_region_coords(region_files) :
    region_list = []

    for region in region_files :
        region_list.append(filename_to_coords(region))

    region_list.sort()

    return region_list


def find_region_bounds(region_list) :
    x_coords = [region[0] for region in region_list]
    z_coords = [region[1] for region in region_list]

    z_coords.sort()

    return {
        'min_x': x_coords[0],
        'max_x': x_coords[-1],
        'min_z': z_coords[0],
        'max_z': z_coords[-1],
    }

def get_new_region_bounds(new_origin, region_bounds) :
    return {
        'min_x': region_bounds["min_x"] + new_origin[0],
        'max_x': region_bounds["max_x"] + new_origin[0],
        'min_z': region_bounds["min_z"] + new_origin[1],
        'max_z': region_bounds["max_z"] + new_origin[1],
    }

def draw_map_of_regions(region_list, region_bounds, id) :
    size_x = region_bounds["max_x"] - region_bounds["min_x"] + 1
    size_z = region_bounds["max_z"] - region_bounds["min_z"] + 1

    region_matrix = [
        [
            "." for x in range(size_x)
        ] for z in range(size_z)
    ]

    for region in region_list :
        matrix_x = region[0] - region_bounds["min_x"]
        matrix_z = region[1] - region_bounds["min_z"]

        region_matrix[matrix_z][matrix_x] = str(id)

    for line in region_matrix :
        print('|' + ''.join(line) + '|')
    
    

def choose_new_location(region_bounds, world_list) :
    collision = True ## Just needed to start the loop (why no do-while in python?!)
    while (collision):
        collision = False

        ## Each subsequent world is farther out
        distance = MOVE_DISTANCE + (len(world_list) - 1) * MOVE_STEP

        distance = random.randint(MOVE_DISTANCE - MOVE_VARIANCE, MOVE_DISTANCE + MOVE_VARIANCE)
        direction = random.uniform(0, 2 * math.pi) ## radians

        ## I found a use for trig in the real world! My maths teachers should be proud
        new_origin = (int(distance * math.sin(direction)), int(distance * math.cos(direction)))
        new_region_bounds = get_new_region_bounds(new_origin, region_bounds)

        # new_region_list = [
        #     for z in 
        # ]

        print(new_origin)

        # ## Check wether any of the edges of the new world are within the bounds of an existing world
        # for world in world_list:
        #     ## Check if x direction overlap
        #     if  ( ## It overlaps in the x direction and in the z direction
        #             world["region_bounds"]["min_x"] <= new_region_bounds["min_x"] <= world["region_bounds"]["max_x"] \
        #             or \
        #             world["region_bounds"]["min_x"] <= new_region_bounds["max_x"] <= world["region_bounds"]["max_x"] \
        #         ) \
        #         and \
        #         ( \
        #             world["region_bounds"]["min_z"] <= new_region_bounds["min_z"] <= world["region_bounds"]["max_z"] \
        #             or \
        #             world["region_bounds"]["min_z"] <= new_region_bounds["max_z"] <= world["region_bounds"]["max_z"] \
        #         ) :
        #         collision = True
        #         break
        #     else :
        #         ## Miss in at least one direction so world ok
        #         continue
    
    return new_origin

def draw_final_map(world_list) :
    ## Gather all worlds into one list and make a matrix of that list
    all_regions = []

    for i in range(len(world_list)) :
        for region in world_list[i]["region_list"] :
            ## TODO: Change this
            all_regions.append(
                (
                    region[0] + world_list[i]["new_origin"][0], 
                    region[1] + world_list[i]["new_origin"][1], 
                    i
                )
            )

    all_regions.sort()

    region_bounds = find_region_bounds(all_regions)

    size_x = region_bounds["max_x"] - region_bounds["min_x"] + 1
    size_z = region_bounds["max_z"] - region_bounds["min_z"] + 1

    region_matrix = [
        [
            "." for x in range(size_x)
        ] for z in range(size_z)
    ]

    for region in all_regions :
        matrix_x = region[0] - region_bounds["min_x"]
        matrix_z = region[1] - region_bounds["min_z"]

        region_matrix[matrix_z][matrix_x] = str(region[2])

    for line in region_matrix :
        print('|' + ''.join(line) + '|')




def move_region_files(new_origin, region_files, src_folder, dest_folder):
    tmp_file_list = []

    for filename in region_files:
        old_coords = filename_to_coords(filename)
        new_coords = (old_coords[0] + new_origin[0], old_coords[1] + new_origin[1])
        
        new_filename = 'r.{}.{}.mca'.format(new_coords[0], new_coords[1])

        old_filepath = os.path.join(src_folder, filename)
        new_filepath = os.path.join(dest_folder, new_filename)
        shutil.copyfile(old_filepath, new_filepath)


def print_intro() :
    print('''
=============================
  Minecraft Map-in-Map Tool

     Created by Maddie_J
=============================

Welcome to my little map-in-map tool! This script lets you hide Minecraft 
worlds within other ones, allowing for organic storytelling as the players
stumble across something they've seen before...

You can cancel at any time by hitting `ctrl + c`. Nothing will be changed
until the very end.


How does this work?
-------------------

First, you need to generate your new Minecraft world! Find a seed you like
in version 1.18 or later (to take advantage of the terrain smoothing) and
create an empty world. This will be the world your other maps will be 
hidden within.

Next, find the paths to the locations of the saves of both your new world 
and all the worlds you want to hide within it. I'll be asking for those paths 
in a moment.

On Windows, open file explorer to `%appdata%\\.minecraft\\saves`, find the
world you want, and then copy/paste the _full_ path to that folder.

On Mac, the save files are apparently located at `~/Library/Application Support/minecraft`.

Linux users should know how to figure this out for themselves :P

Once you've input the relevant file paths, I'll output a representation
of your new randomly generated world, numbered in the order input. Each 
subsequent world will have its origin shifted further than the last, but
this is not a guarantee that the first world will have the closest chunks
to origin, given different world sizes and shapes.

If you don't like the sample output, just respond "no" and rerun this tool.
But if you do like it, respond "yes" and the copying will be complete!

You can then open your new world in Minecraft and start your travels to 
the new old worlds!


And with that, let's start!
---------------------------
''')

if __name__ == "__main__": 
    main()