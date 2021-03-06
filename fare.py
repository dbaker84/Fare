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
import time
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
MSG_X= BAR_WIDTH + 10
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50

TICKCLICK = 50
PERFOOD = 30
PERWATER = 60
STARVERATE = .8
DEHYDRATE = .7

PADJ = [ 1, 1, 1.5,
        2, 3, 2.5,
        2.5, 3, .2]


FOV_ALGO = 0  #default FOV algorithm22
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 7

LIMIT_FPS = 200  #20 frames-per-second maximum

STOCK_NAME = ['Food','Water','Alcohol',
                'Lumber','Iron','Cloth',
                'Tar','Fuel','Javelins']

libtcod.console_set_keyboard_repeat(0,0)

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
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None, person=None, site=None, inventory=None, weapon=None):
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

        self.site = site
        if self.site:  #let the site component know who owns it
            self.site.owner = self

        self.inventory = inventory
        if self.inventory:  #let the inventory component know who owns it
            self.inventory.owner = self

        self.weapon = weapon
        if self.weapon:  #let the inventory component know who owns it
            self.weapon.owner = self

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked

        if not is_blocked((self.x + dx) % MAP_WIDTH, (self.y + dy) % MAP_HEIGHT):
            self.x = (self.x + dx) % MAP_WIDTH
            self.y = (self.y + dy) % MAP_HEIGHT

            self.fighter.wait = self.fighter.speed
        else:
            self.fighter.wait = self.fighter.speed # delay if no move

    def dock(self, target, dx, dy):
        message('You dock into the ' + target.site.stype + ' of ' + target.name + ', population ' + str(target.site.popul))
        # for k in range(0,len(STOCK_NAME)):
        #     message(STOCK_NAME[k] + ' cost ' + str(target.inventory.price[k]) + ' and there are ' + str(target.inventory.stock[k]) + ' for sale.',libtcod.green)

        target.inventory.inv_menu()
        player.x += dx
        player.y += dy

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

    def collect(self):
        if self.site.stype == 'Town':
            cr = 3
        if self.site.stype == 'Port':
            cr = 4

        for k in range(-cr, cr):
            for l in range(-cr, cr):
                if math.sqrt(k**2+l**2) < cr:
                    if map[self.x+k][self.y+l] == -3:
                        self.inventory.stock[0] += 1 # add a food
                    if map[self.x+k][self.y+l] == -2:
                        self.inventory.stock[0] += 1 # add a food
                    # if map[self.x+k][self.y+l] == -1:
                    # if map[self.x+k][self.y+l] == 0:
                    # if map[self.x+k][self.y+l] == 1:
                    if map[self.x+k][self.y+l] == 2:
                        self.inventory.stock[1] += 1 # add a water
                        self.inventory.stock[6] += 1 # add a tar (tarsands)
                    if map[self.x+k][self.y+l] == 3:
                        self.inventory.stock[1] += 1 # add a water
                        self.inventory.stock[6] += 1 # add a tar (evergreens)
                    if map[self.x+k][self.y+l] == 4:
                        self.inventory.stock[0] += 1 # add a food
                        self.inventory.stock[1] += 1 # add a water
                        self.inventory.stock[3] += 1 # add a lumber
                    if map[self.x+k][self.y+l] == 5:
                        self.inventory.stock[0] += 1 # add a food
                        self.inventory.stock[1] += 1 # add a water
                        self.inventory.stock[3] += 1 # add a lumber
                    if map[self.x+k][self.y+l] == 6:
                        self.inventory.stock[0] += 1 # add a food
                        self.inventory.stock[1] += 1 # add a water

    def reprice(self):
        for x in range(0,len(STOCK_NAME)):
            highp = math.log10(100)
            lowp = math.log10(1)
            dif = highp - lowp
            per = (dif / self.site.popul)
            number = self.site.popul - self.inventory.stock[x]
            if number < 0: number = .001
            value = (math.pow(10,number * per)) * PADJ[x]
            if value < 1: value = 1
            self.inventory.price[x] = int(value)


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

        if not libtcod.map_is_in_fov(fov_map, self.x, self.y) and self.site and explored[self.x][self.y] == 1:
            (x, y) = to_camera_coordinates(self.x, self.y)
            libtcod.console_put_char_ex(con, x, y, self.char, self.color * libtcod.dark_grey, get_bcolor(map[self.x][self.y]) * libtcod.dark_grey)

    def clear(self):
        #erase the character that represents this object
        (x, y) = to_camera_coordinates(self.x, self.y)
        if x is not None:
            #libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
            if not libtcod.map_is_in_fov(fov_map, self.x, self.y):
                if explored[x][y] == 1:
                    libtcod.console_put_char_ex(con, x, y, get_char(map[self.x][self.y]), get_fcolor(map[self.x][self.y])*libtcod.dark_grey, get_bcolor(map[self.x][self.y])*libtcod.dark_grey)
            else:
                libtcod.console_put_char_ex(con, x, y, get_char(map[self.x][self.y]), get_fcolor(map[self.x][self.y]), get_bcolor(map[self.x][self.y]))

