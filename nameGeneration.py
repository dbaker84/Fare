import random

def nameBoat():
    noun = ["Aardvark",  "Albatross",  "Alligator",  "Alpaca",  "Anaconda",
	"Ant",  "Anteater",  "Antelope",  "Armadillo",  "Baboon",  "Badger",
	"Bandicoot",  "Barnacle",  "Barracuda",  "Basilisk",  "Bass",  "Bat",
	"Bear",  "Beaver",  "Bee",  "Beetle",  "Beluga",  "Bird",  "Bison",
	"Blackbird",  "Blowfish",  "Blue Jay",  "Boa",  "Boar",  "Bob-Cat",
	"Bonobo",  "Buck",  "Budgie",  "Buffalo",  "Bull",  "Bullfrog",
	"Butterfly",  "Buzzard",  "Caiman",  "Camel",  "Canary",  "Caribou",
	"Carp",  "Cat",  "Caterpillar",  "Catfish",  "Cattle",  "Centipede",
	"Chameleon",  "Cheetah",  "Chicken",  "Chimpanzee",  "Chinchilla",
	"Chipmunk",  "Clam",  "Cobra",  "Cockatiel",  "Cod",  "Cougar",
	"Cow",  "Coyote",  "Crab",  "Crane",  "Crawfish",  "Cricket",
	"Crocodile",  "Crow",  "Cuckoo",  "Cuttlefish",  "Deer",  "Dingo",
	"Dodo",  "Dog",  "Dolphin",  "Donkey",  "Dove",  "Dragon",
	"Dragonfly",  "Drake",  "Duck",  "Eagle",  "Earthworm",  "Echidna",
	"Eel",  "Egret",  "Elephant",  "Elk",  "Emu",  "Falcon",  "Ferret",
	"Finch",  "Firefly",  "Fish",  "Fly",  "Fox",  "Frog",  "Gazelle",
	"Giraffe",  "Goat",  "Goose",  "Gopher",  "Gorilla",  "Grasshopper",
	"Groundhog",  "Hare",  "Hawk",  "Hedgehog",  "Heron",  "Herring",
	"Hippopotamus",  "Horse",  "Hound",  "Hyena",  "Iguana",  "Jackal",
	"Jackrabbit",  "Jaguar",  "Jellyfish",  "Kangaroo",  "Kingfisher",
	"Kookaburra",  "Lamb",  "Lemur",  "Leopard",  "Lion",  "Lionfish",
	"Llama",  "Lynx",  "Manatee",  "Mantis",  "Marmot",  "Mastiff",
	"Mole",  "Mongoose",  "Monkey",  "Moose",  "Mountain Lion",  "Mule",
	"Muskox",  "Muskrat",  "Narwhal",  "Nautilus",  "Newt",  "Nyala",
	"Ocelot",  "Octopus",  "Opossum",  "Osprey",  "Ostrich",  "Otter",
	"Owl",  "Ox",  "Panda",  "Pangolin",  "Panther",  "Peacock",
	"Pelican",  "Penguin",  "Pig",  "Pigeon",  "Platypus",  "Pony",
	"Porcupine",  "Prawn",  "Puffin",  "Puma",  "Quail",  "Rabbit",
	"Raccoon",  "Ram",  "Rat",  "Rattler",  "Ray",  "Rhino",
	"Rhinoceros",  "Robin",  "Rooster",  "Salmon",  "Sandpiper",
	"Scorpion",  "Sea Lion",  "Sea Turtle",  "Seahorse",  "Seal",
	"Shark",  "Skunk",  "Sloth",  "Slug",  "Snail",  "Snake",  "Spider",
	"Squid",  "Squirrel",  "Starfish",  "Stingray",  "Stork",  "Swan",
	"Swordfish",  "Tadpole",  "Tamarin",  "Tapir",  "Tarantula",
	"Terrapin",  "Tiger",  "Tortoise",  "Trout",  "Tuna",  "Turkey",
	"Turtle",  "Urchin",  "Viper",  "Vole",  "Vulture",  "Wallaby",
	"Walrus",  "Warbler",  "Warthog",  "Wasp",  "Weasel",  "Whale",
	"Wildcat",  "Wolf",  "Wolverine",  "Wombat",  "Woodchuck",
	"Woodpecker",  "Wren",  "Yak",  "Zebra"]
 
	    
    cora = random.randint(0, 100)
    if cora < 60:
        fileName=open("prenoun.txt")
    else:
        fileName=open("colors.txt")
    prenoun = [i for i in fileName.readlines()]
    x = random.randint(0,len(noun)-1)
    y = random.randint(0,len(prenoun)-1)
    pre = str(prenoun[y])
    pre = pre.strip()
    pre = pre.capitalize()
    name = "The " + pre + " " + noun[x]
    return(name)




