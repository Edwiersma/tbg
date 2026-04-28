GAME_DATA = {
    "object_classes": {
        "game_object": {"name": "default", "color": "dim"},
        "obj_name": {"parent_class": "game_object", "color": "purple"},
        "location": {"parent_class": "game_object", "color": "dim"},
        "item": {"parent_class": "game_object", "color": "green"},
        "weapon": {"parent_class": "item", "damage": 0, "damage_type": None, "slot": None},
        "armor": {"parent_class": "item", "armor_value": 0, "armor_type": None, "slot": None},
        "player_class": {"parent_class": "game_object", "class_name": "default", "class_weapon": None, "desc": "default"}
    },
    "object_definition": {
        "labyrinth": {"name": "labyrinth", "object_class": "location"},
        "sword_01": {"name": "sword", "object_class": "weapon"},
        "sword_02": {"name": "+1 sword", "object_class": "weapon", "damage": 10, "damage_type": "slash",
                     "slot": "1hand"},
        "helm_01": {"name": "Leather Helmet", "object_class": "armor", "armor": 5, "armor_type": "leather",
                    "slot": "head"},
        "shield_01": {"name": "Buckler", "object_class": "armor", "armor": 15, "armor_type": "metal", "slot": "1hand"}
    }
}


# ---------------------------------------------------------------------------
# Base game object — all dynamic classes inherit from this
# ---------------------------------------------------------------------------

class game_object:
    name: str = ""
    color: str = ""
    def __init__(self, name: str, **kwargs):
        self.name = name

    def render(self) -> str:
        return f"<{self.color}>{self.name}</{self.color}>"

    def __repr__(self) -> str:
        return f"{self.__class__} {self.render()}"

# ---------------------------------------------------------------------------
# Object registries
# ---------------------------------------------------------------------------


CLASS_REGISTRY: dict[str, type] = {"game_object": game_object}  # class_name  → Python class
OBJECT_REGISTRY: dict[str, object] = {}  # object_key  → game object instance


def create_class_object(dependencies):
    def make_init(defaults):
        def __init__(self, **kwargs):
            name = kwargs.pop("name", defaults.get("name", ""))
            game_object.__init__(self, name)
            all_defaults = {}
            for parent in reversed(type(self).__mro__):
                for k, v in vars(parent).items():
                    if not k.startswith("_") and not callable(v):
                        all_defaults[k] = v
            all_defaults.update(defaults)
            for k, v in all_defaults.items():
                if k != "name":
                    setattr(self, k, kwargs.get(k, v))
        return __init__

    created_classes = []
    for class_name in dependencies:
        class_def = GAME_DATA["object_classes"][class_name]
        parent_name = class_def.get("parent_class", "game_object")
        structure = {k: v for k, v in class_def.items() if k not in ("_attr", "parent_class")}
        print(CLASS_REGISTRY[parent_name].__dict__)
        cls = type(class_name, (CLASS_REGISTRY[parent_name],), {**structure, "__init__": make_init(dict(structure))})
        CLASS_REGISTRY[class_name] = cls
        created_classes.append(cls)
    return created_classes


def resolve_class_dependency(resolve_class: str, dependencies=None):
    if dependencies is None:
        dependencies = list()
    if resolve_class in CLASS_REGISTRY:
        return CLASS_REGISTRY[resolve_class] if not dependencies else create_class_object(dependencies)[-1]
    _parent = str(GAME_DATA.get("object_classes").get(resolve_class).get("parent_class", None))
    if _parent:
        dependencies.insert(0, resolve_class)
        return resolve_class_dependency(_parent, dependencies)


def create_instance(struct):
    cls = resolve_class_dependency(struct.get("object_class"))
    struct.pop("object_class")
    inst = cls(**struct)
    return inst


for k, v in GAME_DATA["object_definition"].items():
    OBJECT_REGISTRY[k] = create_instance(v)

sword_02 = OBJECT_REGISTRY["sword_02"]
print(sword_02)
