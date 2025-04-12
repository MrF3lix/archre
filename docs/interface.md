# Interface


## Report

This is how a report looks like:


```json
{
    "client": {
        "name": "",
        "loss_history": [],
        "regions": [
            {
                "state": null,
                "country": "NL"
            }
        ],
        "brokerage": 0.1,
        "brokerName": "Broker X",
        "cedantName": "Company X (Netherlands) N.V.",
        "signatures": [],
        "contractType": "Occurrence",
        "currencyCode": "EUR",
        "inceptionDate": "2025-01-01",
        "expirationDate": "2025-12-31",
        "uniqueMarketReference": null,
        "expiringUniqueMarketReference": null
    },
    "global": {
    
    },
    "wording": {},
    "term": {
        "tax": null,
        "layers": [
            {
                "name": "Layer 1",
                "flatPremium": null,
                "layerNumber": "L1",
                "aggregateLimit": 30000000,
                "depositPremium": 4703900,
                "minimumPremium": null,
                "occurrenceLimit": null,
                "aggregateAttachment": 90000000,
                "occurrenceAttachment": 90000000
            }
        ],
        "perils": [
            "Fire and allied perils"
        ]
    },
    "recommendations": [
        {
            "title": "",
            "description": "",
            "reasoning": ""
        }
    ]
}
```

