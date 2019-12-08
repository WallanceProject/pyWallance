
/******* pyWALLANCE GRAFANA INTERFACE *******/

dashboard =
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "description": "pyWallance in real-time",
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 2,
  "iteration": 1560633277299,
  "links": [],
  "panels": [
    {
      "columns": [],
      "datasource": "MySQLpyWallance",
      "description": "Pending Consensus Responses",
      "fontSize": "100%",
      "gridPos": {
        "h": 7,
        "w": 19,
        "x": 0,
        "y": 0
      },
      "id": 19,
      "interval": "2s",
      "links": [],
      "minSpan": 1,
      "pageSize": null,
      "repeatDirection": "v",
      "scroll": true,
      "showHeader": true,
      "sort": {
        "col": 0,
        "desc": true
      },
      "styles": [
        {
          "alias": "Time",
          "dateFormat": "YYYY-MM-DD HH:mm:ss",
          "pattern": "Time",
          "type": "date"
        },
        {
          "alias": "",
          "colorMode": null,
          "colors": [
            "rgba(245, 54, 54, 0.9)",
            "rgba(237, 129, 40, 0.89)",
            "rgba(50, 172, 45, 0.97)"
          ],
          "decimals": 2,
          "pattern": "/.*/",
          "thresholds": [],
          "type": "number",
          "unit": "short"
        }
      ],
      "targets": [
        {
          "format": "table",
          "group": [],
          "hide": false,
          "metricColumn": "none",
          "rawQuery": true,
          "rawSql": "SELECT SUBSCRIBER AS Voter, PUBLISHER AS Requester, SMARTCONTRACT AS Service, PRICE AS Price, DATE_FORMAT(FROM_UNIXTIME(TIME), '%Y-%m-%d %H:%i:%s') AS Time, PREVSTATE AS State, DCOIN AS RemainingDCoin, OUTDATE AS Outdate FROM CONSENSUS_TRANSACTIONS",
          "refId": "A",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "column"
              }
            ]
          ],
          "timeColumn": "time",
          "where": [
            {
              "name": "$__timeFilter",
              "params": [],
              "type": "macro"
            }
          ]
        }
      ],
      "title": "Consensus Transactions",
      "transform": "table",
      "type": "table"
    },
    {
      "columns": [],
      "datasource": "MySQLpyWallance",
      "description": "List of Available Smart Contracts",
      "fontSize": "100%",
      "gridPos": {
        "h": 7,
        "w": 5,
        "x": 19,
        "y": 0
      },
      "id": 18,
      "interval": "2s",
      "links": [],
      "minSpan": 1,
      "pageSize": null,
      "repeatDirection": "v",
      "scroll": true,
      "showHeader": true,
      "sort": {
        "col": 0,
        "desc": true
      },
      "styles": [
        {
          "alias": "Time",
          "dateFormat": "YYYY-MM-DD HH:mm:ss",
          "pattern": "Time",
          "type": "date"
        },
        {
          "alias": "",
          "colorMode": null,
          "colors": [
            "rgba(245, 54, 54, 0.9)",
            "rgba(237, 129, 40, 0.89)",
            "rgba(50, 172, 45, 0.97)"
          ],
          "decimals": 2,
          "pattern": "/.*/",
          "thresholds": [],
          "type": "number",
          "unit": "short"
        }
      ],
      "targets": [
        {
          "format": "table",
          "group": [],
          "hide": false,
          "metricColumn": "none",
          "rawQuery": true,
          "rawSql": "SELECT NAME AS Name, PRICE AS Price FROM SMARTCONTRACT",
          "refId": "A",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "column"
              }
            ]
          ],
          "timeColumn": "time",
          "where": [
            {
              "name": "$__timeFilter",
              "params": [],
              "type": "macro"
            }
          ]
        }
      ],
      "title": "Smart Contracts",
      "transform": "table",
      "type": "table"
    },
    {
      "content": "<html>\n<head>\n<style>\n.Buy_button {\n  position: absolute;\n  border: 0;\n  border-radius: 4px;\n  color: #fff;\n  background-color: rgba(0, 150, 0, 1);\n  box-shadow: inset 2px 2px 3px rgba(255, 255, 255, .6), inset -2px -2px 3px rgba(0, 0, 0, .6);\n  font-size: 1rem;\n  text-align: center;\n  text-shadow: 1px 1px 1px #000;\n  line-height: 50px;\n  margin-left: auto;\n  margin-right: auto;\n  width: 350px;\n  top: 50%;\n  left: 50%;\n  transform: translate(-50%, -50%);\n}\n\n.Buy_button:hover {\n    background-color: rgba(0, 200, 0, 1);\n}\n\n.Buy_button:active {\n  box-shadow: inset -2px -2px 3px rgba(255, 255, 255, .6), inset 2px 2px 3px rgba(0, 0, 0, .6);\n}\n\n</style></head><body>\n<button class=\"Buy_button\"; onclick=\"window.location.href='pywallancesendrequest:[[Node]]_[[SMC]]_[[SMC_Price]]'\">Buy Service</button>\n</body></html>",
      "description": "Execute Operations for $Node",
      "gridPos": {
        "h": 5,
        "w": 8,
        "x": 0,
        "y": 7
      },
      "id": 21,
      "links": [],
      "mode": "html",
      "repeat": "Node",
      "repeatDirection": "v",
      "scopedVars": {
        "Node": {
          "isNone": true,
          "selected": true,
          "text": "None",
          "value": ""
        }
      },
      "title": "$Node  - Operations",
      "transparent": false,
      "type": "text"
    },
    {
      "columns": [],
      "datasource": "MySQLpyWallance",
      "description": "Pending Request Transactions of $Node",
      "fontSize": "100%",
      "gridPos": {
        "h": 5,
        "w": 11,
        "x": 8,
        "y": 7
      },
      "id": 17,
      "interval": "2s",
      "links": [],
      "minSpan": 1,
      "pageSize": null,
      "repeat": "Node",
      "repeatDirection": "v",
      "scopedVars": {
        "Node": {
          "isNone": true,
          "selected": true,
          "text": "None",
          "value": ""
        }
      },
      "scroll": true,
      "showHeader": true,
      "sort": {
        "col": 0,
        "desc": true
      },
      "styles": [
        {
          "alias": "Time",
          "dateFormat": "YYYY-MM-DD HH:mm:ss",
          "pattern": "Time",
          "type": "date"
        },
        {
          "alias": "",
          "colorMode": null,
          "colors": [
            "rgba(245, 54, 54, 0.9)",
            "rgba(237, 129, 40, 0.89)",
            "rgba(50, 172, 45, 0.97)"
          ],
          "decimals": 2,
          "pattern": "/.*/",
          "thresholds": [],
          "type": "number",
          "unit": "short"
        }
      ],
      "targets": [
        {
          "format": "table",
          "group": [],
          "hide": false,
          "metricColumn": "none",
          "rawQuery": true,
          "rawSql": "SELECT PUBLISHER AS Requester, SMARTCONTRACT AS Service, PRICE AS Price, DATE_FORMAT(FROM_UNIXTIME(TIME), '%Y-%m-%d %H:%i:%s') AS Time, PREVSTATE AS State, OUTDATE AS Outdate FROM REQUEST_TRANSACTIONS WHERE PUBLISHER = $Node",
          "refId": "A",
          "select": [
            [
              {
                "params": [
                  "value"
                ],
                "type": "column"
              }
            ]
          ],
          "timeColumn": "time",
          "where": [
            {
              "name": "$__timeFilter",
              "params": [],
              "type": "macro"
            }
          ]
        }
      ],
      "title": "$Node - Request Transactions",
      "transform": "table",
      "type": "table"
    },
    {
      "cacheTimeout": null,
      "colorBackground": false,
      "colorPostfix": false,
      "colorPrefix": false,
      "colorValue": true,
      "colors": [
        "rgb(28, 197, 80)",
        "rgb(28, 197, 80)",
        "rgb(28, 197, 80)"
      ],
      "datasource": "MySQLpyWallance",
      "decimals": null,
      "description": "DCoins of $Node",
      "format": "none",
      "gauge": {
        "maxValue": 3000,
        "minValue": null,
        "show": false,
        "thresholdLabels": false,
        "thresholdMarkers": true
      },
      "gridPos": {
        "h": 5,
        "w": 5,
        "x": 19,
        "y": 7
      },
      "hideTimeOverride": false,
      "id": 7,
      "interval": "2s",
      "links": [],
      "mappingType": 1,
      "mappingTypes": [
        {
          "name": "value to text",
          "value": 1
        },
        {
          "name": "range to text",
          "value": 2
        }
      ],
      "maxDataPoints": 100,
      "nullPointMode": "connected",
      "nullText": null,
      "postfix": " DC",
      "postfixFontSize": "80%",
      "prefix": "",
      "prefixFontSize": "50%",
      "rangeMaps": [
        {
          "from": "null",
          "text": "N/A",
          "to": "null"
        }
      ],
      "repeat": "Node",
      "repeatDirection": "v",
      "scopedVars": {
        "Node": {
          "isNone": true,
          "selected": true,
          "text": "None",
          "value": ""
        }
      },
      "sparkline": {
        "fillColor": "#bf1b00",
        "full": true,
        "lineColor": "rgb(0, 37, 191)",
        "show": true
      },
      "tableColumn": "COUNTER/5",
      "targets": [
        {
          "format": "table",
          "group": [],
          "hide": false,
          "metricColumn": "none",
          "rawQuery": true,
          "rawSql": "SELECT COUNTER/$DCoin_Rate FROM WALLET WHERE PUBLISHER = $Node",
          "refId": "A",
          "select": [
            [
              {
                "params": [
                  "number"
                ],
                "type": "column"
              }
            ]
          ],
          "table": "WALLET",
          "timeColumn": "number",
          "timeColumnType": "int",
          "where": [
            {
              "name": "",
              "params": [
                "value",
                "=",
                "value"
              ],
              "type": "expression"
            }
          ]
        }
      ],
      "thresholds": "inf",
      "title": "$Node - Wallet",
      "type": "singlestat",
      "valueFontSize": "110%",
      "valueMaps": [
        {
          "op": "=",
          "text": "0.00",
          "value": "null"
        }
      ],
      "valueName": "current"
    }
  ],
  "refresh": "2s",
  "schemaVersion": 16,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": [
      {
        "allValue": null,
        "current": {
          "text": "5",
          "value": "5"
        },
        "datasource": "MySQLpyWallance",
        "definition": "SELECT 5 AS DCOIN_RATE",
        "hide": 2,
        "includeAll": false,
        "label": "DCoin_Rate",
        "multi": false,
        "name": "DCoin_Rate",
        "options": [],
        "query": "SELECT 5 AS DCOIN_RATE",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      },
      {
        "allValue": null,
        "current": {
          "text": "None",
          "value": [
            ""
          ]
        },
        "datasource": "MySQLpyWallance",
        "definition": "SELECT DISTINCT PUBLISHER FROM WALLET",
        "hide": 0,
        "includeAll": false,
        "label": "Node",
        "multi": true,
        "name": "Node",
        "options": [],
        "query": "SELECT DISTINCT PUBLISHER FROM WALLET",
        "refresh": 2,
        "regex": "",
        "skipUrlSync": false,
        "sort": 3,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      },
      {
        "allValue": null,
        "current": {
          "text": "",
          "value": ""
        },
        "datasource": "MySQLpyWallance",
        "definition": "SELECT DISTINCT NAME FROM SMARTCONTRACT",
        "hide": 0,
        "includeAll": false,
        "label": "SMC",
        "multi": false,
        "name": "SMC",
        "options": [],
        "query": "SELECT DISTINCT NAME FROM SMARTCONTRACT",
        "refresh": 2,
        "regex": "",
        "skipUrlSync": false,
        "sort": 3,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      },
      {
        "allValue": null,
        "current": {
          "text": "2",
          "value": "2"
        },
        "datasource": "MySQLpyWallance",
        "definition": "SELECT PRICE FROM SMARTCONTRACT WHERE NAME = '$SMC'",
        "hide": 2,
        "includeAll": false,
        "label": "SMC_Price",
        "multi": false,
        "name": "SMC_Price",
        "options": [],
        "query": "SELECT PRICE FROM SMARTCONTRACT WHERE NAME = '$SMC'",
        "refresh": 2,
        "regex": "",
        "skipUrlSync": false,
        "sort": 3,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      }
    ]
  },
  "time": {
    "from": "2019-05-29T02:37:06.022Z",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "2s",
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ],
    "time_options": [
      "5m",
      "15m",
      "1h",
      "6h",
      "12h",
      "24h",
      "2d",
      "7d",
      "30d"
    ]
  },
  "timezone": "",
  "title": "pyWallance Dashboard",
  "uid": "LzSBlxlmk",
  "version": 4
};
return dashboard;