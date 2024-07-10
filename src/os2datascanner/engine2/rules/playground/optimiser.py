import json

class CustomContainer():
    def __init__(self, id:int, operator:str, components:list, parent=None) -> None:
        self.id = id
        self.operator = operator
        self.components = components
        self.parent = parent

        if self.operator not in ["and", "or"]:
            raise Exception(f"Invalid operator for CustomOperator[id={id}]")

    def as_dict(self):
        return {
            'type': self.operator,
            'components': [comp.as_dict() if isinstance(comp, CustomContainer) else comp for comp in self.components],
        }

    def __repr__(self):
        return str(self.as_dict())

def list_equality_no_order(arr1, arr2):
    base = arr1
    for k in arr2:
        try:
            base.remove(k)
        except ValueError:
            return False
    return not base

def find_duplicates(arr1, arr2):
    for k in arr1:
        if k in arr2:
            yield k

def inverse_extend(arr1, deletions):
    for k in deletions:
        arr1.remove(k)
    return arr1

def load_rule(path):
    with open(path) as file:
        return json.loads(file.read())
 
def dump_rule(obj):
    with open("/home/magenta/osdatascanner/src/os2datascanner/engine2/rules/playground/clean_rule.json", "wt") as file:
        json.dump(obj, file, indent=2)

def display(data):
    try:
        print(json.dumps(data, indent=2))
    except:
        print(json.dumps(json.loads(data), indent=2))

def arr_switch(arr:list, deletion, insertion):
    arr.remove(deletion)
    arr.append(insertion)
    return arr

def custom_set(arr):
    """
    Traditional set() doesn't work with
    custom classes (CustomContainer in 
    this case), and removes it entirely.
    """
    mem = []
    for k in arr:
        if k in mem:
            pass
        else:
            mem.append(k)
            yield k

def check_empty(container):
    global found_redundancy
    if container.components == []:
        print(f"Container of id={container.id} has no more components :(")
        print(f"\tRemoving container of id={container.id}")
        container.parent.components.remove(container)
        found_redundancy = True

def check_useless(container): # Useless aka AND(1), OR(1), etc ...
    global found_redundancy
    if len(container.components) == 1 and isinstance(container.components[0], int):
        print(f"Container of id={container.id} has 1 component left")
        print(f"\tRemoving container id={container.id}")
        print(f"\tGiving the parent container id={container.parent.id} his only component")
        container.parent.components.remove(container)
        container.parent.components.append(container.components[0])
        found_redundancy = True


def container_count_op(container:CustomContainer, op):
    c = 0
    for e in container.components:
        if isinstance(e, CustomContainer):
            if e.operator == op:
                c += 1
    return c

def contains_container(cont):
    return any([isinstance(i, CustomContainer) for i in cont.components])

def containify(container):
    """
    Transorms all {"type": "and" | "or", "components": [...]} 
    into the CustomContainer class, so they become easier to
    handle in python, rather than dictionaries.
    """

    global cc, containers
    for k in container.components:
        if isinstance(k, dict):
            if k["type"] == "not":
                container.components = arr_switch(arr=container.components, deletion=k, insertion=-k["rule"])
            else:
                container.components = arr_switch(arr=container.components, deletion=k, insertion=CustomContainer(cc, k["type"], k["components"], parent=container))
                cc += 1
                containers.append(container.components[-1])
                yield container.components[-1]

rule = load_rule("/home/magenta/osdatascanner/src/os2datascanner/engine2/rules/playground/rule.json")
display(rule)

cc = 1
# not(1 and 2) = not 1 or not 2
# not(1 or 2) = not 1 and not 2


"""
Not {
    And {
        1,
        -2,
    }
}

Or {
    1
    2
    And {
        -2
        3
    }
}
"""

main = CustomContainer(id=0, operator=rule["type"], components=rule["components"])
main.parent = main

found_redundancy = True
cycles = 0

while found_redundancy:
    cycles += 1
    found_redundancy = False

    future = [main]
    containers = [main]

    while future:
        for k in future:
            future.remove(k)
            future.extend(list(containify(k)))

    print(f"\n*****\nOn cycle n*[{cycles}]\n*****\n")
    for cont in containers:
        if isinstance(cont, CustomContainer):

            and_c = container_count_op(cont, "and")
            or_c = container_count_op(cont, "or")

            unique_components = list(custom_set(cont.components.copy()))
            if not list_equality_no_order(cont.components.copy(), unique_components):
                print(f"Container with id={cont.id} got stripped of duplicate elements in his components")
                print(f"\tWent from : {cont.components} to {unique_components}")
                cont.components = unique_components
                found_redundancy = True

            joined_containers = list(custom_set(cont.components))
            joined_containers.extend(list(custom_set(cont.parent.components)))

            if not list_equality_no_order(joined_containers, list(custom_set(joined_containers))):
                if cont.id != 0: # Not main
                    found_redundancy = True
                    print(f"Found redundancy between containers id={cont.id} and id={cont.parent.id}")
                    duplicates = list(find_duplicates(cont.components, cont.parent.components))

                    if cont.operator == "and" and cont.parent.operator == "or":
                        cont.parent.components = inverse_extend(cont.parent.components, duplicates)
                        print(f"\tRemoved {duplicates} from container id={cont.parent.id}")
                        print(f"\tResulting components for container id={cont.id} : {cont.components}")
                        print(f"\tResulting components for container id={cont.parent.id} : {cont.parent.components}")
                    else:
                        cont.components = inverse_extend(cont.components, duplicates)
                        print(f"\tRemoved {duplicates} from container id={cont.id}")
                        print(f"\tResulting components for container id={cont.id} : {cont.components}")
                        print(f"\tResulting components for container id={cont.parent.id} : {cont.parent.components}")

                    # On redundancy, always remove duplicate element from child container
                    # except in the case where parent is OR and child is AND.

                    # a OR b OR (b AND c) != a OR b OR (c AND True) [-]
                    # a OR b OR (b AND c) == a OR (b AND c) [+]

            nests_containers = contains_container(cont)

            if nests_containers:
                if len(cont.components) == or_c:
                    pass
                elif len(cont.components) == and_c:
                    pass

            check_empty(cont)
            check_useless(cont)

dump_rule(main.as_dict())
print("Dumped clean rule")
