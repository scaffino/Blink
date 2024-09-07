schema_block_header = {
    "type": "object",
    "properties": {
        "result": {
        "type": "object",
        "properties": {
            "hash": {
            "type": "string"
            },
            "confirmations": {
            "type": "integer"
            },
            "height": {
            "type": "integer"
            },
            "version": {
            "type": "integer"
            },
            "versionHex": {
            "type": "string"
            },
            "merkleroot": {
            "type": "string"
            },
            "time": {
            "type": "integer"
            },
            "mediantime": {
            "type": "integer"
            },
            "nonce": {
            "type": "integer"
            },
            "bits": {
            "type": "string"
            },
            "difficulty": {
            "type": "number"
            },
            "chainwork": {
            "type": "string"
            },
            "nTx": {
            "type": "integer"
            },
            "previousblockhash": {
            "type": "string"
            },
            "nextblockhash": {
            "type": "string"
            }
        },
        "required": [
            "hash",
            "confirmations",
            "height",
            "version",
            "versionHex",
            "merkleroot",
            "time",
            "mediantime",
            "nonce",
            "bits",
            "difficulty",
            "chainwork",
            "nTx",
            "previousblockhash",
            "nextblockhash"
        ]
        },
        "error": {
        "type": ["string", "null"]
        },
        "id": {
        "type": ["string", "null"]
        }
    },
    "required": [
        "result",
        "error",
        "id"
    ]
    }

schema_proof = {
  "type": "object",
  "properties": {
    "result": {
      "type": "string"
    },
    "error": {
      "type": ["string", "null"]
    },
    "id": {
      "type": ["string", "null"]
    }
  },
  "required": [
    "result",
    "error",
    "id"
  ]
}

schema_block_hash = {
  "type": "object",
  "properties": {
    "result": {
      "type": "string"
    },
    "error": {
      "type": ["string", "null"]
    },
    "id": {
      "type": ["string", "null"]
    }
  },
  "required": [
    "result",
    "error",
    "id"
  ]
}

schema_raw_tx = {
  "type": "object",
  "properties": {
    "result": {
      "type": "object",
      "properties": {
        "txid": {
          "type": "string"
        },
        "hash": {
          "type": "string"
        },
        "version": {
          "type": "integer"
        },
        "size": {
          "type": "integer"
        },
        "vsize": {
          "type": "integer"
        },
        "weight": {
          "type": "integer"
        },
        "locktime": {
          "type": "integer"
        },
        "vin": {
          "type": "array",
          "items": [
            {
              "type": "object",
              "properties": {
                "txid": {
                  "type": "string"
                },
                "vout": {
                  "type": "integer"
                },
                "scriptSig": {
                  "type": "object",
                  "properties": {
                    "asm": {
                      "type": "string"
                    },
                    "hex": {
                      "type": "string"
                    }
                  },
                  "required": [
                    "asm",
                    "hex"
                  ]
                },
                "txinwitness": {
                  "type": "array",
                  "items": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "string"
                    }
                  ]
                },
                "sequence": {
                  "type": "integer"
                }
              },
              "required": [
                "txid",
                "vout",
                "scriptSig",
                "txinwitness",
                "sequence"
              ]
            }
          ]
        },
        "vout": {
          "type": "array",
          "items": [
            {
              "type": "object",
              "properties": {
                "value": {
                  "type": "number"
                },
                "n": {
                  "type": "integer"
                },
                "scriptPubKey": {
                  "type": "object",
                  "properties": {
                    "asm": {
                      "type": "string"
                    },
                    "desc": {
                      "type": "string"
                    },
                    "hex": {
                      "type": "string"
                    },
                    "address": {
                      "type": "string"
                    },
                    "type": {
                      "type": "string"
                    }
                  },
                  "required": [
                    "asm",
                    "desc",
                    "hex",
                    "address",
                    "type"
                  ]
                }
              },
              "required": [
                "value",
                "n",
                "scriptPubKey"
              ]
            },
            {
              "type": "object",
              "properties": {
                "value": {
                  "type": "number"
                },
                "n": {
                  "type": "integer"
                },
                "scriptPubKey": {
                  "type": "object",
                  "properties": {
                    "asm": {
                      "type": "string"
                    },
                    "desc": {
                      "type": "string"
                    },
                    "hex": {
                      "type": "string"
                    },
                    "address": {
                      "type": "string"
                    },
                    "type": {
                      "type": "string"
                    }
                  },
                  "required": [
                    "asm",
                    "desc",
                    "hex",
                    "address",
                    "type"
                  ]
                }
              },
              "required": [
                "value",
                "n",
                "scriptPubKey"
              ]
            }
          ]
        },
        "hex": {
          "type": "string"
        },
        "blockhash": {
          "type": "string"
        },
        "confirmations": {
          "type": "integer"
        },
        "time": {
          "type": "integer"
        },
        "blocktime": {
          "type": "integer"
        }
      },
      "required": [
        "txid",
        "hash",
        "version",
        "size",
        "vsize",
        "weight",
        "locktime",
        "vin",
        "vout",
        "hex",
        "blockhash",
        "confirmations",
        "time",
        "blocktime"
      ]
    },
    "error": {
      "type": ["string", "null"]
    },
    "id": {
      "type": ["string", "null"]
    }
  },
  "required": [
    "result",
    "error",
    "id"
  ]
}
