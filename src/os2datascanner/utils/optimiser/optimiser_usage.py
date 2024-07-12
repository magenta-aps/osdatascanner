from optimiser import *

DIR = "/home/magenta/osdatascanner/src/os2datascanner/utils/optimiser/"
IN_PATH = DIR + "original_rule.json"
OUT_PATH = DIR + "output_rule.json"

def clean_rule(rule_path, output_path):
    rule_optimiser = RuleOptimiser(rule_path, output_path)
    rule_optimiser.run_optimiser()
    return rule_optimiser.clean_rule

clean = clean_rule(IN_PATH, OUT_PATH)
# print(clean)

cont = CustomContainer("or", [1, 2, 3], None)

a = sorted([1, 2, cont])

print(a)