class Person:
    #c
    def __init__(self, age, origin):
        self.age = age
        self.origin = origin

class Site:
    #a tile of the map and its properties
    def __init__(self,  stype, popul):
        self.stype = stype
        self.popul = popul


class Inventory:
    #a tile of the map and its properties
    def __init__(self, stock, price, items):
        self.stock = stock
        self.price = price
        self.items = items

    def inv_menu(self,header = ''):
        #show a menu with each item of the inventory as an option
        width = INVENTORY_WIDTH

        header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
        if header == '':
            header_height = 0
        height = len(STOCK_NAME) + header_height

        #create an off-screen console that represents the menu's window
        window = libtcod.console_new(width, height)

        #print the header, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

        #print all the options
        y = header_height
        for k in range(0,len(STOCK_NAME)):
            text = STOCK_NAME[k] + ' Quantity ' + str(self.stock[k]) + ' Price ' + str(self.price[k])
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1


        #blit the contents of "window" to the root console
        x = SCREEN_WIDTH/2 - width/2
        y = SCREEN_HEIGHT/2 - height/2
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

        #present the root console to the player and wait for a key-press
        libtcod.console_flush()
        time.sleep(1)
        key2 = libtcod.console_wait_for_keypress(True)

        return None




class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, speed, money, crew, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.speed = speed
        self.money = money

        self.crew = crew
        self.death_function = death_function
        self.wait = 0

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

        #if target.ai.direction:
        #    print 'That ship is moving ' + str(target.ai.direction)

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

class TraderMonster:
    #AI for a basic monster.
    def __init__(self, movin=False, path=None):
        self.movin = movin
        self.path = libtcod.path_new_using_map(fov_map)

    def take_turn(self):
        monster = self.owner
        intel = 50 # intelligence of choice
        distance = 1000


        if not monster.ai.movin: # if no destination set, this will set a target and create a path
            monster.ai.path = libtcod.path_new_using_map(fov_map)
            z = False
            while not z:
                tt = objects[random.randint(0,len(objects)-1)]

                if tt.site:
                    ex = tt.x
                    ey = tt.y
                    z = True



            ox = monster.x
            oy = monster.y

            libtcod.path_compute(monster.ai.path,ox, oy, ex, ey)

            # for i in range (libtcod.path_size(monster.ai.path)) :
            #     x,y=libtcod.path_get(monster.ai.path,i)
            #     print 'Astar coord : '+ monster.name + " " + str(x) + " " + str(y)

            monster.ai.movin = True


        if monster.ai.movin:
            x,y=libtcod.path_walk(monster.ai.path,True)
            if x is None :
                monster.ai.movin = False
            else :
                monster.move(x - monster.x,y - monster.y)



class BasicMonster:
    #AI for a basic monster.



    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y) and monster.fighter.crew:

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

