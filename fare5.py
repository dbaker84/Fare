#!/usr/bin/python
#!/usr/bin/python
#
# libtcod python tutorial
#

import libtcodpy as libtcod
import math
import textwrap
import shelve
import random
import nameGeneration

nameBoat = nameGeneration.nameBoat
nameLand = nameGeneration.nameLand

#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of the map portion shown on-screen
CAMERA_WIDTH = 80
CAMERA_HEIGHT = 43

#size of the map
MAP_WIDTH = 200
MAP_HEIGHT = 200

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50




FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 4

LIMIT_FPS = 20  #20 frames-per-second maximum




class Tile:
    #a tile of the map and its properties
    def __init__(self, char, color, bg, blocked, block_sight = None):
        self.char = char
        self.color = color
        self.bg = bg
        self.blocked = blocked

        #all tiles start unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None, person=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks

        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self

        self.person = person
        if self.person:  #let the craft component know who owns it
            self.person.owner = self

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            if self.x + dx > MAP_WIDTH:
                self.x = 0
            elif self.x + dx < 0:
                self.x = MAP_WIDTH - 1
            else:
                self.x += dx

            if self.y + dy > MAP_HEIGHT:
                self.y = 0
            elif self.y + dy < 0:
                self.y = MAP_HEIGHT - 1
            else:
                self.y += dy


    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        #only show if it's visible to the player
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            (x, y) = to_camera_coordinates(self.x, self.y)

            if x is not None:
                #set the color and then draw the character that represents this object at its position
                #libtcod.console_set_default_foreground(con, self.color)
                #libtcod.console_put_char(con, x, y, self.char, libtcod.BKGND_NONE)
                libtcod.console_put_char_ex(con, x, y, self.char, self.color, get_bcolor(map[self.x][self.y]))

    def clear(self):
        #erase the character that represents this object
        (x, y) = to_camera_coordinates(self.x, self.y)
        if x is not None:
            #libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
            libtcod.console_put_char_ex(con, x, y, get_char(map[self.x][self.y]), get_fcolor(map[self.x][self.y])*libtcod.dark_grey, get_bcolor(map[self.x][self.y])*libtcod.dark_grey)

class Person:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, age, origin):
        self.age = age
        self.origin = origin


class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, speed, inv, crew, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.speed = speed
        self.inv = inv
        self.crew = crew
        self.death_function = death_function

    def attack(self, target):
        #a simple formula for attack damage
        #damage = self.power - target.fighter.defense
        message(self.owner.name.capitalize() + ' bumps into ' + target.name)
        if target.fighter.crew:
            z = random.randint(0,len(target.fighter.crew)-1)
            message('You ram into the ' + target.name + ' and launch ' + target.fighter.crew[z].name + ' into the ocean.')
            target.fighter.crew.pop(z)
        else:
            message('You ram into the ' + target.name + ' but see no one on deck.')

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

            #check for death. if there's a death function, call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class BasicMonster:
    #AI for a basic monster.
    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                message(monster.name + ' bounces off your hull!')
                if monster.fighter.crew:
                    z = random.randint(0,len(monster.fighter.crew)-1)
                    message('You see ' + str(monster.fighter.crew[z].person.age) + ' year old ' + monster.fighter.crew[z].name + ' laughing at you.')
                else:
                    message('You see no one on the ship... spooky...')

class Item:
    #an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function = use_function

    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

    def use(self):
        #just call the "use_function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason



def is_blocked(x, y):
    #first test the map tile
    if map[x][y] > 0:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def is_explored(x, y):
    if explored[x][y] == 1:
        return True

    return False

