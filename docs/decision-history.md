# Decision history

OSdatascanner is fairly well documented in a technical sense. That is, the code
is mostly written in a self-explanatory way. However, there is a gap between
understanding how something works and *why it should work*.

This chapter documents the decisions made along the way, and is intended to be
a source of consultation in case of considerations about removing code or 
altering functionality.

## Rule validation

Some rules have additional validation logic. This logic is intended to weed out
false positives, and often stem from real-world cases.

### CPRRule

The CPR rule matches 10-digit numbers through a regular expression. These 
numbers are allowed to be separated at specific places by specific symbols: 
The first six digits may not be separated. Digit 6 and digit 7 may be 
separated by a space, a tabulation, or one of the symbols `-` (with spaces on 
either side), `/`,  or `.`. The last 4 digits must not be separated.

In addition, CPRRule has a few validation options.

#### Modulus-11 check

Danish CPR-numbers issued before the 1st of October 2007 calculate their last 
digit by the ["Modulus-11"-method] [1]. CPR-numbers from some dates are 
[exempt from this check] [2]. This exception is considered in OSdatascanners 
modulus-11 check, and exempted numbers are considered valid CPR-numbers.

This validation serves as an initial method to ensure that any 10-digit number 
identified is indeed a legitimate and valid Danish CPR-number.

#### Probability check

The CPRRule can also calculate a probability for the CPR-number. The check 
works by calculating all valid CPR-numbers for the birth date of the 
checked number, and finding the index of the checked number in the sequence of 
all valid numbers.

Since numbers are generated sequentially, the later numbers 
are less likely to be in use than the earlier numbers in the sequence. If the
CPR-number is not valid for the given birth date of the number, the probability
is zero.

If the birth date of the CPR-number is in the future at the time of checking,
the probability will always be zero.

The check was [implemented] [3] in order for the report module to be able to 
show the most likely CPR matches in the UI first.

#### Context check

The CPRRule context check validation consists of several checks.

The context check is implemented as a single option when adding the CPRRule to 
a custom rule, and essentially allows OSdatascanner to disregard CPR-like 
numbers based on the context present around the matched number.

Below, the different checks are presented in order of application.

##### Bin check

As the rule matches the content with a regular expression, it differentiates 
between all 10-digit numbers, and the numbers identified as CPR-numbers.

All found numbers are then divided into bins, and each bin can then *allow* 
its contained numbers to register as a match, based on a few rules:

1. The number of valid CPR-numbers in the bin make up at least 15% of all 
numbers in the bin.

2. The number of valid CPR-numbers in at least one neighbouring bin make up at 
least 15% of the numbers in that bin.

If both of these requirements are not met, the valid CPR-numbers in those bins 
are not considered further.

This check is [implemented] [4] in consideration of a specific case, where a 
customer has spreadsheets with a large armount of 10-digit numbers, some of 
which may coincidentally be valid CPR-numbers.

This check makes sure, that in files with a few CPR-numbers in between large 
amounts of *invalid* numbers, we assume all 10-digit numbers are not 
CPR-numbers. If the file contains a local high density of valid numbers, those 
will still be considered further.

The cutoff value of 15% is set to be considerably higher than the random 
chance that a 10-digit number will be a valid CPR-number: 3.72%. This number 
is calculated purely from the restrictions on the first 4 digits, and does not 
take into account modulus-11 or similar.

##### Blacklist

If any of the words from the blacklist are present in the content of the 
scanned object, no matches are validated. The blacklist contains the following 
words: `p-nr`, `p.nr`, `p-nummer`, `pnr`, `customer no`, `customer-no`, 
`bilagsnummer`, `order number`, `ordrenummer`, `fakturanummer`, `faknr`, 
`fak-nr`, `tullstatistisk`, `tullstatistik`, `test report no`, `protocol no.`, 
`dhk:tx`.

The words in the blacklist are found by identifying unique words, which we 
only [ever see present] [5] in a certain type of file, which will *never* 
contain Danish CPR numbers.

##### Whitelist

If the abbreviation "cpr" (case insensitive) is present up to 3 words away 
from the matched number, the match is validated by context, no matter the 
results of the the following checks.

