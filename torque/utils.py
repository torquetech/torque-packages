# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""


from torque import exceptions


def merge_dicts(dict1: dict[str, object],
                dict2: dict[str, object],
                allow_overwrites: bool = True) -> dict[str, object]:
    """TODO"""

    new_dict = {} | dict1

    for key in dict2.keys():
        if isinstance(dict2[key], dict):
            if key in new_dict:
                new_dict[key] = merge_dicts(new_dict[key],
                                            dict2[key],
                                            allow_overwrites)

            else:
                new_dict[key] = dict2[key]

        else:
            if not allow_overwrites:
                if key in new_dict:
                    raise exceptions.DuplicateDictEntry(key)

            new_dict[key] = dict2[key]

    return new_dict
