try:
    import json
    import random
    import re
    with open('data/data.json') as json_file:
        GAME_DATA = json.load(json_file)
except:
    pass

# ---------------------------------------------------------------------------
# Base game object — all dynamic classes inherit from this
# ---------------------------------------------------------------------------

class GameObject:
    """
    Base class for all game objects built from object_classes in data.json.
    Provides render() once; all subclasses inherit it for free.
    __repr__ stays human-readable for debugging.
    """
    name: str = ""
    color: str = ""

    def render(self) -> str:
        return f"<{self.color}>{self.name}</{self.color}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, color={self.color!r})"

    def __format__(self, spec) -> str:
        return self.render()

    def __str__(self) -> str:
        return self.render()


# ---------------------------------------------------------------------------
# Object registries
# ---------------------------------------------------------------------------

CLASS_REGISTRY: dict[str, type] = {"game_object": GameObject}  # class_name  → Python class
OBJECT_REGISTRY: dict[str, object] = {}  # object_key  → game object instance


class GameState:
    def __init__(self):
        self.player_count = 1
        self.players = []
        self.player = None
        self.initialized = list([(str(k), None, False) for k in GAME_DATA.get("init").keys()])
        self.init_step = 0
        self.override_commands = ["help", "reset", "credits"]
        self.current_player_num = 1

    def run_intro(self):
        return "\n".join(
            [f"{GAME_DATA.get('credits')}\n\n"] + GAME_DATA.get("game_intro")
        )

    def handler_interface(self, cmd: str | None) -> str:
        for i, (init_name, init_set, initialized) in enumerate(self.initialized):
            if not initialized:
                return self.initialize(i, init_name, init_set, cmd)
        return str(self.__dict__)

    def initialize(self, i, init_name, init_set, cmd=None):
        if not init_set: init_set = init_name
        print(f"initializing {i}, {init_name}, {init_set}, {cmd}, {self.init_step}")
        steps = GAME_DATA.get("init").get(init_set).get("steps")
        step = steps[self.init_step]
        # print(step)
        if cmd is None:
            return step.get("q").format_map(self.__dict__)
        a_required = step.get("a", None)

        cmd_response = ""
        response_list = step.get("r", None)
        if response_list:
            cmd_response = response_list.get(cmd, "")
            if cmd_response:
                cmd_response = f"{random.choice(cmd_response)}\n" if isinstance(cmd_response, list) else f"{cmd_response}\n"
            if response_list.get("_", None):
                cmd_response = f"{response_list.get('_')}\n{cmd_response}"

        if a_required:
            cmd = cmd.lower()
            if isinstance(a_required, list):
                a_list = a_required
                if cmd not in a_list:
                    # print(f"{step.get("q").format_map(self.__dict__)}, {cmd_response}")
                    return cmd_response + step.get("q").format_map(self.__dict__)
            elif isinstance(a_required, str):
                pass

        game_var = step.get("game_var", None)
        if game_var:
            self._set_nested(game_var, cmd)
        game_fnc = step.get("game_fnc", None)
        if game_fnc:
            _fnc_resolved = getattr(self, game_fnc)
            _fnc_resolved(cmd)

        self.init_step += 1
        if self.init_step >= len(steps):
            self.initialized[i] = (init_name, init_set, True)
            self.init_step = 0
            return self.handler_interface(None)

        return cmd_response + steps[self.init_step].get("q").format_map(self.__dict__)

    def _set_nested(self, game_var, value):
        """Supports dot notation e.g. 'player.player_name' -> self.player.player_name"""
        if "." in game_var:
            obj_name, attr = game_var.split(".", 1)
            setattr(getattr(self, obj_name), attr, value)
        else:
            setattr(self, game_var, value)

    def init_var_override(self, cmd, game_var):
        pass

    def fnc_set_player_count(self, cmd):
        self.player_count = int(cmd)
        for i in range(self.player_count):
            self.initialized.insert(i + 2, (f"player_init_{i}", "player_init", False))
        self.initialized.pop(1)

    def fnc_new_player(self, cmd):
        self.player = Player(cmd)
        self.players.append(self.player)
        self.current_player_num += 1

# ---------------------------------------------------------------------------
# Class builder
# ---------------------------------------------------------------------------

def _topological_sort(classes: dict) -> list[str]:
    """Return class names ordered so every parent appears before its children."""
    order, visited = [], set()

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        parent = classes.get(name, {}).get("parent_class")
        if parent and parent in classes:
            visit(parent)
        order.append(name)

    for name in classes:
        visit(name)
    return order


