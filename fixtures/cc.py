from general.models import *

CC = [
    ["TECH & INNOVATION",
    "Audio",
    "Camera Gear",
    "Energy & Green Tech",
    "Fashion & Wearables",
    "Food & Beverages",
    "Health & Fitness",
    "Home",
    "Phones & Accessories",
    "Productivity",
    "Transportation",
    "Travel & Outdoors",
    "Other Innovative Products"],

    ["CREATIVE WORKS",
    "Art",
    "Comics",
    "Dance & Theater",
    "Film",
    "Music",
    "Photography",
    "Podcasts, Blogs & Vlogs",
    "Tabletop Games",
    "Video Games",
    "Web Series & TV Shows",
    "Writing & Publishing",
    "Other Creations"],

    ["COMMUNITY PROJECTS",
    "Animal Rights",
    "Culture",
    "Education",
    "Environment",
    "Human Rights",
    "Local Businesses",
    "Spirituality",
    "Wellness",
    "Other Community Projects"]
]

column = 1
for cc in CC:    
    parent = CampCategory.objects.create(name=cc[0], parent=None, column=column)
    for scc in cc[1:]:
        CampCategory.objects.create(name=scc, parent=parent, column=column)
    column = column + 1
