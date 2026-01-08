# Trello REST API - Create a Card

## Overview
Creates a new card on a Trello board. Cards represent tasks, ideas, or items that can be organized in lists.

## Endpoint
`POST https://api.trello.com/1/cards`

## Authentication
Requires API Key and Token as query parameters:
```
?key={apiKey}&token={apiToken}
```

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `idList` | string | The ID of the list the card should be created in |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The name/title of the card |
| `desc` | string | Description of the card (Markdown supported) |
| `pos` | string/number | Position in list: "top", "bottom", or a positive number |
| `due` | string | Due date in ISO format (e.g., "2024-01-15T12:00:00.000Z") |
| `start` | string | Start date in ISO format |
| `dueComplete` | boolean | Whether the due date is complete |
| `idMembers` | string | Comma-separated member IDs to assign |
| `idLabels` | string | Comma-separated label IDs to apply |
| `urlSource` | string | A URL to attach to the card |
| `idCardSource` | string | ID of a card to copy |
| `keepFromSource` | string | Properties to keep when copying: "all", or comma-separated list |
| `address` | string | Address for location |
| `locationName` | string | Name of location |
| `coordinates` | string | Latitude,longitude |

## Payload Examples

### Simple Card
```json
{
  "idList": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "name": "New Task",
  "desc": "Description of the task"
}
```

### Card with Due Date
```json
{
  "idList": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "name": "Complete project review",
  "desc": "Review all deliverables before deadline",
  "due": "2024-01-20T17:00:00.000Z",
  "pos": "top"
}
```

### Card with Labels and Members
```json
{
  "idList": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "name": "Bug: Login page not loading",
  "desc": "## Issue\nLogin page returns 500 error\n\n## Steps to reproduce\n1. Go to /login\n2. See error",
  "idLabels": "5f1a2b3c4d5e6f7a8b9c0d1e,5f1a2b3c4d5e6f7a8b9c0d2f",
  "idMembers": "5f1a2b3c4d5e6f7a8b9c0d3g",
  "due": "2024-01-10T09:00:00.000Z"
}
```

### Card with Attachment URL
```json
{
  "idList": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "name": "Review this article",
  "desc": "Great reference for our project",
  "urlSource": "https://example.com/article",
  "pos": "bottom"
}
```

### Full Card with All Options
```json
{
  "idList": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "name": "Sprint Planning Task",
  "desc": "## Objective\nPlan the upcoming sprint\n\n## Checklist\n- [ ] Review backlog\n- [ ] Estimate stories\n- [ ] Assign tasks",
  "pos": "top",
  "due": "2024-01-15T14:00:00.000Z",
  "start": "2024-01-08T09:00:00.000Z",
  "dueComplete": false,
  "idMembers": "member1id,member2id",
  "idLabels": "labelid1,labelid2"
}
```

## Response

Returns the created card:

```json
{
  "id": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "name": "New Task",
  "desc": "Description of the task",
  "closed": false,
  "idList": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "idBoard": "5f1a2b3c4d5e6f7a8b9c0d1e",
  "pos": 65535,
  "due": null,
  "dueComplete": false,
  "idMembers": [],
  "labels": [],
  "url": "https://trello.com/c/abc123/1-new-task",
  "shortUrl": "https://trello.com/c/abc123",
  "dateLastActivity": "2024-01-08T12:00:00.000Z"
}
```

## Liquid Template Example

### Simple Card
```liquid
{
  "idList": "{{ list_id }}",
  "name": "{{ task_name }}",
  "desc": "{{ task_description }}"
}
```

### Card with Due Date
```liquid
{
  "idList": "{{ list_id }}",
  "name": "{{ task.name }}",
  "desc": "{{ task.description }}",
  "due": "{{ task.due_date }}",
  "pos": "top"
}
```

### Multiple Cards from Array
```liquid
[{% for task in tasks %}
  {
    "idList": "{{ list_id }}",
    "name": "{{ task.name }}",
    "desc": "{{ task.description }}"
  }{% unless forloop.last %},{% endunless %}{% endfor %}
]
```

## Common Errors

| Error | Description |
|-------|-------------|
| 400 | Invalid list ID or malformed request |
| 401 | Invalid API key or token |
| 404 | List or board not found |
| 429 | Rate limit exceeded (300 requests per 10 seconds) |
