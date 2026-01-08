# Google Sheets API v4

## Overview
The Google Sheets API allows you to create, read, and modify Google Sheets spreadsheets.

---

## spreadsheets.create - Create a New Spreadsheet

### Endpoint
`POST https://sheets.googleapis.com/v4/spreadsheets`

### Authentication
Requires OAuth 2.0 with `https://www.googleapis.com/auth/spreadsheets` scope.

### Request Payload

#### Main Object
| Field | Type | Description |
|-------|------|-------------|
| `properties` | object | Spreadsheet properties |
| `sheets` | array | Array of sheet objects |

#### Properties Object
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | The title of the spreadsheet |
| `locale` | string | Locale of the spreadsheet (e.g., "en_US") |
| `timeZone` | string | Timezone (e.g., "America/New_York") |

#### Sheet Object
| Field | Type | Description |
|-------|------|-------------|
| `properties` | object | Sheet properties (title, index, etc.) |
| `data` | array | Array of GridData objects with cell data |

#### GridData Object
| Field | Type | Description |
|-------|------|-------------|
| `startRow` | integer | Starting row (0-indexed) |
| `startColumn` | integer | Starting column (0-indexed) |
| `rowData` | array | Array of RowData objects |

#### RowData Object
| Field | Type | Description |
|-------|------|-------------|
| `values` | array | Array of CellData objects |

#### CellData Object
| Field | Type | Description |
|-------|------|-------------|
| `userEnteredValue` | object | The value to enter |

#### ExtendedValue Object (for userEnteredValue)
| Field | Type | Description |
|-------|------|-------------|
| `stringValue` | string | A string value |
| `numberValue` | number | A numeric value |
| `boolValue` | boolean | A boolean value |
| `formulaValue` | string | A formula (e.g., "=SUM(A1:A10)") |

### Payload Examples

#### Simple Spreadsheet with Title
```json
{
  "properties": {
    "title": "My New Spreadsheet"
  }
}
```

#### Spreadsheet with Data
```json
{
  "properties": {
    "title": "Product Data"
  },
  "sheets": [
    {
      "properties": {
        "title": "Products"
      },
      "data": [
        {
          "rowData": [
            {
              "values": [
                { "userEnteredValue": { "stringValue": "Name" } },
                { "userEnteredValue": { "stringValue": "Price" } },
                { "userEnteredValue": { "stringValue": "URL" } }
              ]
            },
            {
              "values": [
                { "userEnteredValue": { "stringValue": "Wireless Headphones" } },
                { "userEnteredValue": { "numberValue": 79.99 } },
                { "userEnteredValue": { "stringValue": "https://example.com/p/1" } }
              ]
            },
            {
              "values": [
                { "userEnteredValue": { "stringValue": "USB-C Hub" } },
                { "userEnteredValue": { "numberValue": 45.00 } },
                { "userEnteredValue": { "stringValue": "https://example.com/p/2" } }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Response
```json
{
  "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "properties": {
    "title": "Product Data"
  },
  "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
}
```

### Liquid Template Example
For a workflow with `scraper_results` array:
```liquid
{
  "properties": {
    "title": "Product Data"
  },
  "sheets": [
    {
      "properties": { "title": "Products" },
      "data": [
        {
          "rowData": [
            {
              "values": [
                { "userEnteredValue": { "stringValue": "Name" } },
                { "userEnteredValue": { "stringValue": "Price" } },
                { "userEnteredValue": { "stringValue": "URL" } }
              ]
            }{% for product in scraper_results %},
            {
              "values": [
                { "userEnteredValue": { "stringValue": "{{ product.name }}" } },
                { "userEnteredValue": { "numberValue": {{ product.price }} } },
                { "userEnteredValue": { "stringValue": "{{ product.url }}" } }
              ]
            }{% endfor %}
          ]
        }
      ]
    }
  ]
}
```

---

## spreadsheets.values.append - Append Rows to Existing Spreadsheet

### Endpoint
`POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/{range}:append`

### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `valueInputOption` | string | How to interpret input (`RAW` or `USER_ENTERED`) |
| `insertDataOption` | string | How to insert (`OVERWRITE` or `INSERT_ROWS`) |

### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `spreadsheetId` | string | The ID of the spreadsheet |
| `range` | string | A1 notation range (e.g., "Sheet1!A:C") |

### Request Payload

| Field | Type | Description |
|-------|------|-------------|
| `range` | string | The range to append to |
| `majorDimension` | string | "ROWS" or "COLUMNS" (default: "ROWS") |
| `values` | array | 2D array of values to append |

### Payload Examples

#### Append Single Row
```json
{
  "range": "Sheet1!A:C",
  "majorDimension": "ROWS",
  "values": [
    ["Wireless Headphones", 79.99, "https://example.com/p/1"]
  ]
}
```

#### Append Multiple Rows
```json
{
  "range": "Sheet1!A:C",
  "majorDimension": "ROWS",
  "values": [
    ["Wireless Headphones", 79.99, "https://example.com/p/1"],
    ["USB-C Hub", 45.00, "https://example.com/p/2"],
    ["Mechanical Keyboard", 149.99, "https://example.com/p/3"]
  ]
}
```

#### Simplified Append Request
For the append action, the minimal payload is:
```json
{
  "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "range": "Sheet1!A:C",
  "valueInputOption": "USER_ENTERED",
  "values": [
    ["Product Name", 99.99, "https://example.com"]
  ]
}
```

### Response
```json
{
  "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "tableRange": "Sheet1!A1:C3",
  "updates": {
    "spreadsheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    "updatedRange": "Sheet1!A4:C6",
    "updatedRows": 3,
    "updatedColumns": 3,
    "updatedCells": 9
  }
}
```

### Liquid Template Example
For a workflow with `scraper_results` array and `spreadsheet_id`:
```liquid
{
  "spreadsheetId": "{{ spreadsheet_id }}",
  "range": "Sheet1!A:C",
  "valueInputOption": "USER_ENTERED",
  "values": [{% for product in scraper_results %}
    ["{{ product.name }}", {{ product.price }}, "{{ product.url }}"]{% unless forloop.last %},{% endunless %}{% endfor %}
  ]
}
```

---

## Common Errors
| Status | Error | Description |
|--------|-------|-------------|
| 400 | INVALID_ARGUMENT | Invalid request payload |
| 401 | UNAUTHENTICATED | Missing or invalid authentication |
| 403 | PERMISSION_DENIED | Insufficient permissions |
| 404 | NOT_FOUND | Spreadsheet not found |
| 429 | RESOURCE_EXHAUSTED | Rate limit exceeded |
