from backend.curriculum import MODULES, get_module, get_prev_module, get_next_module


def get_module_by_id(module_id):
    return get_module(module_id)


def get_all_modules():
    return MODULES


def get_questions_for_module(module_id):
    module = get_module(module_id)
    if module:
        return module.get("questions", [])
    return []


def get_prev_module_id(module_id):
    prev = get_prev_module(module_id)
    return prev["id"] if prev else None


def get_next_module_id(module_id):
    next_m = get_next_module(module_id)
    return next_m["id"] if next_m else None
