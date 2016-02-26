#include <vector>
#include <string>
#include <map>
#include <boost/python.hpp>

using namespace std;
using namespace boost::python;

enum ActionType { UPTO, SKIPTO, SKIP, SKIPANY };

struct Rule {
    ActionType action;
    char ch1;
    char ch2;
    string fieldName;
};

struct Parser {

    void upTo(char sym, string fieldName) {
        Rule rule;
        rule.action = UPTO;
        rule.ch1 = sym;
        rule.fieldName = fieldName;
        rules.push_back(rule);
    }

    void skipTo(char sym) {
        Rule rule;
        rule.action = SKIPTO;
        rule.ch1 = sym;
        rules.push_back(rule);
    }

    void skip(char sym) {
        Rule rule;
        rule.action = SKIP;
        rule.ch1 = sym;
        rules.push_back(rule);
    }

    void skipAny() {
        Rule rule;
        rule.action = SKIPANY;
        rules.push_back(rule);
    }

    bool parseLine(string line) {
        result.empty();
        vector<Rule>::iterator ruleIterator = rules.begin();
        int linePointer = 0;
        while (ruleIterator != rules.end()) {
            Rule currentRule = *ruleIterator;
            switch (currentRule.action) {
                case SKIP:
                    if (linePointer >= line.length()) {
                        return false;
                    }
                    if (line[linePointer] != currentRule.ch1) {
                        return false;
                    } else {
                        ++linePointer;
                    }
                    break;

                case SKIPANY:
                    if (linePointer >= line.length()) {
                        return false;
                    }
                    ++linePointer;
                    break;

                case SKIPTO:

                    while (true) {
                        if (linePointer >= line.length()) {
                            return false;
                        }
                        if (line[linePointer] != currentRule.ch1) {
                            ++linePointer;
                        } else {
                            break;
                        }
                    }
                    break;

                case UPTO:
                    int firstSym = linePointer;
                    while (true) {
                        if (linePointer >= line.length()) {
                            return false;
                        }
                        if (line[linePointer] != currentRule.ch1) {
                            ++linePointer;
                        } else {
                            result.insert(
                                pair<string, string>(currentRule.fieldName, line.substr(firstSym, linePointer-firstSym))
                            );
                            break;
                        }

                    }
                    break;
            }
            ruleIterator++;
        }
        return true;
    }

    dict getResults() {
        dict d = dict();
        for (map<string, string>::iterator it = result.begin(); it != result.end(); ++it) {
            d[it->first] = it->second;
        }
        return d;
    }

    vector<Rule> rules;
    map<string, string> result;
};

BOOST_PYTHON_MODULE(parser)
{
  class_<Parser>("Parser")
    .def("skip", &Parser::skip)
    .def("skipTo", &Parser::skipTo)
    .def("skipAny", &Parser::skipAny)
    .def("upTo", &Parser::upTo)
    .def("parseLine", &Parser::parseLine)
    .def("getResults", &Parser::getResults)
  ;
}
