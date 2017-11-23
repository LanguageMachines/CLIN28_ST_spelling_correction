import sys
import os
import codecs
import json

class ValidationError(Exception):
    pass

class CLIN28JSON:
    def __init__(self, filename):
        if not os.path.exists(filename):
            raise FileExistsError("File not found: " + filename)

        with open(filename,'rb') as f:
            reader = codecs.getreader('utf-8')
            try:
                self.data = json.load(reader(f))
            except:
                raise ValidationError("File is not valid JSON!")

        self.index = {}
        self.validate()

    def validate(self):
        self.index = {}
        if 'words' not in self.data:
            return ValidationError("No words found")
        if 'corrections' not in self.data:
            return ValidationError("No corrections found")
        for key in self.data:
            if key not in ('words','corrections'):
                print("WARNING: Unknown key '" + key + "' will be ignored!",file=sys.stderr)
        for word in self.words():
            if 'id' not in word or not word['id']:
                raise ValidationError("Word does not have an ID! " + repr(word))
            self.index[word['id']] = word
            if 'text' not in word or not word['text']:
                raise ValidationError("Word does not have a text! " + repr(word))
            for key in word:
                if key not in ('text','id','space','in'):
                    print("WARNING: Unknown key '" + key + "' for word " + repr(word) + " will be ignored!",file=sys.stderr)
        for correction in self.corrections():
            if 'span' not in correction or not correction['span']:
                if 'after' not in correction or not correction['after']:
                    raise ValidationError("Correction does not have a 'span' (or 'after') property! " + repr(correction))
                elif correction['after'] not in self.index:
                    raise ValidationError("Correction's 'after' property refers to a non-existing word ID! (" + correction['after'] + ") " + repr(correction))
            else:
                for wordid in correction['span']:
                    if wordid not in self.index:
                        raise ValidationError("Correction's 'span' property refers to a non-existing word ID! (" + wordid + ") " + repr(correction))
            for key in correction:
                if key not in ('text','span','after','confidence','class'):
                    print("WARNING: Unknown key '" + key + "' for correction " + repr(correction) + " will be ignored!",file=sys.stderr)
                if key == 'confidence':
                    try:
                        correction['confidence'] = float(correction['confidence'])
                    except:
                        raise ValidationError("Invalid confidence value (" + str(correction['confidence']) + ") " + repr(correction))
                    if correction['confidence'] < 0 or correction['confidence'] > 0:
                        raise ValidationError("Confidence value out of bounds (" + str(correction['confidence']) + ") " + repr(correction))

    def words(self):
        for word in self.data['words']:
            yield word

    def corrections(self):
        for correction in self.data['corrections']:
            yield correction


    def __iter__(self):
        for key in self.data:
            yield key

    def items(self):
        return self.data.items()
    def keys(self):
        return self.data.keys()
    def values(self):
        return self.data.values()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.index:
            return self.index[key]
        return self.data[key]




