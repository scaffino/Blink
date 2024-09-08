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
            "previousblockhash"
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

schema_confirmed_raw_tx = {
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
          "items": {
            "type": "object"
          }
        },
        "vout": {
          "type": "array",
          "items": {
            "type": "object"
          }
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
      "type": [
        "string",
        "null"
      ]
    },
    "id": {
      "type": [
        "string",
        "null"
      ]
    }
  },
  "required": [
    "result",
    "error",
    "id"
  ]
}

schema_general = {
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
