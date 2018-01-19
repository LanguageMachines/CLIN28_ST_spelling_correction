# CLIN 2018 Shared Task: Spelling Correction

## Introduction

This repository harbors the scripts for handling the data that is part of the CLIN28 shared task on spelling correction.

Automatic spell checking and correction has been subject of research for decades. Although state of the art spell checkers perform reasonably well for everyday-life applications, reaching high accuracy remains to be a challenging task. This shared task focuses on the detection and correction of spelling errors in Dutch Wikipedia texts. Wikipedia articles aim to be standard-Dutch texts, which may contain jargon. In particular, this task addresses the detection and correction of the types of spelling errors listed in the next section.

Note the following:
* Submitted spelling correctors will be evaluated for detection and correction of these – and only these – types of errors.
* The spelling errors do not have to be categorized into the categories that are listed below – only detected and corrected.
* In case of officially accepted spelling variation or doubt about the correct spelling, all correct variants are accepted.
* The corrections are evaluated in accordance with the Woordenlijst Nederlandse Taal (http://woordenlijst.org/) and the Leidraad (http://woordenlijst.org/leidraad).

## Errors to detect and correct

* **real-word confusions** (``confusion``), word is confused with a near neighbor (confusion with non-native spelling, homophony, grammatical errors, et cetera):
  * ik wordt → ik word
  * stijl → steil
  * hobbies → hobby’s
  * me → mijn
  * als → dan
* **split errors** (``spliterror``), compound words which are incorrectly separated:
  * beleids medewerker → beleidsmedewerker
  * lang durig → langdurig
* **runon errors** (``runonerror``), incorrect concatenation of words:
  * etcetera → et cetera
  * zeidat → zei dat
* **missing words** (``missingword``), sentence is ungrammatical due to missing elements:
  * samen met vrouw die → samen met de vrouw die
* **redundant words** (``redundantword``), sentence is ungrammatical due to redundant elements:
  * door doordat → doordat
* **missing punctuation** (``missingpunctuation``), missing diacritical symbols and hyphenation marks (other cases of missing punctuation are excluded from the task):
  * een en ander → één en ander
  * financiele → financiële
  * autoongeluk → auto-ongeluk
* **redundant punctuation** (``redundantpunctuation``), redundant diacritical symbols and hyphenation marks (other cases of redundant punctuation are excluded from the task):
  * co-assistent → coassistent
* **capitalisation errors** (``capitalizationerror``), incorrect use of capital letters:
  * Joodse → joodse
  * Minister van Onderwijs → minister van Onderwijs
  * amstelveen → Amstelveen
* **archaic spelling** (``archaic``), outdated spelling:
  *	aktie → actie
  * paardebloem → paardenbloem
* **non-word errors** (``nonworderror``), words that do not exist in Dutch:
  * voek → boek
  * assrtief → assertief

In parentheses are the class IDs for the error categories, this is how they should always be referred to in the data,
this is in line with [this FoLiA Set Definition](https://github.com/proycon/folia/blob/master/setdefinitions/spellingcorrection.foliaset.xml).

## Data

We initially deliver three annotated documents for validation purposes. A validation set consisting of 50 Wikipedia articles will follow before the end of October. The documents may contain zero, one, or more spelling errors. The validation set contains all of the spelling error categories listed below. In December, a full test set will be published in the same format.

### Data format

We deliver the trial set, the test set, and eventually the gold-standard reference in two formats: [FoLiA
XML](https://proycon.github.io/folia) and a JSON format. This JSON representation is automatically derived from the
FoLiA documents and acts as a simplified format for this task to make it more accessible and not place an unnecessarily
high burden on document parsing. It can act as input to your system as it contains all vital information, however, it is
not as rich as the original FoLiA document.

Likewise, your system may output either FoLiA XML or our JSON format. In either case, it is important to ensure your
output is valid by using the validator tools we provide. For FoLiA use the ``foliavalidator`` tool (part of
https://github.com/proycon/folia), for JSON, use the validator provided in this repository.

All data will be delivered to you in tokenised form. Tokenisation has been conducted using
[ucto](https://languagemachines.github.io/ucto). You're expected to adhere to this tokenisation, the data formats have
special facilities for merges, splits, insertions and deletions of tokens, as may naturally arise in spelling
correction.

#### JSON

Familiarity with JSON is assumed; we will merely state the specifics of our representation. At the root level, we have
``words`` and ``corrections``. Words contains a list of all words/tokens along with their ID and some other information.
Corrections contains a list of corrections on those words, this will be provided for the trial data and for the
gold-standard release after the task's end. For the test data, it will be an empty list which your system is expected to
fill. Consider the following example:

```json
{
 "words": [
   { "text": "Dit", "id": "word.1", "space": true, "in": "sentence.1" },
   { "text": "is", "id": "word.2", "space": true, "in": "sentence.1" },
   { "text": "een", "id": "word.3", "space": true, "in": "sentence.1" },
   { "text": "vooorbeeld", "id": "word.4", "space": false, "in": "sentence.1" },
   { "text": ".", "id": "word.5", "space": true, "in": "sentence.1" }
 ],
 "corrections": [
  { "class": "nonworderror", "span": ["word.4"], "text": "voorbeeld" }
 ]
}
```

This example shows one correction.

**Word Specification**:
* ``text`` - The text of the word/token, a string
* ``id`` - The ID of the word/token (string). This is used to refer back to the token. Note that although the ID often has implicit numbering indicating ordering, this is **NOT** guaranteed. The order of the words should be derived from the order they appear in the ``words`` list only. IDs are case sensitive!
* ``space`` - A boolean indicating whether the word/token is followed by a space. This can be used to reconstruct the
  text prior to tokenisation.
* ``in`` - This refers to the ID of the structural element in which the word occurs, almost always a sentence. Sentence
  breaks can be detected by changes in this value. For more structural information, you'll need the original FoLiA
  documents.

**Correction specification:**
* ``span`` - A list of word IDs to which this correction applies.
* ``text`` - The text of the correction, i.e. the new word(s). This text may be an empty string in case of a deletion
  (e.g. redundant word/punctuation), or may consist of multiple space separated words in case of a run-on
  error (for example *naarhuis* -> *naar huis*).
* ``after`` (instead of ``span``)  - Should be used instead of ``span`` in cases of an insertion (insertion of a new word/token where
  previously none existed). The value is a string and is the ID of the word **after which** the correction is to be
  inserted.
* ``confidence`` (optional) - A floating number between 0.0 and 1.0 indicating the confidence in this correction. (If not explicitly mentioned, 1.0 is assumed)
* ``class`` (optional) - The type of the error; i.e. one of the classes defined in [our set definition](https://github.com/proycon/folia/blob/master/setdefinitions/spellingcorrection.foliaset.xml) (use the IDs, not the labels!). Your system does **not** need to output this, it merely serves as extra information in the gold standard.

Note that all JSON for this task should be UTF-8 encoded.

#### FoLiA

The JSON option is the simpler and sufficient option for this task. But if you want to leverage the full
information available in the input document, you can fall back on using the original FoLiA input.

The FoLiA format is extensively documented; consult the [FoLiA website](https://proycon.github.io/folia), we
particularly refer to section 2.10.8 on corrections. Python
users may benefit from using our Python FoLiA library, part of [pynlpl](https://github.com/proycon/pynlpl) and
documented [here](http://pynlpl.readthedocs.io/en/latest/folia.html).

The FoLiA documents may also act as a source for further linguistic enrichment using FoLiA-aware tools such as
[frog](https://languagemachines.github.io/frog).

#### Notes

Some things to keep in mind:
* A correction should span one or more words, span should be specified in the right order and may only be consecutive (use multiple corrections in case of gaps).
* A correction should span the minimum amount of words/tokens, do not include leading/trailing tokens that are not corrected; E.g for *een en ander* → *één en ander*, correct only *een* → *één*.

## Evaluation

Detection and correction of spelling errors in the test documents are evaluated separately (although correction
necessarily implies detection as well), in the following way:

* Matching the detected errors to the marked errors in the gold standard annotation:
  * Precision will be measured as the proportion of correctly detected errors by the corrector in all test documents.  (i.e. irregardless of the actual correction)
  * Recall will be measured as the proportion of the marked errors in the gold standard annotations of all test documents that were detected by the corrector.
  * The F-score is the harmonic mean of the Precision and Recall.
* Matching the proposed corrections of detected errors by the spelling corrector to the corrections made in the gold standard annotations:
  * Precision will be measured as the proportion of correctly corrected errors by the corrector in all test documents.
  * Recall will be measured as the proportion of the marked errors in the gold standard annotations of all test documents that were corrected well by the corrector.
  * The F-score is the harmonic mean of the Precision and Recall.

The spelling corrector is not requested to predict the class of the spelling error. These correction classes are marked in order to describe the quality of submissions in more detail and will appear in the evaluation output.

To evaluate, run ``clin28-evaluate --ref reference.json --out youroutput.json``, see the next section.

## Tools and Installation

We provide the following tools for validation, evaluation and conversion:

 * ``clin28-validator`` - Validates whether the JSON is valid. (**Use this on your system output prior to submission!**)
 * ``clin28-evaluate`` - Implements the evaluation as specified above: evaluates a JSON output file against a JSON reference file
 * ``clin28-folia2json`` - Converts FoLiA XML to the JSON format for this task

The tools are written in Python (3.4 or above!) and available from the Python Package Index, download and install with a
simple:

    pip3 install clin28tools

For global installation, provided you have administrative rights, you can prepend ``sudo``, but we recommend using a Python virtual environment instead.

Alternatively, you can install the tools after having cloned this git repository:

    python3 setup.py install

## Good Software development

For this task we would like to encourage practice of good and sustainable academic software development. We therefore
encourage participants to make their software for this task publicly available as open source. We will judge the
software for this task using the [CLARIAH Software Quality Survey](http://softwarequality.clariah.nl/) and the highest scoring system (i.e. not necessarily
the most performant system!) will be awarded an honourable mention.

## Important dates

* 4 December 2017: test data online
* 12 January 2017: deadline for submission of source code and output
* 19 January 2018: feedback to submissions
* 26 January 2018: presenting the results at the CLIN conference
