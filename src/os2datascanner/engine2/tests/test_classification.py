import re

from os2datascanner.engine2.utilities.classification.engine import (
        ClassificationEngine)


characteristic_words = {
    ("en", "English"): [
        ("why", 40),
        ("of", 10),
    ],
    ("da", "Danish"): [
        ("hvorfor", 40),
        ("af", 10),
    ],
    ("no", "Norwegian Bokmål"): [
        ("hvorfor", 40),
        ("av", 10),
    ],
    ("sv", "Swedish"): [
        ("varför", 40),
        ("av", 10),
    ],
    ("fr", "French"): [
        ("pourquoi", 40),
        ("de", 10),
        ("d'", 10),
    ],
    ("es", "Castilian"): [
        ("por qué", 40),
        ("de", 10),
    ],
    ("de", "German"): [
        ("warum", 40),
        ("von", 10),
    ],
    ("nl", "Dutch"): [
        ("waarom", 40),
        ("van", 10),
    ]
}


phrases = {
    "en": "Why did any of us think this was a good idea?",
    "da": "Hvorfor tænkte nogle af os, at det var en god idé?",
    "no": "Hvorfor syntes noen av oss det var en god idé?",
    "sv": "Varför tyckte några av oss att det var en bra idé?",
    "fr": "Pourquoi certains d'entre nous ont-ils pensé que"
          " c'était une bonne idée ?",
    "es": "¿Por qué algunos de nosotros pensamos que era una buena idea?",
    "de": "Warum hielten einige von uns das für eine gute Idee?",
    "nl": "Waarom dachten sommigen van ons dat het een goed idee was?"
}


class TestEngine2Classification:
    def test_basic_classification(self):
        ce = ClassificationEngine()
        for (code, name), training in characteristic_words.items():
            kl = ce.add_classification(code, name)
            for word, weight in training:
                kl.any_of.append(
                        ClassificationEngine.WordTerm(weight, word, re.I))

        for code, in_phrase in phrases.items():
            (classification, weight) = ce.classify(in_phrase)[0]
            assert classification.ident == code
            assert weight == 50

    def test_threshold(self):
        ce = ClassificationEngine()

        kl = ce.add_classification("ev", "Evil", threshold=40)
        kl.at_least_one_of.append(ClassificationEngine.WordTerm(10, "evil"))
        kl.at_least_one_of.append(ClassificationEngine.WordTerm(10, "nasty"))
        kl.at_least_one_of.append(ClassificationEngine.WordTerm(10, "wicked"))
        kl.at_least_one_of.append(ClassificationEngine.WordTerm(10, "vicious"))
        kl.at_least_one_of.append(ClassificationEngine.WordTerm(
                10, "malevolent"))

        text = """
        Mwahahahaha! Thanks to my new evil flock of bats my nasty, wicked plans
        will finally come to fruition!"""

        assert ce.classify(text) == []

        text += """
        My vicious, malevolent revenge is within my grasp!!"""

        assert ce.classify(text)[0][0].ident == "ev"

    def test_contradiction(self):
        ce = ClassificationEngine()

        kl = ce.add_classification("ev", "Evil", threshold=10)
        kl.at_least_one_of.append(ClassificationEngine.WordTerm(10, "evil"))
        kl.none_of.append(ClassificationEngine.WordTerm(None, "puppies"))

        text = "I am so evil..."

        assert ce.classify(text)[0][0].ident == "ev"

        text += """
        ... that I only spend HALF of my weekends rescuing puppies and giving
        them treats"""

        assert ce.classify(text) == []
