#!/usr/bin/env python
# coding=utf-8

#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

from __future__ import absolute_import, division, print_function, unicode_literals
import os,sys

splunkhome = os.environ['SPLUNK_HOME']
sys.path.append(os.path.join(splunkhome, 'etc', 'apps', 'TA-json_redact', 'lib'))
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
from jsonpath_ng import jsonpath, parse
import json


@Configuration()
class JsonRedactCommand(StreamingCommand):
    """ Redacts a JSON document.

    ##Syntax

    .. code-block::
        jsonredact infield=<fieldname> outfield=<fieldname> value=<string> <JSONpath-list>

    ##Description

    All field values matched by one of the `JSONpath` expressions, are replaced through `value`. The JSON document that
    should be redacted has to be stored in the field `infield`. The redacted version is stored in `outfield`. The fields
    content is replaced by the specified `value`.
    JSONpath expressions can be tested using e.g. [JSONPath Online Evaluator](https://jsonpath.com/).

    ##Example

    Redacts the fields firstName, lastName and phoneNumbers within the JSON document document within `_raw` and stores the
    redected version in `out`.

    .. code-block::
        sourcetype=json | jsonredact infield="_raw" outfield="out" value="-redacted-" "$.firstName" "$.lastName" "$.phoneNumbers[:].number"

    """
    infield = Option(
        doc='''
        **Syntax:** **infield=***<fieldname>*
        **Description:** Name of the field that will hold original JSON Document.
        **Default:** _raw''',
        require=False, default="_raw", validate=validators.Fieldname())

    outfield = Option(
        doc='''
        **Syntax:** **outfield=***<fieldname>*
        **Description:** Name of the field that the redacted JSON Document will be saved to.''',
        require=True, validate=validators.Fieldname())

    value = Option(
        doc='''
        **Syntax:** **pattern=***<string>*
        **Description:** Specify a string value to replace redacted values.
        **Default:** -redacted-''',
        require=False, default="-redacted-")

    def stream(self, records):
        jsonpaths = []
        for fieldname in self.fieldnames:
            jsonpaths.append(parse(fieldname))

        for record in records:
            document = json.loads(record[self.infield])
            for jsonpath in jsonpaths:
                document = jsonpath.update(document, self.value)
            record[self.outfield] = json.dumps(document)
            yield record

dispatch(JsonRedactCommand, sys.argv, sys.stdin, sys.stdout, __name__)
