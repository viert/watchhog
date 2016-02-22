UPTO = 0
SKIP = 1
SKIPTO = 2
SKIPANY = 3

class Parser(object):
    def __init__(self):
        self._rules = []
        self._result = {}

    def upTo(self, sym, fieldName):
        self._rules.append({'action': UPTO, 'sym': sym, 'fieldName': fieldName})

    def skip(self, sym):
        self._rules.append({'action': SKIP, 'sym': sym})

    def skipTo(self, sym):
        self._rules.append({'action': SKIPTO, 'sym': sym})

    def skipAny(self):
        self._rules.append({'action': SKIPANY})

    def getResults(self):
        return self._result

    def parseLine(self, line):
        self._result = {}
        rulesIterator = iter(self._rules)
        linePointer = 0
        while True:
            try:
                currentRule = rulesIterator.next()
            except StopIteration:
                break

            action = currentRule['action']
            if action == SKIP:
                if linePointer >= len(line) or line[linePointer] != currentRule['sym']:
                    return False
                else:
                    linePointer += 1
            elif action == SKIPANY:
                if linePointer >= len(line):
                    return False
                else:
                    linePointer += 1
            elif action == SKIPTO:
                while True:
                    if linePointer >= len(line):
                        return False
                    if line[linePointer] != currentRule['sym']:
                        linePointer += 1
                    else:
                        break
            elif action == UPTO:
                firstSym = linePointer
                while True:
                    if linePointer >= len(line):
                        return False
                    if line[linePointer] != currentRule['sym']:
                        linePointer += 1
                    else:
                        self._result[currentRule['fieldName']] = line[firstSym:linePointer]
                        break
        return True