def gen_ships():
    global ships, map, objects
    numships = 300

    ai_component = BasicMonster()


    for i in range(0,numships):
        #choose random spot for this monster
        placable = False
        while placable == False:
            x = random.randint(0, MAP_WIDTH-1)
            y = random.randint(0, MAP_HEIGHT-1)
            if map[x][y] == 0: placable = True
        #x = 40
        #y = 49

        roster = []
        crewsize = random.randint(0,8)

        if crewsize > 0:
            for i in range(1,crewsize):
                person_component = Person(age = random.randint(16,80), origin = nameLand())
                crewmate = Object(x, y, 'i', nameLand(), libtcod.darker_magenta, blocks=True, person=person_component)
                roster.append(crewmate)


        fighter_component = Fighter(hp=random.randint(4,10), defense=random.randint(4,10), power=random.randint(4,10), speed = random.randint(4,10), inv = [], crew = roster)
        ai_component = BasicMonster()

        ship = Object(x, y, '&', nameBoat(), libtcod.darker_magenta, blocks=True, ai=ai_component, fighter=fighter_component)
        print ship.name + ' ' + str(ship.x) + 'x ' + str(ship.y) + 'y'
        print str(ship.fighter.hp) + 'hp ' + str(ship.fighter.defense) + 'def ' + str(ship.fighter.power) + 'power ' + str(ship.fighter.hp) + 'speed'


        #if ship.fighter.crew:
        #    for j in range(0,len(ship.fighter.crew)-1):
        #        print ship.fighter.crew[0].name + ' from ' + ship.fighter.crew[0].person.origin + ', age ' + str(ship.fighter.crew[0].person.age)




        objects.append(ship)


def place_monsters():
    #choose random number of monsters
    #num_monsters = random.randint(199, 200)
    num_monsters = 300

    for i in range(num_monsters):
        #choose random spot for this monster
        placable = False
        while placable == False:
            x = random.randint(0, MAP_WIDTH-1)
            y = random.randint(0, MAP_HEIGHT-1)
            if map[x][y] == 0: placable = True


        fighter_component = Fighter(hp=16, defense=1, power=4, speed=4, inv = [])
        ai_component = BasicMonster()


        monster = Object(x, y, '&', 'Tentacle', libtcod.darker_magenta, blocks=True, fighter=fighter_component, ai=ai_component)
        objects.append(monster)

