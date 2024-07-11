import json

class CustomContainer():
    """
    CustomContainer class for being able to work
    with the rule dictionairies easier. Takes
    an id to be able to recognise it in the logs.
    A container is a recognised by this form :
    {"type": "and" | "or", "components": [...]}
    """

    def __init__(self, id:int, operator:str, components:list, parent=None) -> None:
        self.id = id
        self.operator = operator
        self.components = components
        self.parent = parent

        if self.operator not in ["and", "or"]:
            raise Exception(f"Invalid operator[op={self.operator}] for CustomOperator[id={id}]")

    def as_dict(self):
        """
        Returns the dictionairy form of this object. Usefull for re-converting to json later on.
        """
        return {
            'type': self.operator,
            'components': [comp.as_dict() if isinstance(comp, CustomContainer) else comp for comp in self.components],
        }

    def __repr__(self):
        """
        Used for printing the resulting object, so you dont
        see < __main__ CustomContainer object at x567df78fd>
        """
        return str(self.as_dict())

def list_equality_no_order(arr1, arr2):
    """
    In python [1, 2, 3] == [3, 2, 1] equals False.
    In our case, we just want to check if two containers
    have the same components. This function detects any
    elements that do not occur in both. If none are found,
    they are identical.
    """
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
    """
    Does the opposite of the extend() method.
    Given a base array and a list of elements,
    removes each from the base array each 
    element in that list.
    """
    for k in deletions:
        try:
            arr1.remove(k)
        except ValueError:
            print("[!!] Warning [!!]")
            print(f"\tTried to remove {k} from {arr1}, but got ValueError")
            print(f"\tThis is not supposed to happen ...")
    return arr1

def load_rule(path):
    # Loads json rule form given path
    with open(path) as file:
        return json.loads(file.read())
 
def dump_rule(obj, output_path):
    # Dumps python dict object as json to given path
    with open(output_path, "wt") as file:
        json.dump(obj, file, indent=2)

def display(data):
    # Displays CustomContainer object as a dict
    try:
        print(json.dumps(data, indent=2))
    except:
        print(json.dumps(json.loads(data), indent=2))

def arr_switch(arr:list, deletion, insertion):
    """
    Maybe useless, but quite frequently had
    to remove a and append b to a list, so
    this function does just that.
    Switches in given array a for b.
    """
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

def check_empty(container:CustomContainer):
    # Checks if container has no components i.e. AND(null) | OR(null)
    global found_redundancy
    if not container.components:
        print(f"Container of id={container.id} has no more components :(")
        print(f"\tRemoving container of id={container.id}")
        try:
            container.parent.components.remove(container)
            containers.remove(container)
            found_redundancy = True
        except Exception as e:
            print(f"\t[-] Failed to remove container id={container.id}, was already removed from its parent from prior redundancy")
            print(f"\tException encountered : {str(e)}")

def check_useless(container:CustomContainer):
    # Useless i.e. AND(1), OR(1), etc ...
    global found_redundancy
    if len(container.components) == 1:
        print(f"Container of id={container.id} has 1 component left")
        print(f"\tRemoving container id={container.id}")
        print(f"\tGiving the parent container id={container.parent.id} his only component")
        try:
            container.parent.components = arr_switch(container.parent.components, container, container.components[0])
            containers.remove(container)
            found_redundancy = True
        except Exception as e:
            print(f"\t[-] Failed to remove container id={container.id}, was already removed from its parent from prior redundancy")
            print(f"\tException encountered : {str(e)}")

def check_symbol_redundancy(container:CustomContainer):
    # Checks for AND(n, -n) | OR(n, -n)
    global found_redundancy
    mem = []
    for k in container.components:
        mem.append(k)
        if isinstance(k, int):
            if -k in mem:
                print("\n********** [!!] Warning [!!] **********")
                print(f"Found symbol redundancy in container id={container.id}")
                print(f"\tContainer has {k} and {-k} in its components")

                container.parent.components.remove(container)
                containers.remove(container)
                return_value = (container.operator == "or")
                # Neat little trick above. If 1 or -1, always true. 1 and -1, always false

                print(f"Container of id={container.id} was removed for always returning {return_value}")
                print("********** [!!] Warning [!!] **********\n")
                found_redundancy = True

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
    return any([isinstance(i, CustomContainer) for i in cont.components])

