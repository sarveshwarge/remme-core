# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

import hashlib
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError

# TODO: think about more logging in helper functions


class BasicHandler(TransactionHandler):
    def __init__(self, name, versions):
        self._family_name = name
        self._family_versions = versions
        self._namespace_prefix = hashlib.sha512(self.FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]

    @property
    def family_name(self):
        return self._family_name

    @property
    def family_versions(self):
        return self._family_versions

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        pass


def make_address(prefix, name):
    return prefix + hashlib.sha512(name.encode('utf-8')).hexdigest()[0:64]


def decode_transaction(transaction, transaction_pb_class):
    transaction_payload = transaction_pb_class()
    try:
        transaction_payload.ParseFromString(transaction.payload)
    except:
        raise InvalidTransaction("Invalid payload serialization")
    return transaction_payload


def get_data(prefix, name, context, data_pb_class):
    data = data_pb_class()
    data_address = make_address(prefix, name)
    raw_data = context.get_state([data_address])
    try:
        data.ParseFromString(raw_data[0])
    except IndexError:
        return None, None
    except:
        raise InternalError("Failed to deserialize data")
    return data


def store_data(prefix, name, context, data_pb_instance):
    serialized = data_pb_instance.SerializeToString()
    data_address = make_address(prefix, name)
    adresses = context.set_state({ data_address: serialized })
    if len(addresses) < 1:
        raise InternalError("State Error")