def make_map():
    global map, objects, ships
    global explored
    #the list of objects with just the player
    objects = [player]

    #fill map with "ocean" tiles
    map = [[ 0
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    for r in range(0,4500):
        x = libtcod.random_get_int(0, 1, MAP_WIDTH-1)
        y = libtcod.random_get_int(0, 1, MAP_HEIGHT-1)
        map[x][y] = 1

    #fill in "holes"
    for k in range (0,3):
        for x in range(0,MAP_WIDTH-1):
            for y in range(0,MAP_HEIGHT-1):
                if map[x][y] == 0:
                    neighbors = 0
                    for r in range(-1,1):
                        for s in range(-1,1):
                            if map[x+r][y+s] == 1:
                                #if r == -1 and s == -1:
                                #    neighbors += 0
                                if r or s == 0:
                                    neighbors += 3
                                else:
                                    neighbors += 1

                    chance = random.randint(0,6)
                    if chance < neighbors: map[x][y] = 3
    #
    # #sink lonely islands
    # for x in range(0,MAP_WIDTH-1):
    #     for y in range(0,MAP_HEIGHT-1):
    #         if map[x][y] > 0:
    #             neighbors = 0
    #             for r in range(-1,1):
    #                 for s in range(-1,1):
    #                     if map[x+r][y+s] == 1: neighbors += 1
    #             chance = random.randint(1,4)
    #             if chance > neighbors: map[x][y] = 0

    #change to zero for fog
    explored = [[ 1
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]


def place_objects(room):
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)

        if libtcod.random_get_int(0, 0, 100) < 80:  #80% chance of getting an orc
            #create an orc
            monster = Object(x, y, 'o', libtcod.desaturated_green)
        else:
            #create a troll
            monster = Object(x, y, 'T', libtcod.darker_green)

        objects.append(monster)

##	rooms = []
##	num_rooms = 0
##
##	for r in range(MAX_ROOMS):
##		#random width and height
##		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
##		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
##		#random position without going out of the boundaries of the map
##		x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
##		y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
##
##		#"Rect" class makes rectangles easier to work with
##		new_room = Rect(x, y, w, h)
##
##		#run through the other rooms and see if they intersect with this one
##		failed = False
##		for other_room in rooms:
##			if new_room.intersect(other_room):
##				failed = True
##				break
##
##		if not failed:
##			#this means there are no intersections, so this room is valid
##
##			#"paint" it to the map's tiles
##			create_room(new_room)
##
##			#add some contents to this room, such as monsters
##			place_objects(new_room)
##
##			#center coordinates of new room, will be useful later
##			(new_x, new_y) = new_room.center()
##
##			if num_rooms == 0:
##				#this is the first room, where the player starts at
##				player.x = new_x
##				player.y = new_y
##			else:
##				#all rooms after the first:
##				#connect it to the previous room with a tunnel
##
##				#center coordinates of previous room
##				(prev_x, prev_y) = rooms[num_rooms-1].center()
##
##				#draw a coin (random number that is either 0 or 1)
##				if libtcod.random_get_int(0, 0, 1) == 1:
##					#first move horizontally, then vertically
##					create_h_tunnel(prev_x, new_x, prev_y)
##					create_v_tunnel(prev_y, new_y, new_x)
##				else:
##					#first move vertically, then horizontally
##					create_v_tunnel(prev_y, new_y, prev_x)
##					create_h_tunnel(prev_x, new_x, new_y)
##
##			#finally, append the new room to the list
##			rooms.append(new_room)
##			num_rooms += 1




def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)
    (x, y) = (camera_x + x, camera_y + y)  #from screen to map coordinates

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def move_camera(target_x, target_y):
    global camera_x, camera_y, fov_recompute

    #new camera coordinates (top-left corner of the screen relative to the map)
    x = target_x - CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
    y = target_y - CAMERA_HEIGHT / 2

    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > MAP_WIDTH - CAMERA_WIDTH - 1: x = MAP_WIDTH - CAMERA_WIDTH - 1
    if y > MAP_HEIGHT - CAMERA_HEIGHT - 1: y = MAP_HEIGHT - CAMERA_HEIGHT - 1

    if x != camera_x or y != camera_y: fov_recompute = True

    (camera_x, camera_y) = (x, y)

def to_camera_coordinates(x, y):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = (x - camera_x, y - camera_y)

    if (x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT):
        return (None, None)  #if it's outside the view, return nothing

    return (x, y)

def get_char(x):
    string = 'Z'
    if x == 0:
        z = random.randint(0,100)
        if z <= 90:
            string = ' '
        else:
            string = '~'
    elif x == 1: string = '^'
    elif x == 2: string = 'X'
    elif x == 3: string = '.'
    return string

def get_fcolor(x):
    color = libtcod.red
    if x == 0: color = libtcod.white
    elif x == 1: color = libtcod.green
    elif x == 3: color = libtcod.dark_green
    return color

def get_bcolor(x):
    color = libtcod.yellow
    if x == 0: color = libtcod.sky
    elif x == 1: color = libtcod.sepia
    elif x == 3: color = libtcod.sepia
    return color

def render_all():
    global fov_map, color_obscure_barrier, color_light_wall
    global color_obscure_open, color_light_ground
    global fov_recompute

    move_camera(player.x, player.y)

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        libtcod.console_clear(con)

        #go through all tiles, and set their background color according to the FOV
        for y in range(CAMERA_HEIGHT):
            for x in range(CAMERA_WIDTH):
                (map_x, map_y) = (camera_x + x, camera_y + y)
                visible = libtcod.map_is_in_fov(fov_map, map_x, map_y)

                wall = is_blocked(map_x,map_y)

                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if explored[map_x][map_y] == 1:
                        libtcod.console_put_char_ex(con, x, y, get_char(map[map_x][map_y]), get_fcolor(map[map_x][map_y])*libtcod.dark_grey, get_bcolor(map[map_x][map_y])*libtcod.dark_grey)
                else:
                    #it's visible
                    libtcod.console_put_char_ex(con, x, y, get_char(map[map_x][map_y]), get_fcolor(map[map_x][map_y]), get_bcolor(map[map_x][map_y]))
                    #since it's visible, explore it
                    #mapping = 20
                    #z = random.randint(1, 100)
                    #if z < mapping:
                    explored[map_x][map_y] = 1

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    xcoord = str(player.x)
    ycoord = str(player.y)
    coords = xcoord + "X " + ycoord + "Y"
    libtcod.console_print_ex(coordpan, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, coords)
    libtcod.console_blit(coordpan, 0, 0, 0, 0, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)


    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red)

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )


