"""Persistent menu preferences and keyboard binding rules.

All gameplay key events are translated to existing game action keys, keeping
the old mission/interior/combat logic working without duplicate handlers.
Arrow keys remain an alternate movement option and menu navigation keys are
reserved. The file lives alongside the save but is never part of a new game.
"""
import json
import os

DEFAULT_KEYS={
 "move_up":"w", "move_down":"s", "move_left":"a", "move_right":"d",
 "sprint":"shift_l", "shoot":"space", "reload":"r",
 "interact":"e", "horse":"h", "lasso":"l", "hogtie":"g",
 "dead_eye":"q", "map":"m", "journal":"j",
 "tonic":"1", "weapon":"2", "gather":"f", "camp":"t",
 "bounty":"b", "work":"p", "road_job":"n", "rumor":"u",
 "story":"y", "ledger":"i", "waypoint_clear":"c",
 "sound_toggle":"v", "music_toggle":"o"
}
CONTROL_LABELS={
 "move_up":"Move north", "move_down":"Move south",
 "move_left":"Move west", "move_right":"Move east",
 "sprint":"Sprint / gallop", "shoot":"Fire revolver",
 "reload":"Reload", "interact":"Interact / enter (Shift+key)",
 "horse":"Mount / dismount", "lasso":"Throw lasso",
 "hogtie":"Hogtie", "dead_eye":"Dead Eye", "map":"Territory map",
 "journal":"Journal", "tonic":"Health tonic", "weapon":"Switch weapon",
 "gather":"Gather", "camp":"Rest at camp", "bounty":"Take bounty",
 "work":"Paid work", "road_job":"Road contract", "rumor":"Rumors",
 "story":"Regional story", "ledger":"Work ledger", "waypoint_clear":"Clear waypoint",
 "sound_toggle":"Toggle effects", "music_toggle":"Toggle music"
}
# Always keep these globally accessible for user safety and existing UI.
RESERVED=frozenset(("escape","return","kp_enter","tab","up","down","left","right",
                     "f1","f5","f6","f7","f8","f11","shift_r",
                     "control_l","control_r","alt_l","alt_r","super_l","super_r"))

DEFAULT_AUDIO={"master_volume":.7,"music_volume":.55,"effects_volume":.8}
DEFAULT_FLAGS={"music_enabled":True,"sound_on":False}

def normalized_key(key):
    key=str(key).strip().lower()
    aliases={"shift":"shift_l","spacebar":"space","enter":"return",
             "control":"control_l","plus":"equal","minus":"minus"}
    return aliases.get(key,key)

def normalize_bindings(raw):
    if not isinstance(raw,dict):return dict(DEFAULT_KEYS)
    values=dict(DEFAULT_KEYS)
    used=set()
    for action in DEFAULT_KEYS:
        key=normalized_key(raw.get(action,values[action]))
        if not key or key in RESERVED or (key=="shift_l" and action!="sprint") or key in used:
            key=DEFAULT_KEYS[action]
        values[action]=key
        used.add(key)
    # Repair malformed duplicate custom settings deterministically.
    for action,key in list(values.items()):
        if sum(1 for v in values.values() if v==key)>1:
            return dict(DEFAULT_KEYS)
    return values

def rebind(bindings,action,key):
    """Replace one binding or report why it cannot be assigned."""
    if action not in DEFAULT_KEYS:return None,"Unknown action"
    key=normalized_key(key)
    if key in RESERVED or not key or (key=="shift_l" and action!="sprint"):
        return None,"That key is reserved"
    for other,assigned in bindings.items():
        if other!=action and assigned==key:
            return None,"Already assigned to "+CONTROL_LABELS[other]
    result=dict(bindings);result[action]=key
    return result,None

def translate(key,bindings):
    key=normalized_key(key)
    for action,assigned in bindings.items():
        if key==assigned:return DEFAULT_KEYS[action]
    return key

def load_preferences(path):
    preferences={"keys":dict(DEFAULT_KEYS),"audio":dict(DEFAULT_AUDIO),
                 "music_enabled":True,"sound_on":False}
    try:
        with open(path,encoding="utf8") as fh:data=json.load(fh)
    except (OSError,ValueError,TypeError):return preferences
    if not isinstance(data,dict):return preferences
    preferences["keys"]=normalize_bindings(data.get("keys",{}))
    audio=data.get("audio",{})
    if isinstance(audio,dict):
        for name,default in DEFAULT_AUDIO.items():
            try:
                value=float(audio.get(name,default))
                if value!=value:continue
                preferences["audio"][name]=max(0.,min(1.,value))
            except (TypeError,ValueError,OverflowError):pass
    for flag in ("music_enabled","sound_on"):
        if flag in data:preferences[flag]=bool(data[flag])
    return preferences

def save_preferences(path,bindings,audio,music_enabled,sound_on):
    folder=os.path.dirname(path)
    if folder:os.makedirs(folder,exist_ok=True)
    payload={"keys":dict(bindings),"audio":{name:getattr(audio,name) for name in DEFAULT_AUDIO},
             "music_enabled":bool(music_enabled),"sound_on":bool(sound_on)}
    temporary=path+".tmp"
    try:
        with open(temporary,"w",encoding="utf8") as fh:
            json.dump(payload,fh,indent=2,sort_keys=True)
            fh.flush();os.fsync(fh.fileno())
        os.replace(temporary,path)
    except OSError:
        try:os.unlink(temporary)
        except OSError:pass
        raise