class SailingMonster:
    #AI for a basic monster.
    def __init__(self, direction, randomness):
        self.direction = direction
        self.randomness = randomness

    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        dx = 0
        dy = 0
        if monster.ai.randomness > random.randint(1,100):
            monster.ai.direction = random.randint(1,8)

        if monster.ai.direction == 1:
                dx = -1
                dy = 1
        elif monster.ai.direction == 2:
                dx = 0
                dy = 1
        elif monster.ai.direction == 3:
                dx = 1
                dy = 1
        elif monster.ai.direction == 4:
                dx = -1
                dy = 0
        #5 goes in the direction of 9, to not skip a number
        elif monster.ai.direction == 5:
                dx = 1
                dy = -1
        elif monster.ai.direction == 6:
                dx = 1
                dy = 0
        elif monster.ai.direction == 7:
                dx = -1
                dy = -1
        elif monster.ai.direction == 8:
                dx = -1
                dy = 0

        #print monster.x
        #print dx
        #print monster.y
        #print dy
        if map[monster.x + dx][monster.y + dy] > 0:
            monster.ai.direction = random.randint(1,8)
            #print monster.name + ' change direction to ' + str(monster.ai.direction)

        if map[monster.x + dx][monster.y + dy] < 1:
            monster.move(dx, dy)
            #print monster.name + ' moved toward the ' + str(monster.ai.direction)


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

class Weapon:
    #an item that can be picked up and used.
    def __init__(self, range, damage, accuracy):
        self.range = range
        self.damage = damage
        self.accuracy = accuracy





def is_blocked(x, y):
    #first test the map tile
    if x < 0: x = 0
    if y < 0: y = 0
    if x > MAP_WIDTH-1: x = MAP_WIDTH-1
    if y > MAP_HEIGHT-1: y = MAP_HEIGHT-1

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            if object.site:
                return False
            else:
                return True

    if map[x][y] > 0:
        return True


    return False

def is_explored(x, y):
    if explored[x][y] == 1:
        return True

    return False

def gen_ships(numships):
    global ships, map, objects


    for i in range(0,numships):
        #choose random spot for this monster
        placable = False
        while placable == False:
            x = random.randint(10, MAP_WIDTH-10)
            y = random.randint(10, MAP_HEIGHT-10)
            if map[x][y] < 1:
                placable = True

        # if random.randint(1,100) > 50:
        #     ai_component = BasicMonster()
        # else:
        #     ai_component = SailingMonster(direction=random.randint(1,8),randomness=1)

        ai_component = TraderMonster()
        roster = []
        crewsize = random.randint(1,8)

        if crewsize > 0:
            for i in range(1,crewsize):
                person_component = Person(age = random.randint(16,80), origin = nameLand())
                crewmate = Object(x, y, 'i', nameLand(), libtcod.lighter_red, blocks=False, person=person_component)
                roster.append(crewmate)

        zitems = []
        z = random.randint(0,100)
        if z <= 33:
            weapon_design = Weapon(range=70,damage=3,accuracy=60)
            equipment = Object(x,y,'x',"Rifled Cannon",libtcod.light_grey,weapon=weapon_design)
        if 33 < z <= 66:
            weapon_design = Weapon(range=50,damage=5,accuracy=60)
            equipment = Object(x,y,'x',"Smooth-bore Cannon",libtcod.light_grey,weapon=weapon_design)
        else:
            weapon_design = Weapon(range=30,damage=7,accuracy=60)
            equipment = Object(x,y,'x',"Exploding Javelin",libtcod.light_grey,weapon=weapon_design)

        zitems.append(equipment)

        inventory_component = Inventory(stock=[], price=[], items = zitems)
        fighter_component = Fighter(hp=random.randint(4,10), defense=random.randint(4,10), power=random.randint(4,10), speed = random.randint(4,10),money = 0, crew = roster)

        ship = Object(x, y, 22, nameBoat(), libtcod.red, blocks=False, ai=ai_component, fighter=fighter_component,inventory=inventory_component)


        objects.append(ship)



