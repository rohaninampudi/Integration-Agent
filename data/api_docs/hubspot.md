# HubSpot API - Create a Contact

## Overview
Creates a new contact in HubSpot CRM. Contacts represent people who interact with your business.

## Endpoint
`POST https://api.hubapi.com/crm/v3/objects/contacts`

## Authentication
Requires a Private App access token or OAuth token with `crm.objects.contacts.write` scope.

Headers:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

## Request Payload

### Required Structure
```json
{
  "properties": {
    "email": "contact@example.com"
  }
}
```

### Standard Contact Properties
| Property | Type | Description |
|----------|------|-------------|
| `email` | string | Contact's email address (commonly used as unique identifier) |
| `firstname` | string | First name |
| `lastname` | string | Last name |
| `phone` | string | Phone number |
| `company` | string | Company name |
| `website` | string | Website URL |
| `jobtitle` | string | Job title |
| `address` | string | Street address |
| `city` | string | City |
| `state` | string | State/Region |
| `zip` | string | Postal/ZIP code |
| `country` | string | Country |
| `lifecyclestage` | string | Lead, MQL, SQL, opportunity, customer, etc. |
| `hs_lead_status` | string | Lead status (New, Open, In Progress, etc.) |

## Payload Examples

### Basic Contact
```json
{
  "properties": {
    "email": "john.doe@company.com",
    "firstname": "John",
    "lastname": "Doe"
  }
}
```

### Full Contact with Company Info
```json
{
  "properties": {
    "email": "jane.smith@acmecorp.com",
    "firstname": "Jane",
    "lastname": "Smith",
    "phone": "+1-555-123-4567",
    "company": "Acme Corporation",
    "jobtitle": "VP of Engineering",
    "website": "https://acmecorp.com",
    "address": "123 Main Street",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102",
    "country": "United States",
    "lifecyclestage": "lead",
    "hs_lead_status": "NEW"
  }
}
```

### Lead with Source Information
```json
{
  "properties": {
    "email": "prospect@example.com",
    "firstname": "Alex",
    "lastname": "Johnson",
    "company": "TechStartup Inc",
    "jobtitle": "CTO",
    "lifecyclestage": "marketingqualifiedlead",
    "hs_lead_status": "OPEN",
    "hs_analytics_source": "ORGANIC_SEARCH",
    "notes_last_updated": "Interested in enterprise plan"
  }
}
```

## Associations (Optional)

Associate contact with companies or deals:

```json
{
  "properties": {
    "email": "contact@example.com",
    "firstname": "Contact",
    "lastname": "Name"
  },
  "associations": [
    {
      "to": {
        "id": "123456789"
      },
      "types": [
        {
          "associationCategory": "HUBSPOT_DEFINED",
          "associationTypeId": 1
        }
      ]
    }
  ]
}
```

## Response

Returns the created contact:

```json
{
  "id": "551",
  "properties": {
    "createdate": "2024-01-08T12:00:00.000Z",
    "email": "john.doe@company.com",
    "firstname": "John",
    "hs_object_id": "551",
    "lastmodifieddate": "2024-01-08T12:00:00.000Z",
    "lastname": "Doe"
  },
  "createdAt": "2024-01-08T12:00:00.000Z",
  "updatedAt": "2024-01-08T12:00:00.000Z",
  "archived": false
}
```

## Liquid Template Example

### Simple Contact
```liquid
{
  "properties": {
    "email": "{{ email }}",
    "firstname": "{{ first_name }}",
    "lastname": "{{ last_name }}"
  }
}
```

### Contact with Company
```liquid
{
  "properties": {
    "email": "{{ lead.email }}",
    "firstname": "{{ lead.first_name }}",
    "lastname": "{{ lead.last_name }}",
    "company": "{{ lead.company }}",
    "jobtitle": "{{ lead.job_title }}",
    "phone": "{{ lead.phone }}",
    "lifecyclestage": "lead"
  }
}
```

### Multiple Contacts from Array
```liquid
[{% for contact in contacts %}
  {
    "properties": {
      "email": "{{ contact.email }}",
      "firstname": "{{ contact.first_name }}",
      "lastname": "{{ contact.last_name }}",
      "company": "{{ contact.company }}"
    }
  }{% unless forloop.last %},{% endunless %}{% endfor %}
]
```

## Common Errors

| Error | Description |
|-------|-------------|
| 400 | Invalid property value or unknown property |
| 401 | Invalid or expired access token |
| 403 | Insufficient permissions |
| 409 | Contact with this email already exists |
| 429 | Rate limit exceeded (100 requests per 10 seconds) |