##### Delimiter balance

If the immediate context, within 3 words, of the match contains an unbalanced 
amount of delimiters, that is either `()`, `[]`, `{}`, `<>`, `<? ?>`, `<% %>`, 
or `/* */`, the match will be invalidated.

This check is implemented based on false positives identified by a specific
client.

##### Surrounding symbols

If one of the symbols `+`, `-`, `!`, `#`, or `%` are within 3 words of the 
matched number, the match will be invalidated.

This check is implemented based on false positives identified by a specific
client.

##### Surrounding numbers

If the word immediately before or after the matched number is another number, 
and that number does not match the simple CPR-number regex, the matched number 
is invalidated.

This is because other non-CPR-like numbers before or after the matched number 
indicates, that the matched number is not really a CPR-number, but rather part 
of a larger number, which is separated by spaces.

Do note that a number separated from the CPR-number by a symbol, such as a 
parenthesis, is not considered immediately before or after the CPR-number,
the _symbol_ is.

##### Surrounding mixed case words

If the word immediately before or after the matched number is a word with 
mixed case -- that is, a word which is not lowercase (`magenta`), uppercase 
(`MAGENTA`). or capitalized (`Magenta`) -- the matched number is invalidated.

This is because mixed case words indicate, that the string is randomly 
generated, maybe part of an encrypted string or similar.

#### Exceptions

When adding a new CPRRule to a CustomRule, it is possible to define a list of 
10-digit numbers, which should *not* be matched. All numbers present in this 
list are invalidated, even if they are valid Danish CPR-numbers.

This is [implemented] [6] to answer a concern from some clients, after they 
looked up some false positives in the Danish CPR register, and confirmed that 
a lot of the numbers validated with the CPRRule are not in use. We considered 
consulting the register during a scan, but decided against it due to 
performance concerns.

It is possible, in the future, that we would implement a call to the CPR 
register to save a temporary dump when a scan is run, which we can then refer 
to during scans.


### NameRule

OSdatascanners name rule is made to match names belonging to people. The basic 
regular exression looks for up to five instances, and at least two, of 
individual names, which are each identified as up to two "simple names" 
connected by a hyphen. A simple name is a word consisting of an upper case 
letter, then either nothing more, a period or only lower case letters.

The first instance of these individual names are identified as the first name, 
the last instance is the last name, and each other instance in between are 
middle names.

#### Compare to list of names

The rule compares to a list of all first names and last names in Denmark from
2014. If the found first and last names are present in the lists, the match 
probability is 100%, otherwise, if only one of the found names is present in
the lists, the match probability is 50%.

#### Expansive search

As an optional setting, the rule can expand its search. After identifying full
names, the rule will aggressively search for strings that could potentially be
part of a name (including individual capital letters). Any matches found in this
expansive search have a probability of 10%.

Previously, this was default behaviour, but resulted in so many false positives
that the rule was effectively unusable.


### AddressRule

OSdatascanner can scan for addresses with the built-in AddressRule. This rule
matches Danish addresses by the rules specified [here] [7].

#### Compare to list of addresses

For validation, matched streets are compared to a list of Danish street names.
The found street names must be contained in this list for the rule to match.



[1]: https://cpr.dk/media/12066/personnummeret-i-cpr.pdf "Method for performing a modulus-11 check."

[2]: https://cpr.dk/cpr-systemet/personnumre-uden-kontrolciffer-modulus-11-kontrol "CPR-numbers exempt from modulus-11 check."

[3]: https://redmine.magenta.dk/issues/34360 "[For Internal Use] Ticket about implementing probability check in CPRRule."

[4]: https://redmine.magenta.dk/issues/56007 "[For Internal Use] Ticket about implementing bin check in CPRRule."

[5]: https://redmine.magenta.dk/issues/45892 "[For Internal Use] Ticket about extending the blacklisted expressions in CPRRule."

[6]: https://redmine.magenta.dk/issues/58526 "[For Internal Use] Ticket for adding exception list to CPRRule."

[7]: https://danmarksadresser.dk/regler-og-vejledning/adresser/ "Description of the construction of Danish addresses."