def nameLand():
    namer = ''
    str(namer)
    letter = 0

    sylb = [["EIN","DER","SCH","DIE","UND","CHE","CHT","DEN","GEN","INE",
            "TEN","UNG","HEN","NDE","LIC","VER","SIE","STE","NEN","EIT",
            "BER","TER","NGE","DAS","ACH","ERS","AND","REN","NIC","ERE",
            "SIC","IST","LLE","BEN","AUF","ABE","END","SEN","SEI","MIT",
            "MEN","IGE","AUS","NTE","ESE","EN","ER","CH","DE","EI","IE",
            "IN","TE","GE","UN","ND","IC","ES","BE","HE","ST","NE","AN",
            "RE","SE","DI","SC","AU","NG","SI","LE","DA","IT","HT","EL",
             "LI","ICH"],
            ["NA","NY","RA","IN","AM","AR","TA","IA","KA","HA","AT","MI",
             "MA","ON","FA","LA","TR","EN","IT","DI","AH","IK","SA","NO",
             "AL","SY","TE","RI","ND","TS","TO","NI","RE","ZA","VA","AO",
             "OA","IS","ANA","TRA","AMI","MIN","ARA","ANY","INA","AHA",
             "DIA","RAN","NAN","IKA","NDR","ATR","MAN","AKA","TAN","HAN",
             "AND","IZA","TEN","ONA","IAN","ANT","ARY","OVA","FAN","ALA",
             "IRE","ANO","ITR","ENY","MPI","TAO","IKI","TAM","WIK","HAT",
             "ZAN","TSY","DRA","AIN","MBA","AMP","ENA","ATI","ASA","OLO",
             "FAH","LAN","AMB","ANI","ITA","IND","ARI","AN"],
            ["TH","HE","AN","ER","IN","RE","ND","OU","EN","ON","ED","TO",
             "IT","HA","AT","VE","OR","AS","HI","AR","TE","ES","NG","IS",
             "ST","LE","AL","TI","SE","WA","EA","ME","NT","NE","THE","AND",
             "ING","HER","YOU","VER","WAS","HAT","NOT","FOR","THI","THA",
             "HIS","ENT","ITH","ION","ERE","WIT","ALL","EVE","OUL","ULD",
             "TIO","TER","HEN","HAD","SHO","OUR","HIN","ERA","ARE","TED",
             "OME","BUT"],
            ["DERP","STEIN","HEIM","A"]
            ]
        
    
    attempt = 0
    validstr = 0
    sSet = random.randint(0,len(sylb)-1)
    howLong = random.randint(5,10)
    
    while validstr == 0:
        namer = ''
        validstr = 1
        attempt += 1

        while len(namer) < howLong:
                letter = random.randint(0,len(sylb[sSet])-1)
                namer = namer + sylb[sSet][letter]

        conscount = 0
        vowcount = 0
        prevletter = ''

        for letter in namer:
            if letter == "A" or letter == "E" or letter == "I" or letter == "O" or letter == "U":
                if letter == prevletter:
                    validstr = 0
                prevletter = letter
                vowcount += 1
                conscount = 0
                if vowcount >= 2:
                    validstr = 0
            else:
                conscount += 1
                vowcount = 0
                if conscount >= 3:
                    validstr = 0
                    
        if validstr == 0:
            chance = random.randint(1,100)
            if chance == 1:
                validstr = 1
                #print("exception!")

    nRatio = .0001+namer.count("A")+namer.count("E")+namer.count("I")+namer.count("O")+namer.count("U")
    vRatio = round( (len(namer)-nRatio)/nRatio,2)
    
    #print(str(vRatio) + ' ' + str(namer) + str(attempt))

    return str.capitalize(namer)
    
