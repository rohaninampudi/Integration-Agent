# Stripe API - Create a Customer

## Overview
Creates a new customer object in Stripe. Customers allow you to perform recurring charges, save payment methods, and track payments.

## Endpoint
`POST https://api.stripe.com/v1/customers`

## Authentication
Requires a Secret API Key in the Authorization header.

Headers:
```
Authorization: Bearer sk_test_...
Content-Type: application/x-www-form-urlencoded
```

Note: Stripe accepts `application/x-www-form-urlencoded` by default, but also accepts JSON with `Content-Type: application/json`.

## Request Payload

### Common Fields
| Field | Type | Description |
|-------|------|-------------|
| `email` | string | Customer's email address |
| `name` | string | Customer's full name |
| `phone` | string | Customer's phone number |
| `description` | string | Arbitrary description |
| `metadata` | object | Key-value pairs for custom data |
| `address` | object | Customer's address |
| `shipping` | object | Shipping information |
| `payment_method` | string | ID of payment method to attach |
| `invoice_settings` | object | Default invoice settings |
| `preferred_locales` | array | Preferred languages for invoices |
| `tax_exempt` | string | Tax exemption status: "none", "exempt", "reverse" |

### Address Object
```json
{
  "line1": "123 Main St",
  "line2": "Apt 4",
  "city": "San Francisco",
  "state": "CA",
  "postal_code": "94102",
  "country": "US"
}
```

### Shipping Object
```json
{
  "name": "John Doe",
  "phone": "+1-555-123-4567",
  "address": {
    "line1": "456 Ship St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94102",
    "country": "US"
  }
}
```

## Payload Examples

### Basic Customer
```json
{
  "email": "customer@example.com",
  "name": "John Doe"
}
```

### Customer with Phone and Description
```json
{
  "email": "jane.smith@company.com",
  "name": "Jane Smith",
  "phone": "+1-555-987-6543",
  "description": "Enterprise customer - Annual plan"
}
```

### Customer with Full Address
```json
{
  "email": "customer@example.com",
  "name": "John Doe",
  "phone": "+1-555-123-4567",
  "address": {
    "line1": "123 Main Street",
    "line2": "Suite 100",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94102",
    "country": "US"
  }
}
```

### Customer with Metadata
```json
{
  "email": "enterprise@bigcorp.com",
  "name": "Big Corp Inc.",
  "description": "Enterprise tier customer",
  "metadata": {
    "account_id": "acc_12345",
    "plan": "enterprise",
    "signup_source": "sales_demo",
    "account_manager": "jane@ourcompany.com"
  }
}
```

### Customer with Shipping
```json
{
  "email": "buyer@example.com",
  "name": "Alex Johnson",
  "shipping": {
    "name": "Alex Johnson",
    "phone": "+1-555-000-1234",
    "address": {
      "line1": "789 Shipping Lane",
      "city": "Los Angeles",
      "state": "CA",
      "postal_code": "90001",
      "country": "US"
    }
  }
}
```

### Complete Customer Object
```json
{
  "email": "complete@example.com",
  "name": "Complete Customer",
  "phone": "+1-555-999-8888",
  "description": "Full customer profile",
  "address": {
    "line1": "100 Billing Ave",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "US"
  },
  "shipping": {
    "name": "Complete Customer",
    "address": {
      "line1": "200 Shipping Blvd",
      "city": "New York",
      "state": "NY",
      "postal_code": "10002",
      "country": "US"
    }
  },
  "metadata": {
    "user_id": "user_abc123",
    "tier": "premium"
  },
  "preferred_locales": ["en-US"]
}
```

## Response

Returns the created customer object:

```json
{
  "id": "cus_abc123",
  "object": "customer",
  "email": "customer@example.com",
  "name": "John Doe",
  "phone": null,
  "description": null,
  "address": null,
  "created": 1704700000,
  "currency": null,
  "default_source": null,
  "delinquent": false,
  "invoice_prefix": "ABC123",
  "livemode": false,
  "metadata": {},
  "shipping": null,
  "tax_exempt": "none"
}
```

## Liquid Template Example

### Simple Customer
```liquid
{
  "email": "{{ email }}",
  "name": "{{ name }}"
}
```

### Customer with Metadata
```liquid
{
  "email": "{{ customer.email }}",
  "name": "{{ customer.name }}",
  "phone": "{{ customer.phone }}",
  "description": "{{ customer.description }}",
  "metadata": {
    "user_id": "{{ customer.id }}",
    "source": "{{ signup_source }}"
  }
}
```

### Customer with Address
```liquid
{
  "email": "{{ email }}",
  "name": "{{ name }}",
  "address": {
    "line1": "{{ address.line1 }}",
    "city": "{{ address.city }}",
    "state": "{{ address.state }}",
    "postal_code": "{{ address.postal_code }}",
    "country": "{{ address.country | default: 'US' }}"
  }
}
```

## Common Errors

| Error | Description |
|-------|-------------|
| 400 | Invalid parameter (e.g., malformed email) |
| 401 | Invalid API key |
| 402 | Request failed (e.g., card declined) |
| 429 | Rate limit exceeded |
