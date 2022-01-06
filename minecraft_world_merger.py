import os
import random
import math
import shutil
import re
from collections.abc import Sequence

## Constants
MOVE_DISTANCE = 30
MOVE_VARIANCE = 5
MOVE_STEP = 5

OVERWORLD_REGION = "region"
POI_REGION = "poi"
ENTITIES_REGION = "entities"

def filename_to_coords(filename) : 
    name_parts = filename.split(".")
    return (int(name_parts[1]), int(name_parts[2]))


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
        self.path: str                     = path.strip()
        self.region_files                  = self._get_region_files(self.path)
        self.original_region_list          = self._region_files_to_list(self.region_files)
        self.region_list                   = self.original_region_list
        self.region_bounds: WorldBoundary  = WorldBoundary(self.region_list)
        self.new_origin: tuple             = (0, 0)



    def _get_region_files(self, path) :
        region_files_all = os.listdir(os.path.join(path, OVERWORLD_REGION))
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

    def choose_new_location(self, world_list) :
        while True:
            ## Each subsequent world is a random spot farther out
            base_distance = MOVE_DISTANCE + (len(world_list) * MOVE_STEP)

            distance = random.randint(base_distance - MOVE_VARIANCE, base_distance + MOVE_VARIANCE)
            direction = random.uniform(0, 2 * math.pi) ## radians

            ## I found a use for trig in the real world! My maths teachers should be proud
            new_origin = (int(distance * math.sin(direction)), int(distance * math.cos(direction)))
            self.move_origin(new_origin)

            print(new_origin)

            ## TODO: Redo collision checking
            region_set = set(self.region_list)
            world_set = world_list.get_region_set()

            if len(world_set.intersection(region_set)) == 0:
                break
        

    def print_world(self, world_id) : ## TODO
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

            region_matrix[matrix_z][matrix_x] = str(world_id)

        for line in region_matrix :
            print('|' + ''.join(line) + '|')
    

class WorldList(Sequence) :
    def __init__(self) :
        self.world_list = []
        self.world_set = set()

    def __getitem__(self, i):
        return self.world_list[i]

    def __len__(self):
        return len(self.world_list)

    def append(self, world: World) :
        self.world_list.append(world)
        self.world_set.update(world.region_list)

    def get_region_set(self) :
        return self.world_set

    def print_final_world(self) :
        world_boundary = WorldBoundary(list(self.world_set))

        size_x = world_boundary.max_x - world_boundary.min_x + 1
        size_z = world_boundary.max_z - world_boundary.min_z + 1

        region_matrix = [
            [
                "." for x in range(size_x)
            ] for z in range(size_z)
        ]

        for i in range(len(self)):
            for region in self[i].region_list :
                matrix_x = region[0] - world_boundary.min_x
                matrix_z = region[1] - world_boundary.min_z

                region_matrix[matrix_z][matrix_x] = str(i)


        for line in region_matrix :
            print('|' + ''.join(line) + '|')

    def move_region_files(self):
        this_is_first_world = True
        for world in self:
            if this_is_first_world:
                this_is_first_world = False
                continue

            move_poi = os.path.exists(os.path.join(world.path, POI_REGION))
            move_entities = os.path.exists(os.path.join(world.path, ENTITIES_REGION))

            for filename in world.region_files:
                old_coords = filename_to_coords(filename)
                new_coords = (old_coords[0] + world.new_origin[0], old_coords[1] + world.new_origin[1])
                
                new_filename = 'r.{}.{}.mca'.format(new_coords[0], new_coords[1])

                old_filepath = os.path.join(world.path, OVERWORLD_REGION, filename)
                new_filepath = os.path.join(self[0].path, OVERWORLD_REGION, new_filename)
                shutil.copyfile(old_filepath, new_filepath)

                if move_poi:
                    try:
                        old_filepath = os.path.join(world.path, POI_REGION, filename)
                        new_filepath = os.path.join(self[0].path, POI_REGION, new_filename)
                        shutil.copyfile(old_filepath, new_filepath)
                    except:
                        pass

                if move_entities:
                    try:
                        old_filepath = os.path.join(world.path, ENTITIES_REGION, filename)
                        new_filepath = os.path.join(self[0].path, ENTITIES_REGION, new_filename)
                        shutil.copyfile(old_filepath, new_filepath)
                    except:
                        pass


    
## Now back to normal script whatevers
def main() :
    print_intro()

    world_list = WorldList()
    world = get_world_from_user(len(world_list))

    while world is not None:
        world.print_world(len(world_list))

        if len(world_list) != 0 : ## First world is destination world and shouldn't be moved
            world.choose_new_location(world_list)
            print(
                "The new centre for world {} will be region {}, which is around coords {}".format(
                    len(world_list), 
                    world.new_origin, 
                    world.get_origin_coords()
                )
            )


        world_list.append(world)
        world = get_world_from_user(len(world_list))

    
    print("""
Final Map
---------
    """)
    world_list.print_final_world()

    print()
    confirmation = input("Are you happy with this map? Type 'yes' to apply: ")

    if confirmation.strip().lower() == "yes" :
        print("Copying files. This may take a few mins...")
        world_list.move_region_files()
        print("""
Done!

Feel free to open your world in Minecraft and start exploring! You
can use the output above to help navigate to your hidden worlds.
Or leave it a surprise! It's all in your hands now.
""")



def get_world_from_user(world_id) -> World :
    if (world_id == 0) :
        path = input("What's the path to your new world? ")
    else: 
        path = input("\nWhat's the path to old world {}? (leave blank when done) ".format(world_id))

    return None if path.strip() == "" else World(path)


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
========================================================================
                       Minecraft Map-in-Map Tool

                          Created by Maddie_J
========================================================================

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