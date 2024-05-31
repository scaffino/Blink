def init():
    global proof_size 
    proof_size = 0

    global schema_block_header
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