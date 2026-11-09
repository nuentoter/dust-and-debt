"""Two handcrafted multi-stage New Austellia regional stories.

Each route visits three existing settlements, then returns to its origin.
Towns use the authoritative illustrated atlas coordinates, so no procedural
randomness or inaccessible mission-specific combat targets are introduced.
"""
from frontier_expansion import SETTLEMENTS

_TOWNS={key:(name,x,y) for key,name,x,y,*_ in SETTLEMENTS}

CHAPTERS=(
    {
      "id":"iron_rail",
      "title":"The Iron Rail Covenant",
      "origin":"drybone",
      "steps":(
        ("drybone","Meet Ada Pike in Galloway and investigate the missing rail dispatch."),
        ("ember","Trace the forged shipping stamps to Larkfield."),
        ("sundown","Recover the signal register from Riversend."),
        ("drybone","Return the evidence to Galloway for the railway hearing."),
      ),
      "reward":165,
      "honor":4,
      "dialogue":(
        "Someone is replacing the railroad bills. The conductor fears an inside hand.",
        "Larkfield confirms an entire wagon was diverted.",
        "The signal register names the last honest train crew.",
        "The railway hearing can finally proceed. You have earned this.",
      ),
    },
    {
      "id":"river_oath",
      "title":"Oath of the Blackwater",
      "origin":"saltwater",
      "steps":(
        ("saltwater","Hear Jonah Reed's story at Roan Creek."),
        ("painted","Follow the missing water permits to Dustwell."),
        ("ironwell","Find the old mine-water records at Iron Mesa."),
        ("saltwater","Return with proof to Roan Creek's river council."),
      ),
      "reward":180,
      "honor":5,
      "dialogue":(
        "The water permits were sold twice. Folks downstream are paying for it.",
        "Dustwell's copies reveal the forged river rights.",
        "The mine ledgers prove who closed the headwaters.",
        "We can protect the water now. The river has not forgotten your help.",
      ),
    },
)

CHAPTER_BY_ID={chapter["id"]:chapter for chapter in CHAPTERS}

def node_for(chapter,step):
    if isinstance(chapter,str):chapter=CHAPTER_BY_ID[chapter]
    index=max(0,min(int(step),len(chapter["steps"])-1))
    key,description=chapter["steps"][index]
    name,x,y=_TOWNS[key]
    return {"town":key,"town_name":name,"x":x,"y":y,
            "description":description,"index":index}

def available_chapter(x,y,completed):
    for chapter in CHAPTERS:
        if chapter["id"] in completed:continue
        node=node_for(chapter,0)
        if (node["x"]-x)**2+(node["y"]-y)**2<330**2:
            return chapter
    return None

def all_chapter_nodes_walkable(can_move,search):
    """Useful for testing a production atlas without requiring exact town-center clearance."""
    result={}
    for chapter in CHAPTERS:
        for index in range(len(chapter["steps"])):
            node=node_for(chapter,index)
            result[(chapter["id"],index)]=search(node["x"],node["y"],can_move)
    return result
