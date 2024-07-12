import json

rule_ids = {
    1:'{"type":"cpr","modulus_11":true,"ignore_irrelevant":true,"examine_context":true,"exceptions":""}',
    2: '{"type":"address","whitelist":[],"blacklist":[]}',
    3: '{"type":"name","whitelist":[],"blacklist":[],"expansive":false}',
    4: '{"type":"name","whitelist":[],"blacklist":[],"expansive":true}',
    5: '{"type":"ordered-wordlist","dataset":"da_20211018_laegehaandbog_stikord"}',
    6: '{"type":"passport"}'
}

class RuleOptimiser():
    def __init__(self, default_input_path: str, default_output_path: str) -> None:
        self.IN_PATH = default_input_path
        self.OUT_PATH = default_output_path
        self.containers: list['CustomContainer'] = []
        self.found_redundancy: bool = True
        self.cycles: int = 0
        self.setup()

    @property
    def clean_rule(self):
        return load_json(self.OUT_PATH)

    def setup(self):
        """Copies the original rule into
        another file where it is cleaned"""
        obj = load_json(self.IN_PATH, extensive=True)
        dump_json(obj, self.OUT_PATH)

    def containify(self, container: 'CustomContainer'):
        """Transforms all {"type": "and" | "or", "components": [...]} 
        into the CustomContainer class, so they become easier to
        handle in python, rather than dictionaries. Not k becomes -k.

        *JSON to CustomContainer*"""

        for k in container.components:
            if isinstance(k, dict):
                if k["type"] == "not":
                    container.components = arr_switch(arr=container.components, deletion=k, insertion=-k["rule"])
                else:
                    new = CustomContainer(k["type"], k["components"], container)
                    container.components = arr_switch(arr=container.components, deletion=k, insertion=new)
                    self.containers.append(container.components[-1])
                    yield container.components[-1]


    def get_containers(self, main: 'CustomContainer'):
        """Gets a list of all the containers.
        Repeats itself with containify, but
        otherwise the code wouldn't work."""
        found = [main]
        next_up: list[CustomContainer] = [main]
        while next_up:
            for cont in next_up:
                for comp in cont.components:
                    if isinstance(comp, dict):
                        new = CustomContainer(comp["type"], comp["components"], cont)
                        found.append(new)
                        cont.components.remove(comp)
                        cont.components.append(new)
                        self.containers.append(new) # [new piece of code]
                    elif isinstance(comp, CustomContainer):
                        found.append(comp)
                next_up.remove(cont)
        return found


    def check_empty(self, container:'CustomContainer'):
        # Checks if container has no components i.e. AND(null) | OR(null)
        if not container.components:
            try:
                container.parent.components.remove(container)
                self.containers.remove(container)
                self.found_redundancy = True
            except ValueError:
                pass
            return True
        return False


    def check_useless(self, container:'CustomContainer'):
        # Useless i.e. AND(1), OR(1), etc ...
        if len(container.components) == 1:
            try:
                container.parent.components = arr_switch(container.parent.components, container, container.components[0])
                self.containers.remove(container)
                self.found_redundancy = True
            except ValueError:
                pass
            return True
        return False


    def check_symbol_redundancy(self, container:'CustomContainer'):
        # Checks for AND(n, -n) | OR(n, -n)
        mem = []
        for k in container.components:
            mem.append(k)
            if isinstance(k, int):
                if -k in mem:
                    container.parent.components.remove(container)
                    self.containers.remove(container)
                    self.found_redundancy = True
                    return True
        return False

    def optimisation_cycle(self):
        """Does all the checks on the loaded rule as cycles.
        If a cycle completed, a new one starts if the previous
        one found anything. If not, main() ends."""
        rule = load_json(self.OUT_PATH)

        main = CustomContainer(operator=rule["type"], components=rule["components"])
        main.parent = main

        self.found_redundancy = True
        self.cycles = 0

        while self.found_redundancy:
            self.cycles += 1
            self.found_redundancy = False

            future = [main]
            self.containers = [main]


            while future:
                for k in future:
                    future.remove(k)
                    future.extend(list(self.containify(k)))

            self.containers.extend(self.get_containers(main))
            self.containers = list(remove_duplicates(self.containers))

            for cont in self.containers:
                if isinstance(cont, CustomContainer):

                    unique_components = list(remove_duplicates(cont.components.copy()))
                    if not list_equality_no_order(cont.components.copy(), unique_components):
                        cont.components = unique_components
                        self.found_redundancy = True

                    duplicates = list(find_duplicates(cont.components, cont.parent.components))

                    if duplicates and cont != main:
                        self.found_redundancy = True

                        duplicates = list(find_duplicates(cont.components, cont.parent.components))

                        if cont.operator == "and" and cont.parent.operator == "or":
                            cont.parent.components = inverse_extend(cont.parent.components, duplicates)
                        else:
                            cont.components = inverse_extend(cont.components, duplicates)

                        # On redundancy, always remove duplicate element from child container
                        # except in the case where parent is OR and child is AND.

                        # a OR b OR (b AND c) != a OR b OR (c AND True) [-]
                        # a OR b OR (b AND c) == a OR (b AND c) [+]

                    if cont.operator == cont.parent.operator and cont != main:
                        try:
                            cont.parent.components.remove(cont)
                            self.containers.remove(cont)
                            cont.parent.components.extend(cont.components)
                            continue
                        except ValueError:
                            pass
                    if self.check_empty(cont) or self.check_useless(cont) or self.check_symbol_redundancy(cont):
                        continue

        dump_json(main.as_dict(), self.OUT_PATH)
        return self.cycles > 1 # If it did more than 1 cycle, it means it found something

    def reformat_rule(self, path):
        obj = str(load_json(path))
        for id in rule_ids:
            obj = obj.replace(str(id), rule_ids[id])
        obj = obj.replace("'", '"') # Fixing some double | single quote problems
        obj = json.loads(obj)
        with open(self.OUT_PATH, "wt") as file:
            json.dump(obj, file)

    def run_optimiser(self):
        refactored = True
        while refactored:
            refactored = self.optimisation_cycle()
            # Get previous cycles. 
            # While previous optimisation_cycle() found stuff, run it again.
            # Maybe check for risk of infinite recursion
        self.reformat_rule(self.OUT_PATH)