def _resolve_attrs_and_defaults(class_name: str, classes: dict) -> tuple[list, dict]:
    """
    Walk the parent chain and additively merge _attr lists and default values.
    Returns (full_attr_list, defaults_dict).
    """
    chain = []
    current = class_name
    while current:
        chain.insert(0, current)
        current = classes.get(current, {}).get("parent_class")

    attrs    = []
    defaults = {}
    for name in chain:
        defn = classes.get(name, {})
        for attr in defn.get("_attr", []):
            if attr not in attrs:
                attrs.append(attr)
        for k, v in defn.items():
            if k not in ("_attr", "parent_class"):
                defaults[k] = v

    return attrs, defaults

def build_class_registry(game_data: dict) -> None:
    """
    Dynamically build Python classes from object_classes in data.json
    and populate CLASS_REGISTRY.
    """
    classes = game_data.get("object_classes", {})
    order   = _topological_sort(classes)

    for class_name in order:
        attrs, defaults = _resolve_attrs_and_defaults(class_name, classes)

        # Determine Python base class(es)
        parent_name = classes.get(class_name, {}).get("parent_class")
        if parent_name and parent_name in CLASS_REGISTRY:
            py_base = CLASS_REGISTRY[parent_name]
        else:
            py_base = GameObject

        def make_init(attrs, defaults):
            def __init__(self, **kwargs):
                # Apply class-level defaults first, then instance kwargs
                for attr in attrs:
                    value = kwargs.get(attr, defaults.get(attr, None))
                    setattr(self, attr, value)
                # Also apply defaults for keys not in _attr (e.g. desc, class_name)
                for k, v in defaults.items():
                    if not hasattr(self, k) or getattr(self, k) is None:
                        setattr(self, k, kwargs.get(k, v))
            return __init__

        cls = type(
            class_name.capitalize(),
            (py_base,),
            {
                "__init__": make_init(attrs, defaults),
                # Stamp class-level defaults so repr works even before instantiation
                **{k: v for k, v in defaults.items()}
            }
        )
        CLASS_REGISTRY[class_name] = cls

# ---------------------------------------------------------------------------
# Object resolver
# ---------------------------------------------------------------------------

_OBJ_TAG = re.compile(r"<o>(\w+)</o>")

def get_or_build_class(class_name: str) -> type:
    """
    Returns the Python class for class_name, building it (and any missing
    ancestors) first if needed. game_object is always the root and is
    guaranteed to exist in CLASS_REGISTRY.
    """
    # Base case — already exists, just return it
    if class_name in CLASS_REGISTRY:
        return CLASS_REGISTRY[class_name]

    class_def = GAME_DATA["object_classes"][class_name]
    parent_name = class_def.get("parent_class", "game_object")

    # Recurse — ensures parent is built before we build this class
    parent_cls = get_or_build_class(parent_name)

    # Build this class now that its parent exists
    attrs, defaults = _resolve_attrs_and_defaults(class_name, GAME_DATA["object_classes"])

    cls = type(
        class_name.capitalize(),
        (parent_cls,),
        {"__init__": make_init(attrs, defaults),
         **{k: v for k, v in defaults.items()}}
    )
    CLASS_REGISTRY[class_name] = cls
    return cls


def get_or_build_instance(object_key: str) -> GameObject | None:
    """
    Returns a new instance for object_key from object_definition,
    building its class chain via get_or_build_class if needed.
    """
    obj_def = GAME_DATA["object_definition"].get(object_key)
    if not obj_def:
        return None

    class_name = obj_def["object_class"]
    cls = get_or_build_class(class_name)

    kwargs = {k: v for k, v in obj_def.items() if k != "object_class"}
    return cls(**kwargs)

def get_parent_class(parent_class: str):
    _parent = GAME_DATA.get("object_classes").get(parent_class).get("parent_class", None)
    if _parent:
        return get_parent_class(_parent)
    return parent_class

def resolve_objects(text: str) -> str:
    for _ in range(10):
        match = _OBJ_TAG.search(text)
        if not match:
            break
        key = match.group(1)

        # Try registry first
        obj = OBJECT_REGISTRY.get(key)

        # Not found — try building it on demand and caching it
        if obj is None:
            obj = get_or_build_instance(key)
            if obj is not None:
                OBJECT_REGISTRY[key] = obj

        replacement = obj.render() if obj is not None else f"<dim>{key}</dim>"
        text = text[:match.start()] + replacement + text[match.end():]
    return text


class Player:
    def __init__(self, name):
        self.player_name = name
        self.player_class = None

test_string = "Beneath you lies a <o>labyrinth</o> of ancient stone."

print(resolve_objects(test_string))
