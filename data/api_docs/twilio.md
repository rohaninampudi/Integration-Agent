# Twilio API - Create a Message (Send SMS)

## Overview
Sends an SMS or MMS message using Twilio's Programmable Messaging API.

## Endpoint
`POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`

## Authentication
Requires Basic Auth with Account SID and Auth Token.

```
Authorization: Basic {base64(AccountSid:AuthToken)}
Content-Type: application/x-www-form-urlencoded
```

Note: Can also use JSON with `Content-Type: application/json`.

## Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `AccountSid` | string | Your Twilio Account SID |

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `To` | string | Recipient phone number (E.164 format: +1234567890) |
| `From` | string | Your Twilio phone number (E.164 format) |
| `Body` | string | The message text (up to 1600 characters for SMS) |

### Alternative to From
| Field | Type | Description |
|-------|------|-------------|
| `MessagingServiceSid` | string | Messaging Service SID (instead of From) |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `MediaUrl` | array | URLs of media to send (MMS) |
| `StatusCallback` | string | URL to receive status updates |
| `MaxPrice` | string | Maximum price in USD (e.g., "0.05") |
| `ValidityPeriod` | integer | Seconds message is valid (max 14400) |
| `SendAt` | string | ISO 8601 datetime for scheduled messages |
| `ScheduleType` | string | "fixed" for scheduled messages |
| `ShortenUrls` | boolean | Shorten URLs in message body |

## Payload Examples

### Simple SMS
```json
{
  "To": "+14155551234",
  "From": "+14155559876",
  "Body": "Hello from Twilio!"
}
```

### SMS with Special Characters
```json
{
  "To": "+14155551234",
  "From": "+14155559876",
  "Body": "Your verification code is: 123456. This code expires in 10 minutes."
}
```

### SMS using Messaging Service
```json
{
  "To": "+14155551234",
  "MessagingServiceSid": "MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "Body": "Your order #12345 has been shipped!"
}
```

### MMS with Media
```json
{
  "To": "+14155551234",
  "From": "+14155559876",
  "Body": "Check out this image!",
  "MediaUrl": ["https://example.com/image.jpg"]
}
```

### SMS with Status Callback
```json
{
  "To": "+14155551234",
  "From": "+14155559876",
  "Body": "Important notification",
  "StatusCallback": "https://yourapp.com/webhook/sms-status"
}
```

### Scheduled SMS
```json
{
  "To": "+14155551234",
  "MessagingServiceSid": "MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "Body": "Reminder: Your appointment is tomorrow at 2 PM.",
  "SendAt": "2024-01-10T14:00:00Z",
  "ScheduleType": "fixed"
}
```

### SMS with All Options
```json
{
  "To": "+14155551234",
  "From": "+14155559876",
  "Body": "Your account balance is $150.00. Reply STOP to unsubscribe.",
  "StatusCallback": "https://yourapp.com/sms-status",
  "MaxPrice": "0.05",
  "ValidityPeriod": 3600
}
```

## Response

Returns the created message object:

```json
{
  "sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "date_created": "Mon, 08 Jan 2024 12:00:00 +0000",
  "date_updated": "Mon, 08 Jan 2024 12:00:00 +0000",
  "date_sent": null,
  "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "to": "+14155551234",
  "from": "+14155559876",
  "messaging_service_sid": null,
  "body": "Hello from Twilio!",
  "status": "queued",
  "num_segments": "1",
  "num_media": "0",
  "direction": "outbound-api",
  "api_version": "2010-04-01",
  "price": null,
  "price_unit": "USD",
  "error_code": null,
  "error_message": null,
  "uri": "/2010-04-01/Accounts/ACxxx/Messages/SMxxx.json"
}
```

## Message Status Values
| Status | Description |
|--------|-------------|
| `queued` | Message is queued to be sent |
| `sending` | Message is being sent |
| `sent` | Message was sent successfully |
| `delivered` | Message was delivered to recipient |
| `undelivered` | Message could not be delivered |
| `failed` | Message failed to send |

## Liquid Template Example

### Simple SMS
```liquid
{
  "To": "{{ to_phone }}",
  "From": "{{ from_phone }}",
  "Body": "{{ message }}"
}
```

### Alert SMS
```liquid
{
  "To": "{{ alert_phone }}",
  "From": "{{ twilio_number }}",
  "Body": "🚨 Alert: {{ alert_message }}\n\nTimestamp: {{ timestamp }}\nSource: {{ source }}"
}
```

### Verification Code SMS
```liquid
{
  "To": "{{ user_phone }}",
  "From": "{{ twilio_number }}",
  "Body": "Your {{ app_name }} verification code is: {{ verification_code }}. This code expires in {{ expiry_minutes }} minutes."
}
```

### Order Notification SMS
```liquid
{
  "To": "{{ customer_phone }}",
  "MessagingServiceSid": "{{ messaging_service_sid }}",
  "Body": "Hi {{ customer_name }}! Your order #{{ order_id }} has been {{ order_status }}. Track it here: {{ tracking_url }}"
}
```

## Phone Number Format

Always use E.164 format:
- US: `+14155551234`
- UK: `+442071234567`
- Include country code with `+` prefix
- No spaces, dashes, or parentheses

## Common Errors

| Error | Description |
|-------|-------------|
| 21211 | Invalid 'To' phone number |
| 21212 | Invalid 'From' phone number |
| 21408 | Permission to send SMS not enabled |
| 21610 | Message body is required |
| 21614 | 'To' number is not a valid mobile number |
| 30003 | Unreachable destination handset |
| 30006 | Landline or unreachable carrier |