class CustomContainer():
    """CustomContainer class for being able to work
    with the rule dictionairies easier.
    A container is a recognised by this form :
    {"type": "and" | "or", "components": [...]}"""

    def __init__(self, operator: str, components: list, parent=None) -> None:
        self.operator = operator
        self.components = components
        self.parent:'CustomContainer' = parent

        if self.operator not in ["and", "or"]:
            raise ValueError(f"Invalid operator[op={self.operator}]")

    def as_dict(self):
        """
        Returns the dictionairy form of this object. Usefull for re-converting to json later on.
        """
        return {
            'type': self.operator,
            'components': [comp.as_dict() if isinstance(comp, CustomContainer) else comp for comp in self.components],
        }

    def __repr__(self):
        """Used for printing the resulting object, so you dont
        see < __main__ CustomContainer object at x567df78fd>"""
        return str(self.as_dict())

def list_equality_no_order(arr1, arr2):
    """In python [1, 2, 3] == [3, 2, 1] equals False.
    In our case, we just want to check if two containers
    have the same components. This function detects any
    elements that do not occur in both. If none are found,
    they are identical."""
    base = arr1
    for k in arr2:
        try:
            base.remove(k)
        except ValueError:
            # Can't remove because it isn't there
            return False
    # Return not (is there anything left in base). True if empty else False
    return not base

def find_duplicates(arr1, arr2):
    # Yields any element that appears in both.
    for k in arr1:
        if k in arr2:
            yield k

def inverse_extend(arr1, deletions):
    """Given a base array and a list of elements,
    removes from the base array each 
    element in that list."""
    for k in deletions:
        try:
            arr1.remove(k)
        except ValueError:
            raise ValueError("ValueError occurred in inverse_extend()")
    return arr1

def load_json(path, extensive=False):
    # Loads json object from given path
    with open(path) as file:
        obj = file.read()
        if extensive:
            for id in rule_ids:
                obj = obj.replace(rule_ids[id], str(id))
        return json.loads(obj)
 
def dump_json(obj, output_path):
    # Dumps python dict object as json to given path
    with open(output_path, "wt") as file:
        json.dump(obj, file, indent=4)

def display(data):
    # Displays CustomContainer object as a dict
    try:
        print(json.dumps(data, indent=4))
    except:
        print(json.dumps(json.loads(data), indent=4))

def arr_switch(arr:list, deletion, insertion):
    """Maybe useless, but quite frequently had
    to remove a and append b to a list, so
    this function does just that.
    Switches in given array a for b."""
    arr.remove(deletion)
    arr.append(insertion)
    return arr

def remove_duplicates(arr):
    """Traditional set() doesn't work with
    custom classes (CustomContainer in 
    this case), and removes it entirely."""
    mem = []
    for k in arr:
        if k in mem:
            pass
        else:
            mem.append(k)
            yield k

def container_count_op(container:CustomContainer, op):
    # Returns amount of containers *with given operator* directly in another one.
    c = 0
    for e in container.components:
        if isinstance(e, CustomContainer):
            if e.operator == op:
                c += 1
    return c

def contains_container(cont):
    # Boolean of (cont has any containers directly inside ?)
    return any(isinstance(i, CustomContainer) for i in cont.components)
