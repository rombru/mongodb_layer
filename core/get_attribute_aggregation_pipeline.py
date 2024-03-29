get_attribute_aggregation_pipeline = [
    {
        '$limit': 10000
    }, {
        '$project': {
            'keys': {
                '$objectToArray': {
                    '$ifNull': [
                        '$$ROOT', {}
                    ]
                }
            }
        }
    }, {
        '$unwind': '$keys'
    }, {
        '$project': {
            'keys': {
                'key': [
                    {
                        '$concat': [
                            'root:', '$keys.k'
                        ]
                    }
                ],
                'nested': {
                    '$switch': {
                        'branches': [
                            {
                                'case': {
                                    '$eq': [
                                        {
                                            '$type': '$keys.v'
                                        }, 'object'
                                    ]
                                },
                                'then': {
                                    '$map': {
                                        'input': {
                                            '$objectToArray': '$keys.v'
                                        },
                                        'as': 'nestedkey',
                                        'in': {
                                            '$concat': [
                                                'object:', '$keys.k', '.', '$$nestedkey.k'
                                            ]
                                        }
                                    }
                                }
                            }, {
                                'case': {
                                    '$eq': [
                                        {
                                            '$type': '$keys.v'
                                        }, 'array'
                                    ]
                                },
                                'then': {
                                    '$map': {
                                        'input': {
                                            '$reduce': {
                                                'input': {
                                                    '$map': {
                                                        'input': {
                                                            '$filter': {
                                                                'input': '$keys.v',
                                                                'as': 'key',
                                                                'cond': {
                                                                    '$eq': [
                                                                        {
                                                                            '$type': '$$key'
                                                                        }, 'object'
                                                                    ]
                                                                }
                                                            }
                                                        },
                                                        'as': 'nestedkey',
                                                        'in': {
                                                            '$objectToArray': '$$nestedkey'
                                                        }
                                                    }
                                                },
                                                'initialValue': [],
                                                'in': {
                                                    '$concatArrays': [
                                                        '$$value', '$$this'
                                                    ]
                                                }
                                            }
                                        },
                                        'as': 'nestedkey',
                                        'in': {
                                            '$concat': [
                                                'array:', '$keys.k', '.', '$$nestedkey.k'
                                            ]
                                        }
                                    }
                                }
                            }
                        ],
                        'default': []
                    }
                }
            }
        }
    }, {
        '$project': {
            'keys': {
                '$setUnion': [
                    '$keys.key', '$keys.nested'
                ]
            }
        }
    }, {
        '$unwind': '$keys'
    }, {
        '$group': {
            '_id': None,
            'keys': {
                '$addToSet': '$keys'
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'keys': 1
        }
    }
]