# CLIN 2018 Shared Task: Spelling Correction

## Introduction

This repository harbors the scripts for handling the data that is part of the CLIN28 shared task on spelling correction. 

Automatic spell checking and correction has been subject of research for decades. Although state of the art spell checkers perform reasonably well for everyday-life applications, reaching high accuracy remains to be a challenging task. This shared task focuses on the detection and correction of spelling errors in Dutch Wikipedia texts. Wikipedia articles aim to be standard-Dutch texts, which may contain jargon. In particular, this task addresses the detection and correction of the types of spelling errors listed below:

## Data

We initially deliver one annotated document for validation purposes. A validation set consisting of 50 Wikipedia articles will follow before the end of October. The documents may contain zero, one or more spelling errors. The validation set contains all of the spelling error categories listed below. In December, a full test set will be published in the same format. 

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

### JSON

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
* ``space`` - A boolean indicating whether the word/token is followed by a space. This can be used to reconstructed the
  text prior to tokenisation.
* ``in`` - This refers to the ID of the structural element in which the word occurs, almost always a sentence. Sentence
  breaks can be detected by changes in this value. For more structural information, you'll need the original FoLiA
  documents.

**Correction specification:**
* ``class`` - The type of the error; should be one of the classes defined in [our set definition](https://github.com/proycon/folia/blob/master/setdefinitions/spellingcorrection.foliaset.xml) (use the IDs, not the labels!). These are case sensitive.
* ``span`` - A list of word IDs to which this correction applies.
* ``text`` - The text of the correction, i.e. the new word(s). This text may be an empty string in case of a deletion
  (e.g. redundant word/punctuation), or may consist of multiple space separated words in case of a run-on
  error (for example *naarhuis* -> *naar huis*).
* ``after`` - Should be used instead of ``span`` in cases of an insertion (insertion of a new word/token where
  previously none existed). The value is a string and is the ID of the word **after which** the correction is to be
  inserted.

Note that all JSON for this task should be UTF-8 encoded.

### FoLiA

The JSON option is the simpler and sufficient option for this task. But if you want to leverage the full
information available in the input document, you can fall back to use the original FoLiA input.

The FoLiA format is extensively documented; consult the [FoLiA website](https://proycon.github.io/folia), we
particularly refer to section 2.10.8 on corrections. Python
users may benefit from using our Python FoLiA library, part of [pynlpl](https://github.com/proycon/pynlpl) and
documented [here](http://pynlpl.readthedocs.io/en/latest/folia.html).

The FoLiA documents may also act as a source for further linguistic enrichment using FoLiA-aware tools such as
[frog](https://languagemachines.github.io/frog).
