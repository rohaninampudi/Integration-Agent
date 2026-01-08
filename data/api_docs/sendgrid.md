# SendGrid v3 API - Mail Send

## Overview
Sends an email using SendGrid's Web API. Supports text, HTML, templates, attachments, and advanced tracking options.

## Endpoint
`POST https://api.sendgrid.com/v3/mail/send`

## Authentication
Requires an API Key in the Authorization header.

Headers:
```
Authorization: Bearer SG.xxxx...
Content-Type: application/json
```

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `personalizations` | array | Array of recipient and personalization data |
| `from` | object | Sender email and name |
| `subject` | string | Email subject line |
| `content` | array | Email content (text and/or HTML) |

### Personalizations Object
| Field | Type | Description |
|-------|------|-------------|
| `to` | array | Array of recipient objects `{email, name}` |
| `cc` | array | CC recipients |
| `bcc` | array | BCC recipients |
| `subject` | string | Override subject for this personalization |
| `dynamic_template_data` | object | Data for dynamic templates |
| `substitutions` | object | Substitution tags |

### Content Object
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | MIME type: "text/plain" or "text/html" |
| `value` | string | The actual content |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `reply_to` | object | Reply-to email and name |
| `attachments` | array | File attachments |
| `template_id` | string | SendGrid template ID |
| `categories` | array | Categories for tracking |
| `send_at` | integer | Unix timestamp for scheduled send |
| `tracking_settings` | object | Click/open tracking settings |

## Payload Examples

### Simple Text Email
```json
{
  "personalizations": [
    {
      "to": [
        {
          "email": "recipient@example.com",
          "name": "John Doe"
        }
      ]
    }
  ],
  "from": {
    "email": "sender@company.com",
    "name": "Company Name"
  },
  "subject": "Hello from SendGrid",
  "content": [
    {
      "type": "text/plain",
      "value": "This is a test email sent via SendGrid."
    }
  ]
}
```

### HTML Email
```json
{
  "personalizations": [
    {
      "to": [
        {
          "email": "recipient@example.com"
        }
      ]
    }
  ],
  "from": {
    "email": "notifications@company.com",
    "name": "Notifications"
  },
  "subject": "Your Weekly Report",
  "content": [
    {
      "type": "text/plain",
      "value": "View this email in HTML for the full experience."
    },
    {
      "type": "text/html",
      "value": "<html><body><h1>Weekly Report</h1><p>Here's your summary...</p></body></html>"
    }
  ]
}
```

### Email with Multiple Recipients
```json
{
  "personalizations": [
    {
      "to": [
        { "email": "user1@example.com", "name": "User One" },
        { "email": "user2@example.com", "name": "User Two" }
      ],
      "cc": [
        { "email": "manager@example.com" }
      ]
    }
  ],
  "from": {
    "email": "team@company.com",
    "name": "Team Updates"
  },
  "subject": "Team Announcement",
  "content": [
    {
      "type": "text/plain",
      "value": "Important team update..."
    }
  ]
}
```

### Email with Dynamic Template
```json
{
  "personalizations": [
    {
      "to": [
        { "email": "customer@example.com" }
      ],
      "dynamic_template_data": {
        "first_name": "John",
        "order_number": "12345",
        "order_total": "$99.99",
        "items": [
          { "name": "Product A", "price": "$49.99" },
          { "name": "Product B", "price": "$50.00" }
        ]
      }
    }
  ],
  "from": {
    "email": "orders@store.com",
    "name": "Store Name"
  },
  "template_id": "d-abc123def456"
}
```

### Email with Categories and Tracking
```json
{
  "personalizations": [
    {
      "to": [{ "email": "user@example.com" }]
    }
  ],
  "from": {
    "email": "marketing@company.com",
    "name": "Marketing"
  },
  "subject": "Special Offer Inside!",
  "content": [
    {
      "type": "text/html",
      "value": "<html><body><p>Check out our <a href='https://example.com'>special offer</a>!</p></body></html>"
    }
  ],
  "categories": ["marketing", "promo", "january"],
  "tracking_settings": {
    "click_tracking": {
      "enable": true
    },
    "open_tracking": {
      "enable": true
    }
  }
}
```

## Response

Returns `202 Accepted` on success (no body), or error details on failure.

Success: HTTP 202 with empty body

Error response:
```json
{
  "errors": [
    {
      "message": "The from address does not match a verified Sender Identity.",
      "field": "from.email",
      "help": "http://sendgrid.com/docs/..."
    }
  ]
}
```

## Liquid Template Example

### Simple Email
```liquid
{
  "personalizations": [
    {
      "to": [
        {
          "email": "{{ to_email }}",
          "name": "{{ to_name }}"
        }
      ]
    }
  ],
  "from": {
    "email": "{{ from_email }}",
    "name": "{{ from_name }}"
  },
  "subject": "{{ subject }}",
  "content": [
    {
      "type": "text/plain",
      "value": "{{ body }}"
    }
  ]
}
```

### Notification Email
```liquid
{
  "personalizations": [
    {
      "to": [
        { "email": "{{ recipient_email }}" }
      ]
    }
  ],
  "from": {
    "email": "notifications@{{ company_domain }}",
    "name": "{{ company_name }} Notifications"
  },
  "subject": "{{ notification_title }}",
  "content": [
    {
      "type": "text/html",
      "value": "<html><body><h2>{{ notification_title }}</h2><p>{{ notification_body }}</p></body></html>"
    }
  ],
  "categories": ["notification", "automated"]
}
```

## Common Errors

| Error | Description |
|-------|-------------|
| 400 | Malformed JSON or missing required fields |
| 401 | Invalid API key |
| 403 | From address not verified |
| 413 | Payload too large (max 30MB) |
| 429 | Rate limit exceeded |
