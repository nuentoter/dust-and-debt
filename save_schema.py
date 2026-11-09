"""Save validation and lightweight migration for Dust & Debt v2.9.

Validate before overwriting a good save. Old development saves with no schema
are accepted as schema 0; migration supplies safe defaults without resetting
quest and economy records.
"""
import math

SAVE_SCHEMA=2
ALLOWED_DIFFICULTIES=frozenset(("trail","standard","hard"))
ALLOWED_WEAPONS=frozenset(("peacemaker","marshal"))

def _finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def validate_save(data,world_width=60000,world_height=40960,mission_count=9):
    if not isinstance(data,dict):raise ValueError("save is not an object")
    schema=data.get("schema",0)
    if not isinstance(schema,int) or isinstance(schema,bool) or schema<0 or schema>SAVE_SCHEMA:
        raise ValueError("unsupported save schema")
    for key in ("x","y","stage"):
        if key not in data:raise ValueError("save lacks "+key)
    if not _finite(data["x"]) or not 23<=data["x"]<=world_width-23:
        raise ValueError("invalid x coordinate")
    if not _finite(data["y"]) or not 23<=data["y"]<=world_height-23:
        raise ValueError("invalid y coordinate")
    if type(data["stage"]) is not int or not 0<=data["stage"]<mission_count:
        raise ValueError("invalid story stage")
    for key in ("money","reserve","ammo","tonics","kills","field_arrests","work_finished"):
        if key in data and (type(data[key]) is not int or data[key]<0 or data[key]>10000000):
            raise ValueError("invalid "+key)
    if "hp" in data and (not _finite(data["hp"]) or not -1000<=data["hp"]<=1000):
        raise ValueError("invalid hp")
    if "contract" in data and data["contract"] is not None and not isinstance(data["contract"],dict):
        raise ValueError("invalid contract")
    if "road_contract" in data and data["road_contract"] is not None and not isinstance(data["road_contract"],dict):
        raise ValueError("invalid road contract")
    if "audio" in data and not isinstance(data["audio"],dict):
        raise ValueError("invalid audio settings")
    if "settings" in data and not isinstance(data["settings"],dict):
        raise ValueError("invalid settings")
    return True

def migrate_save(data):
    """Return a copy, retaining unknown keys and all active quest progress."""
    validate_save(data)
    migrated=dict(data)
    migrated.setdefault("weapon","peacemaker")
    if migrated["weapon"] not in ALLOWED_WEAPONS:migrated["weapon"]="peacemaker"
    migrated.setdefault("difficulty","standard")
    if migrated["difficulty"] not in ALLOWED_DIFFICULTIES:migrated["difficulty"]="standard"
    migrated["aim_assist"]=bool(migrated.get("aim_assist",False))
    settings=migrated.get("settings",{})
    settings=dict(settings)
    quality=settings.get("graphics","normal")
    settings["graphics"]=quality if quality in ("low","normal") else "normal"
    settings["weather"]=bool(settings.get("weather",True))
    settings["hints"]=bool(settings.get("hints",True))
    migrated["settings"]=settings
    migrated["schema"]=SAVE_SCHEMA
    return migrated
