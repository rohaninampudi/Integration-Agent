# Jira Cloud Platform REST API - Create Issue

## Overview
Creates a new issue (ticket) in a Jira project. Issues can be bugs, tasks, stories, epics, or custom issue types.

## Endpoint
`POST https://your-domain.atlassian.net/rest/api/3/issue`

## Authentication
Requires Basic Auth with API token or OAuth 2.0.

Headers:
```
Authorization: Basic {base64(email:api_token)}
Content-Type: application/json
```

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `fields.project.key` | string | Project key (e.g., "PROJ", "DEV") |
| `fields.summary` | string | Issue title/summary |
| `fields.issuetype.name` | string | Issue type: "Bug", "Task", "Story", etc. |

### Common Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `fields.description` | object | Rich text description (ADF format) |
| `fields.priority.name` | string | Priority: "Highest", "High", "Medium", "Low", "Lowest" |
| `fields.assignee.id` | string | Assignee's account ID |
| `fields.reporter.id` | string | Reporter's account ID |
| `fields.labels` | array | Array of label strings |
| `fields.components` | array | Array of component objects |
| `fields.fixVersions` | array | Array of version objects |
| `fields.duedate` | string | Due date (YYYY-MM-DD) |
| `fields.parent.key` | string | Parent issue key (for subtasks) |

## Description Format (Atlassian Document Format)

Jira uses ADF for rich text:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Description text here"
        }
      ]
    }
  ]
}
```

## Payload Examples

### Simple Bug
```json
{
  "fields": {
    "project": {
      "key": "PROJ"
    },
    "summary": "Login page returns 500 error",
    "issuetype": {
      "name": "Bug"
    }
  }
}
```

### Bug with Description and Priority
```json
{
  "fields": {
    "project": {
      "key": "PROJ"
    },
    "summary": "Users cannot reset password",
    "issuetype": {
      "name": "Bug"
    },
    "priority": {
      "name": "High"
    },
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "When users click 'Forgot Password', they receive a 404 error."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": { "level": 3 },
          "content": [
            { "type": "text", "text": "Steps to Reproduce" }
          ]
        },
        {
          "type": "orderedList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{ "type": "text", "text": "Go to login page" }]
                }
              ]
            },
            {
              "type": "listItem",
              "content": [
                {
                  "type": "paragraph",
                  "content": [{ "type": "text", "text": "Click 'Forgot Password'" }]
                }
              ]
            }
          ]
        }
      ]
    },
    "labels": ["production", "urgent"]
  }
}
```

### Task with Due Date
```json
{
  "fields": {
    "project": {
      "key": "DEV"
    },
    "summary": "Update API documentation",
    "issuetype": {
      "name": "Task"
    },
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Update the API docs to reflect the new endpoints."
            }
          ]
        }
      ]
    },
    "duedate": "2024-01-20",
    "priority": {
      "name": "Medium"
    }
  }
}
```

### Story with Components
```json
{
  "fields": {
    "project": {
      "key": "PROD"
    },
    "summary": "As a user, I want to export data to CSV",
    "issuetype": {
      "name": "Story"
    },
    "components": [
      { "name": "Backend" },
      { "name": "Export" }
    ],
    "labels": ["data", "export", "csv"]
  }
}
```

## Response

Returns the created issue:

```json
{
  "id": "10001",
  "key": "PROJ-123",
  "self": "https://your-domain.atlassian.net/rest/api/3/issue/10001"
}
```

## Liquid Template Example

### Simple Issue
```liquid
{
  "fields": {
    "project": {
      "key": "{{ project_key }}"
    },
    "summary": "{{ summary }}",
    "issuetype": {
      "name": "{{ issue_type | default: 'Bug' }}"
    }
  }
}
```

### Bug with Description
```liquid
{
  "fields": {
    "project": {
      "key": "{{ project_key }}"
    },
    "summary": "{{ summary }}",
    "issuetype": {
      "name": "Bug"
    },
    "priority": {
      "name": "{{ priority | default: 'Medium' }}"
    },
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "{{ description }}"
            }
          ]
        }
      ]
    },
    "labels": [{% for label in labels %}"{{ label }}"{% unless forloop.last %}, {% endunless %}{% endfor %}]
  }
}
```

## Common Errors

| Error | Description |
|-------|-------------|
| 400 | Required field missing or invalid value |
| 401 | Invalid authentication |
| 403 | No permission to create issues in project |
| 404 | Project or issue type not found |
