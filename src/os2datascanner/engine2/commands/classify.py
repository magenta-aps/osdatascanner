import json
from os2datascanner.engine2.utilities.classification.compat import (
        taxon_json_taxonomy_to_classification_engine)


def classify(taxonomy, *files_to_scan):
    with open(taxonomy, "rt") as fp:
        engine = taxon_json_taxonomy_to_classification_engine(json.load(fp))

    results = []

    for f in files_to_scan:
        print(f"File to be classified : {f}")
        with open(f, "rt") as fp:
            sub_result = []
            for classification, weight in engine.classify(fp.read())[:5]:
                sub_result.append(f"\t {classification.ident} {classification.label} {weight}")
            results.append(sub_result)

    return results
