import pandas as pd
import spacy
from nltk.stem.wordnet import WordNetLemmatizer
from collections.abc import Iterable
from datetime import date
from os import path
from io import StringIO
import re

nlp = spacy.load('en_core_web_sm')

CSV_PATH = "global_logs.csv"
SUBJECTS = {"nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"}
OBJECTS = {"dobj", "dative", "attr", "oprd"}
BREAKER_POS = {"CCONJ", "VERB"}
NEGATIONS = {"no", "not", "n't", "never", "none"}


def main():
    logs_df = pd.read_csv(CSV_PATH)
    print("processing logs..")
    print(logs_df.head())
    process_logs(logs_df)

def clean_error(text):
    pattern = r"(WARNING \|)|(ERROR   \|)|(WARNING:)"
    match = re.search(pattern, text)

    if match:
        return text.replace(match[0], "")
    else:
        return text
    
def process_logs(logs_df):
    svo_aggregate = {}
    csv_df = pd.DataFrame(columns=['ID', 'SVOs'])
    ID = ""
    GLOBAL_SVOS = []
    for _, row in logs_df.iterrows():
        if (ID == ""):
            ID = row['ID']
        elif (ID != row['ID']):
            # print(GLOBAL_SVOS)
            if len(GLOBAL_SVOS) > 1:
                new_data = pd.DataFrame({'ID': [ID], 'SVOs': [GLOBAL_SVOS]})
                csv_df = pd.concat([csv_df, new_data], ignore_index=True)
            ID = row['ID']
            GLOBAL_SVOS = []
        # try:
        text = clean_error(row['LOG'])
        tok = nlp(text.strip())
        svos = findSVOs(tok)
        print(text)
        print(svos)
        for n in svos:
            GLOBAL_SVOS += n
        # except Exception as e:
        #     continue
    csv_df.to_csv('svo.csv', index=False)
    return svo_aggregate

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECTS = ["dobj", "dative", "attr", "oprd"]

def getSubsFromConjunctions(subs):
    moreSubs = []
    for sub in subs:
        # rights is a generator
        rights = list(sub.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreSubs.extend([tok for tok in rights if tok.dep_ in SUBJECTS or tok.pos_ == "NOUN"])
            if len(moreSubs) > 0:
                moreSubs.extend(getSubsFromConjunctions(moreSubs))
    return moreSubs

def getObjsFromConjunctions(objs):
    moreObjs = []
    for obj in objs:
        # rights is a generator
        rights = list(obj.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreObjs.extend([tok for tok in rights if tok.dep_ in OBJECTS or tok.pos_ == "NOUN"])
            if len(moreObjs) > 0:
                moreObjs.extend(getObjsFromConjunctions(moreObjs))
    return moreObjs

def getVerbsFromConjunctions(verbs):
    moreVerbs = []
    for verb in verbs:
        rightDeps = {tok.lower_ for tok in verb.rights}
        if "and" in rightDeps:
            moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
            if len(moreVerbs) > 0:
                moreVerbs.extend(getVerbsFromConjunctions(moreVerbs))
    return moreVerbs

def findSubs(tok):
    head = tok.head
    while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
        head = head.head
    if head.pos_ == "VERB":
        subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
        if len(subs) > 0:
            verbNegated = isNegated(head)
            subs.extend(getSubsFromConjunctions(subs))
            return subs, verbNegated
        elif head.head != head:
            return findSubs(head)
    elif head.pos_ == "NOUN":
        return [head], isNegated(tok)
    return [], False

def isNegated(tok):
    negations = {"no", "not", "n't", "never", "none"}
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True
    return False

def findSVs(tokens):
    svs = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        if len(subs) > 0:
            for sub in subs:
                svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
    return svs

def getObjsFromPrepositions(deps):
    objs = []
    for dep in deps:
        if dep.pos_ == "ADP" and dep.dep_ == "prep":
            objs.extend([tok for tok in dep.rights if tok.dep_  in OBJECTS or (tok.pos_ == "PRON" and tok.lower_ == "me")])
    return objs

def getObjsFromAttrs(deps):
    for dep in deps:
        if dep.pos_ == "NOUN" and dep.dep_ == "attr":
            verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
            if len(verbs) > 0:
                for v in verbs:
                    rights = list(v.rights)
                    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
                    objs.extend(getObjsFromPrepositions(rights))
                    if len(objs) > 0:
                        return v, objs
    return None, None

def getObjFromXComp(deps):
    for dep in deps:
        if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
            v = dep
            rights = list(v.rights)
            objs = [tok for tok in rights if tok.dep_ in OBJECTS]
            objs.extend(getObjsFromPrepositions(rights))
            if len(objs) > 0:
                return v, objs
    return None, None

def getAllSubs(v):
    verbNegated = isNegated(v)
    subs = [tok for tok in v.lefts if tok.dep_ in SUBJECTS and tok.pos_ != "DET"]
    if len(subs) > 0:
        subs.extend(getSubsFromConjunctions(subs))
    else:
        foundSubs, verbNegated = findSubs(v)
        subs.extend(foundSubs)
    return subs, verbNegated

def getAllObjs(v):
    rights = list(v.rights)
    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
    objs.extend(getObjsFromPrepositions(rights))
    potentialNewVerb, potentialNewObjs = getObjFromXComp(rights)
    if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
        objs.extend(potentialNewObjs)
        v = potentialNewVerb
    if len(objs) > 0:
        objs.extend(getObjsFromConjunctions(objs))
    return v, objs

def findSVOs(tokens):
    svos = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
    if not verbs:
        for sub in [tok for tok in tokens if tok.pos_ == "NOUN" or tok.pos_ == "PROPN"]:
            svos.append((sub.lower_,))
        return svos
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        if len(subs) > 0:
            v, objs = getAllObjs(v)
            if objs:
                for sub in subs:
                    for obj in objs:
                        objNegated = isNegated(obj)
                        if sub.lower_ and v.lower_ and obj.lower_:
                            svos.append((sub.lower_, "!" + v.lower_ if verbNegated or objNegated else v.lower_, obj.lower_))
            else:
                for sub in subs:
                    if sub.lower_ and v.lower_:
                        svos.append((sub.lower_, v.lower_))
        else:
            for sub in [tok for tok in tokens if tok.pos_ == "NOUN" or tok.pos_ == "PROPN"]:
                if sub.lower_:
                    svos.append((sub.lower_,))

    return svos



def printDeps(toks):
    for tok in toks:
        print(tok.orth_, tok.dep_, tok.pos_, tok.head.orth_, [t.orth_ for t in tok.lefts], [t.orth_ for t in tok.rights])

if __name__ == "__main__":
    main()