def containify(container):
    """
    Transforms all {"type": "and" | "or", "components": [...]} 
    into the CustomContainer class, so they become easier to
    handle in python, rather than dictionaries. Not k becomes -k.

    *JSON to CustomContainer*
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

def get_containers(main):
    """
    Gets a list of all the containers.
    Repeats itself with containify, but
    otherwise the code wouldn't work.
    """
    global cc
    found = [main]
    next_up:list[CustomContainer] = [main]
    while next_up:
        for cont in next_up:
            for comp in cont.components:
                if isinstance(comp, dict):
                    print("[!] Found a dict instance whilst doing get_containers()")
                    print(f"\tFound in container id={cont.id}")
                    print(f"Dict in question : {comp}")
                    new = CustomContainer(cc, comp["type"], comp["components"], cont)
                    found.append(new)
                    cont.components.remove(comp)
                    cont.components.append(new)
                    cc += 1
                elif isinstance(comp, CustomContainer):
                    found.append(comp)
            next_up.remove(cont)
    return found


DIR = "/home/magenta/osdatascanner/src/os2datascanner/engine2/rules/playground/"
IN_PATH = "/home/magenta/osdatascanner/src/os2datascanner/engine2/rules/playground/input_rule.json"
OUT_PATH = "/home/magenta/osdatascanner/src/os2datascanner/engine2/rules/playground/output_rule.json"


with open(DIR + "original_rule.json", "rt") as file:
    obj = json.load(file)

with open(IN_PATH, "wt") as file:
    json.dump(obj, file)

containers = []

def main(input_path, output_path):
    """
    Does all the checks on the loaded rule as cycles.
    If a cycle completed, a new one starts if the previous
    one found anything. If not, main() ends.
    """
    global cc, found_redundancy, cycles, containers
    rule = load_rule(input_path)
    display(rule)

    cc = 1

    main = CustomContainer(id=0, operator=rule["type"], components=rule["components"])
    main.parent = main

    found_redundancy = True
    cycles = 0

    print("\nStart of this main\n")


    while found_redundancy:
        cycles += 1
        found_redundancy = False

        future = [main]
        containers = [main]


        while future:
            for k in future:
                future.remove(k)
                future.extend(list(containify(k)))

        containers.extend(get_containers(main))
        containers = list(custom_set(containers))

        print(f"\n******************\n* On cycle n.[{cycles}] *\n******************\n")
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

                duplicates = list(find_duplicates(cont.components, cont.parent.components))

                if duplicates and cont.id != 0: # Not main
                    found_redundancy = True
                    
                    if cont.components == cont.parent.components:
                        print(f"Identical components between container id={cont.id} and id={cont.parent.id}")

                    print(f"Found duplicates between containers id={cont.id} and id={cont.parent.id}")
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

                else:
                    if cont.operator == cont.parent.operator and cont.id != 0: # Not main
                        print("Found redundancy of same type nested containers")
                        try:
                            cont.parent.components.remove(cont)
                            containers.remove(cont)
                            cont.parent.components.extend(cont.components)
                            print(f"\tResulting components for container id={cont.parent.id} : {cont.parent.components}")
                        except Exception as e:
                            print(f"\t[-] Failed to remove container id={cont.id}, was already removed from its parent from prior redundancy")
                            print(f"\tException encountered : {str(e)}")

                check_empty(cont)
                check_useless(cont)
                check_symbol_redundancy(cont)
                      
    dump_rule(main.as_dict(), output_path)
    print("Dumped clean rule")
    print("\nEnd of this main()\n")
    return cycles > 1 # If it did more than 1 cycle, it means it found something


refactored = True
while refactored:
    refactored = main(IN_PATH, IN_PATH) # Get previous cycles. 
    # While previous main() found stuff, run main() again.
    # Maybe check for risk of infinite recursion