def make_map():
    global map, objects, ships, player
    global explored
    #the list of objects with just the player
    objects = []

    #fill map with "ocean" tiles
    map = [[ 0
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]


    noise_zoom=20 #lower number = bigger islands
    noise_octaves=20 #lower number = smoother islands

    hm = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    hm1 = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    hm2 = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)

    noise = libtcod.noise_new(2)
    libtcod.heightmap_add_fbm(hm1, noise, noise_zoom, noise_zoom, 0.0, 0.0, noise_octaves, 0.0, 1.0)

    libtcod.heightmap_multiply_hm(hm1, hm1, hm)
    libtcod.heightmap_normalize(hm, mi=0.0, ma=1)

    libtcod.heightmap_delete(hm1)
    libtcod.heightmap_delete(hm2)

    lm = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    hm1 = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)
    hm2 = libtcod.heightmap_new(MAP_WIDTH, MAP_HEIGHT)

    noise2 = libtcod.noise_new(2)
    libtcod.heightmap_add_fbm(hm1, noise2, noise_zoom, noise_zoom, 0.0, 0.0, noise_octaves, 0.0, 1.0)

    libtcod.heightmap_multiply_hm(hm1, hm1, lm)
    libtcod.heightmap_normalize(lm, mi=0.0, ma=1)

    # generate world grid
    for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                hmv = libtcod.heightmap_get_value(hm, x, y)
                if .25 > hmv >= 0: hmv = -1
                elif .50 > hmv >= .25: hmv = 0
                elif .75 > hmv >= .50: hmv = 1
                elif .87 > hmv >= .75: hmv = 2
                elif 1 > hmv >= .87: hmv = 3
                map[x][y] = hmv

    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            hmv = libtcod.heightmap_get_value(lm, x, y)
            if libtcod.random_get_float(0,0,.7) > hmv:
                if map[x][y] == -1: map[x][y] = -3
                elif map[x][y] == 0: map[x][y] = -2
                elif map[x][y] == 1: map[x][y] = 4
                elif map[x][y] == 2: map[x][y] = 5
                elif map[x][y] == 3: map[x][y] = 6


    libtcod.heightmap_delete(hm)
    libtcod.heightmap_delete(lm)
    libtcod.heightmap_delete(hm1)
    libtcod.heightmap_delete(hm2)

    for i in range(MAP_HEIGHT):
        map[0][i] = 8
        map[MAP_WIDTH-1][i] = 8

    for i in range(MAP_WIDTH):
        map[i][0] = 8
        map[i][MAP_HEIGHT-1] = 8

    explored = [[ 1
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]






def place_sites(num_sites):
    global map, objects, ships, player
    global explored
    #the list of objects with just the player


    for i in range(0,num_sites):
        place = False
        while not place:
            x = libtcod.random_get_int(0,10, MAP_WIDTH-10)
            y = libtcod.random_get_int(0,10, MAP_HEIGHT-10)
            if map[x][y] > 0:
                for k in range(-1,2):
                    for l in range(-1,2):
                        if map[x+k][y+l] < 1:
                            place = True
                            for othersites in objects:
                                if othersites.site:
                                    dx = othersites.x - x
                                    dy = othersites.y - y
                                    if math.sqrt(dx ** 2 + dy ** 2) < 10:
                                        place = False


        s_stock = []
        s_price = []

        for k in range(0,len(STOCK_NAME)):
            s_stock.append(0)
            s_price.append(0)


        loc_inv = Inventory(stock = s_stock, price = s_price, items = [])



        if random.randint(0,100) > 50:
            rtype = 'Town'
        else:
            rtype = 'Port'


        people = int(math.pow(10,libtcod.random_get_float(0,math.log10(100),math.log10(5000))))



        loc_info = Site(stype=rtype, popul = people)


        locale = Object(x, y, '#', nameLand(), color=libtcod.dark_blue, blocks=False, site=loc_info, inventory=loc_inv)

        objects.append(locale)
        map[x][y] = -9
        num_sites -= 1




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
    # x = (target_x - CAMERA_WIDTH / 2) % MAP_WIDTH #coordinates so that the target is at the center of the screen
    # y = (target_y - CAMERA_HEIGHT / 2) % MAP_WIDTH
    x = target_x - CAMERA_WIDTH / 2  #coordinates so that the target is at the center of the screen
    y = target_y - CAMERA_HEIGHT / 2

    #make sure the camera doesn't see outside the map
    if x < 0: x = 0
    if y < 0: y = 0
    if x > MAP_WIDTH - CAMERA_WIDTH: x = MAP_WIDTH - CAMERA_WIDTH
    if y > MAP_HEIGHT - CAMERA_HEIGHT: y = MAP_HEIGHT - CAMERA_HEIGHT

    if x != camera_x or y != camera_y: fov_recompute = True

    (camera_x, camera_y) = (x, y)
7
def to_camera_coordinates(x, y):
    #convert coordinates on the map to coordinates on the screen
    (x, y) = ((x - camera_x) % MAP_WIDTH, (y - camera_y) % MAP_HEIGHT)

    if (x < 0 or y < 0 or x >= CAMERA_WIDTH or y >= CAMERA_HEIGHT):
        return (None, None)  #if it's outside the view, return nothing

    return (x, y)

def check_here(x,y):
    global objects_here
    objects_here = []
    for o in objects:
        if o.fighter:
            if o.x == x and o.y == y and o.name != player.name:
                objects_here.append(o.name)

def get_char(x):
    string = 'Z'
    if x < 1:
        z = random.randint(0,100)
        if z <= 95:
            string = ' '
        else:
            string = '~'
    elif x == 1: string = ' '
    elif x == 2: string = '-'
    elif x == 3: string = '^'
    elif x == 4: string = '.'
    elif x == 5: string = '*'
    elif x == 6: string = '^'
    elif x == 8: string = '+'
    return string

def get_fcolor(x):
    color = libtcod.red
    if x == -1 or x == -3: color = libtcod.white
    elif x == 0 or x == -2: color = libtcod.white
    elif x == -9: color = libtcod.gray
    elif x == 1: color = libtcod.sepia
    elif x == 2: color = libtcod.light_gray
    elif x == 3: color = libtcod.gray
    elif x == 4: color = libtcod.light_green
    elif x == 5: color = libtcod.darker_green
    elif x == 6: color = libtcod.green
    elif x == 8: color = libtcod.fuchsia
    return color

def get_bcolor(x):
    color = libtcod.yellow
    if x == -1 or x == -3: color = libtcod.sky
    elif x == 0 or x == -2: color = libtcod.light_sky
    elif x == -9: color = libtcod.gray
    elif x == 1: color = libtcod.light_sepia
    elif x == 2: color = libtcod.sepia
    elif x == 3: color = libtcod.dark_sepia
    elif x == 4: color = libtcod.dark_green
    elif x == 5: color = libtcod.dark_green
    elif x == 6: color = libtcod.dark_sepia
    elif x == 8: color = libtcod.darker_fuchsia
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

                visible = True #see entire map
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
    # dungeon_level = 1
    # render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
    #             libtcod.light_red, libtcod.darker_red)
    # libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

    check_here(player.x,player.y)
    y = 1
    for (name) in objects_here:
        libtcod.console_set_default_foreground(panel, libtcod.red)
        libtcod.console_print_ex(panel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, name)
        y += 1

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

        # #try to find an attackable object there
        # fight_tar = None
        # site_tar = None
        # for object in objects:
        #     if object.fighter and object.x == x and object.y == y:
        #         fight_tar = object
        #         break
        #     if object.site and object.x == x and object.y == y:
        #         site_tar = object
        #         break
        #
        # #attack if target found, move otherwise
        # if fight_tar is not None:
        #     player.fighter.attack(fight_tar)
        # elif site_tar is not None:
        #     player.dock(site_tar,dx,dy)
        # else:
        player.move(dx, dy)
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

    options = [STOCK_NAME[i] for i in range(0,len(STOCK_NAME))]

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

def handle_keys():
    global key

    if key.vk == libtcod.KEY_NONE:
        return 'noturn'

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game






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

        if key_char == 'e':
            engaging = False
            for object in objects:
                if object.x == player.x and object.y == player.y and object.fighter and object.name != player.name:
                    target = object
                    engage_combat(target)
                    engaging = True
            if not engaging:
                print "No one to fight!"
            time.sleep(1)

        if key_char == 'k':
            engaging = False
            for object in objects:
                if object.x == player.x and object.y == player.y and object.fighter and object.name != player.name:
                    target = object
                    engage_combat(target)
                    engaging = True
            if not engaging:
                print "No one to fight!"

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

        # if key_char == 'w':
        #     #show the inventory; if an item is selected, drop it
        #
        #     time.sleep(1)
        #     print "Warp to what X?"
        #     wx = libtcod.console_wait_for_keypress(True)
        #     wx = chr(key.c)
        #     wx = int(wx)
        #     print wx
        #
        #     time.sleep(1)
        #     print "Warp to what Y?"
        #     wy = libtcod.console_wait_for_keypress(True)
        #     wy = chr(key.c)
        #     wy = int(wy)
        #     print wy
        #
        #     if not isinstance( wx, int ) or not isinstance( wy, int ):
        #         message('Wrong coords',libtcod.red)
        #     else:
        #         message('Warping to ' + str(wx) + " " + str(wy), libtcod.light_magenta)
        #         player.x = wx
        #         player.y = wy
    return 'tookturn'



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

def engage_combat(target):

    engaged = True

    distance = random.randint(30,100)

    eweapon = None
    pweapon = None
    if target.inventory.items:
        for eq in target.inventory.items:
            if eq.weapon:
                eweapon=eq
                print "Opponent is using " + eq.name
    if player.inventory.items:
        for eq in player.inventory.items:
            if eq.weapon:
                pweapon=eq
                print "Player is using " + eq.name

    while engaged:

        patt = ''

        if eweapon:
            if distance > eweapon.weapon.range:
                distance -= (10-target.fighter.speed)
                eatt = "attempted to get closer"
            else:
                if random.randint(0,100) < eweapon.weapon.accuracy:
                    eatt  = "attacked with the " + eweapon.name + " and did " + str(eweapon.weapon.damage) + " damage"
                else:
                    eatt = "attacked with the " + eweapon.name + " but missed"


        pressed = libtcod.console_wait_for_keypress(True)

        pchar = chr(pressed.c)


        if pchar == 'a' or pchar == 'A':
            if eweapon:
                if distance > pweapon.weapon.range:
                    patt = "attacked with the " + pweapon.name + " but the shot fell short"
                else:
                    if random.randint(0,100) < pweapon.weapon.accuracy:
                        patt = "attacked with the " + pweapon.name + " and did " + str(pweapon.weapon.damage) + " damage"
                    else:
                        patt = "attacked with the " + pweapon.name + " but missed"

        elif pchar == 'f' or pchar == 'F':
            patt = 'flee'
            engaged = False
        elif pchar == 'c' or pchar == 'C':
            patt = 'attempted to get closer'
            distance -= (10 - player.fighter.speed)
        elif pchar == 'i' or pchar == 'I':
            patt = 'attempted to get move further away'
            distance += (10 - player.fighter.speed)
        elif pchar == 'w' or pchar == 'W':
            patt = 'waited'
        else:
            patt = ''



        libtcod.console_set_default_background(battlepan, libtcod.sky)
        libtcod.console_clear(battlepan)

        libtcod.console_set_default_foreground(battlepan,libtcod.darker_green)
        libtcod.console_print_ex(battlepan, 2, 2, libtcod.BKGND_NONE, libtcod.LEFT, player.name)
        libtcod.console_print_ex(battlepan, 2, 3, libtcod.BKGND_NONE, libtcod.LEFT, "HP: " + str(player.fighter.hp) + " / " + str(player.fighter.max_hp))
        if pweapon:
            libtcod.console_print_ex(battlepan, 2, 4, libtcod.BKGND_NONE, libtcod.LEFT, "Weapon: " + pweapon.name)
        else:
            libtcod.console_print_ex(battlepan, 2, 4, libtcod.BKGND_NONE, libtcod.LEFT, "Weapon: Unarmed")



        libtcod.console_set_default_foreground(battlepan,libtcod.black)
        libtcod.console_print_ex(battlepan, SCREEN_WIDTH/2, 3, libtcod.BKGND_NONE, libtcod.CENTER, 'vs.')

        libtcod.console_print_ex(battlepan, 2, 12, libtcod.BKGND_NONE, libtcod.LEFT, 'Actions last turn: ' + str(distance))
        if len(patt) > 0:
            libtcod.console_print_ex(battlepan, 2, 13, libtcod.BKGND_NONE, libtcod.LEFT, 'You ' + patt + ".")
        if len(eatt) > 0:
            libtcod.console_print_ex(battlepan, 2, 14, libtcod.BKGND_NONE, libtcod.LEFT, 'The ' + target.name + " " + eatt + ".")
        libtcod.console_print_ex(battlepan, 2, 15, libtcod.BKGND_NONE, libtcod.LEFT, 'Range to target: ' + str(distance))
        libtcod.console_print_ex(battlepan, 2, 17, libtcod.BKGND_NONE, libtcod.LEFT, 'What is your command?')
        libtcod.console_print_ex(battlepan, 2, 18, libtcod.BKGND_NONE, libtcod.LEFT, '[A]ttack, [C]lose distance, [I]increase distance, [F]lee engagement, [W]ait')

        libtcod.console_set_default_foreground(battlepan,libtcod.red)
        libtcod.console_print_ex(battlepan, SCREEN_WIDTH-3, 2, libtcod.BKGND_NONE, libtcod.RIGHT, target.name)
        libtcod.console_print_ex(battlepan, SCREEN_WIDTH-3, 3, libtcod.BKGND_NONE, libtcod.RIGHT, "HP: " + str(target.fighter.hp) + " / " + str(target.fighter.max_hp))
        if eweapon:
            libtcod.console_print_ex(battlepan, SCREEN_WIDTH-3, 4, libtcod.BKGND_NONE, libtcod.RIGHT, "Weapon: " + eweapon.name)
        else:
            libtcod.console_print_ex(battlepan, SCREEN_WIDTH-3, 4, libtcod.BKGND_NONE, libtcod.RIGHT, "Weapon: Unarmed")


        libtcod.console_blit(battlepan, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
        libtcod.console_flush()

def target_tile(max_range=None):
    #return the position of a tile left-click3ed in player's FOV (optionally in a range), or (None,None) if right-clicked.
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
    global player, inventory, game_msgs, game_state, tick

    tick = 0

    #create object representing the player
    #generate map (at this point it's not drawn to the screen)


    make_map()
    print 'mapped'

    place_sites(100) # do this before ships - it checks all objects for placement; shorter list
    print 'sites placed'

    initialize_fov()
    print 'fovved'

    gen_ships(100)
    print 'ships genned'


    game_state = 'ready'

    zitems = []
    z = random.randint(0,100)
    if z <= 33:
        weapon_design = Weapon(range=70,damage=3,accuracy=60)
        equipment = Object(0,0,'x',"Rifled Cannon",libtcod.light_grey,weapon=weapon_design)
    if 33 < z <= 66:
        weapon_design = Weapon(range=50,damage=5,accuracy=60)
        equipment = Object(0,0,'x',"Smooth-bore Cannon",libtcod.light_grey,weapon=weapon_design)
    else:
        weapon_design = Weapon(range=30,damage=7,accuracy=60)
        equipment = Object(0,0,'x',"Exploding Javelin",libtcod.light_grey,weapon=weapon_design)

    zitems.append(equipment)

    inventory_component = Inventory(stock=[], price=[], items = zitems)
    fighter_component = Fighter(hp=30, defense=2, power=5, speed=2, money=0, crew=[], death_function=player_death)
    player = Object(random.randint(1,MAP_WIDTH-1), random.randint(1,MAP_HEIGHT-1), 22, 'The Pequod', libtcod.darker_flame, fighter=fighter_component, inventory=inventory_component,blocks=False)
    objects.append(player)
    inventory = []

    #create the list of game messages and their colors, starts empty
    game_msgs = []

    #a warm welcoming message!
    message('Welcome to the world of FARE', libtcod.red)



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
    global camera_x, camera_y, key, mouse, tick, objects, game_state

    player_action = None
    mouse = libtcod.Mouse()
    key = libtcod.Key()

    (camera_x, camera_y) = (0, 0)

    # print game_state
    while not libtcod.console_is_window_closed():
        #render the screen
        # print game_state


        if tick >= TICKCLICK:
            tick = 0
            print 'TICK'
            process_world()


        game_state = 'noturn'
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()

        libtcod.console_flush()



        #handle keys and exit game if needed
        if player.fighter.wait > 0:
            player.fighter.wait -= 1
            tick += 1
            # print 'Waiting for player ' + str(player.fighter.wait)
            for object in objects:
                if object.ai:
                    if object.fighter.wait > 0:  #don't take a turn yet if still waiting
                        object.fighter.wait -= 1
                        #print object.name + ' is now at ' + str(object.fighter.wait)
                    else:
                        object.clear()
                        #print object.name + ' is taking a turn'
                        object.ai.take_turn()
                        object.draw()
        else:
            game_state = handle_keys()
            if game_state == 'tookturn':
                tick += 1
            # print 'Player takes action'
            if game_state == 'exit':
                save_game()
                break



def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'FARE')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Test mode', 'Quit'], 24)
        if choice == 0:  #new game
            new_game()
            play_game()
        elif choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:
            circle_test()
        elif choice == 3:  #quit
            break

def process_world():

    for thing in objects:
        if thing.site:
            thing.collect() # collect resources

            #eat food
            thing.inventory.stock[0] -= thing.site.popul / PERFOOD
            if thing.inventory.stock[0] < 0: #starvation
                thing.site.popul = int(thing.site.popul * STARVERATE)
                thing.inventory.stock[0] = 0
                # print thing.name + ' is starving!'

            #drink water
            thing.inventory.stock[1] -= thing.site.popul / PERWATER
            if thing.inventory.stock[1] < 0: #dehydration
                thing.site.popul = int(thing.site.popul * DEHYDRATE)
                thing.inventory.stock[1] = 0
                # print thing.name + ' is dehydrated!'

            #population growth if food and water
            if thing.inventory.stock[0] > 0 and thing.inventory.stock[1] > 0: #population growth if food and water
                thing.site.popul = int(thing.site.popul + (thing.inventory.stock[0]/(PERFOOD/2)))
                # print thing.name + ' is growing!'

            thing.reprice()







def circle_test():
    cr = 5
    for x in range(-cr, cr):
        for y in range(-cr, cr):
            if math.sqrt(x**2+y**2) < cr:
                print str(x) + 'x and ' + str(y) + 'y is in the circle'
            else:
                print str(x) + 'x and ' + str(y) + 'y is out of the circle'


libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'FARE', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
off2 = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
battlepan = libtcod.console_new(MAP_WIDTH,MAP_HEIGHT)
coordpan = libtcod.console_new(15, 1)

main_menu()