def player_move_or_attack(dx, dy):
    global fov_recompute


    if not (dx == 0 and dy == 0):
        #the coordinates the player is moving to/attacking
        x = player.x + dx
        y = player.y + dy

        #try to find an attackable object there
        target = None
        for object in objects:
            if object.fighter and object.x == x and object.y == y:
                target = object
                break

        #attack if target found, move otherwise
        if target is not None:
            player.fighter.attack(target)
        else:
            player.move(dx, dy)

    fov_recompute = True


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

def handle_keys():
    global key

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if game_state == 'playing':
        #movement keys
        if key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)

        elif key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)

        elif key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)

        elif key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)

        elif key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)

        elif key.vk == libtcod.KEY_KP5:
            player_move_or_attack(0, 0)

        else:
            #test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick up an item
                for object in objects:  #look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if key_char == 'd':
                #show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            return 'didnt-take-turn'

def player_death(player):
    #the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'

    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red

def monster_death(monster):
    #transform it into a nasty corpse! it doesn't block, can't be
    #attacked and doesn't move
    message(monster.name.capitalize() + ' is dead!', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    global key, mouse
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
        (x, y) = (mouse.cx, mouse.cy)
        (x, y) = (camera_x + x, camera_y + y)  #from screen to map coordinates

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy





def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['explored'] = explored
    file['objects'] = objects
    #file['ships'] = ships
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file.close()

def load_game():
    #open the previously saved shelve and load the game data
    global map, explored, objects, ships, player, stairs, inventory, game_msgs, game_state

    file = shelve.open('savegame', 'r')
    map = file['map']
    explored = file['explored']
    objects = file['objects']
    #ships = file['ships']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    file.close()

    initialize_fov()

def new_game():
    global player, inventory, game_msgs, game_state

    #create object representing the player
    fighter_component = Fighter(hp=30, defense=2, power=5, speed = 10, inv=[1,2,3,4], crew=[], death_function=player_death)

    player = Object(random.randint(1,MAP_WIDTH-1), random.randint(1,MAP_HEIGHT-1), 22, 'player', libtcod.darker_flame, fighter=fighter_component)


    #generate map (at this point it's not drawn to the screen)
    make_map()
    gen_ships()
    initialize_fov()

    game_state = 'playing'
    inventory = []

    #create the list of game messages and their colors, starts empty
    game_msgs = []

    #a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not is_blocked(x,y), not is_blocked(x,y))

    libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)

def play_game():
    global camera_x, camera_y, key, mouse

    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    (camera_x, camera_y) = (0, 0)

    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()

        libtcod.console_flush()

        #erase all objects at their old locations, before they move
        #for object in objects:
        #    object.clear()

        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break


        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'FARE66')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Ship Gen Test', 'Quit'], 24)
        if choice == 0:  #new game
            new_game()
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        if choice == 2:  #make ship test mode
            gen_ships()
        elif choice == 3:  #quit
            break

libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
coordpan = libtcod.console_new(15, 1)

main_menu()
