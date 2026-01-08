# GitHub REST API - Create an Issue

## Overview
Creates a new issue in a GitHub repository.

## Endpoint
`POST /repos/{owner}/{repo}/issues`

## Authentication
Requires a personal access token or GitHub App with `issues:write` permission.

## Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `owner` | string | Repository owner (username or organization) |
| `repo` | string | Repository name |

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | The title of the issue |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `body` | string | The contents/description of the issue (Markdown supported) |
| `assignees` | array | Array of usernames to assign to the issue |
| `milestone` | integer | Milestone number to associate with the issue |
| `labels` | array | Array of label names to add to the issue |

## Payload Examples

### Simple Issue
```json
{
  "title": "Bug: Application crashes on startup"
}
```

### Issue with Description
```json
{
  "title": "Bug: Application crashes on startup",
  "body": "## Description\n\nThe application crashes immediately after launching.\n\n## Steps to Reproduce\n1. Launch the application\n2. Observe crash\n\n## Expected Behavior\nApplication should start normally."
}
```

### Issue with Labels and Assignees
```json
{
  "title": "Feature Request: Dark Mode",
  "body": "## Summary\n\nAdd a dark mode option for better visibility in low-light conditions.\n\n## Motivation\n\nMany users prefer dark mode for reduced eye strain.",
  "labels": ["enhancement", "ui", "good first issue"],
  "assignees": ["octocat", "hubot"]
}
```

### Automated Bug Report
```json
{
  "title": "Automated: Scrape Failed - 2024-01-08",
  "body": "## Error Details\n\nThe scheduled scrape job failed with the following error:\n\n```\nTimeoutError: Request exceeded 30000ms\nURL: https://example.com/products\n```\n\n## Context\n- Job ID: scrape-12345\n- Started: 2024-01-08T10:00:00Z\n- Failed: 2024-01-08T10:00:30Z\n\n---\n*This issue was automatically created by the Integration Agent.*",
  "labels": ["bug", "automated", "scraper"]
}
```

### Issue with Milestone
```json
{
  "title": "Update documentation for v2.0",
  "body": "Documentation needs to be updated to reflect changes in version 2.0",
  "labels": ["documentation"],
  "milestone": 3
}
```

## Response

### Success Response (201 Created)
```json
{
  "id": 1,
  "node_id": "MDU6SXNzdWUx",
  "url": "https://api.github.com/repos/octocat/Hello-World/issues/1347",
  "html_url": "https://github.com/octocat/Hello-World/issues/1347",
  "number": 1347,
  "state": "open",
  "title": "Found a bug",
  "body": "I'm having a problem with this.",
  "user": {
    "login": "octocat",
    "id": 1
  },
  "labels": [
    {
      "id": 208045946,
      "name": "bug",
      "color": "f29513"
    }
  ],
  "assignees": [],
  "milestone": null,
  "created_at": "2011-04-22T13:33:48Z",
  "updated_at": "2011-04-22T13:33:48Z"
}
```

### Error Response (422 Validation Failed)
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "resource": "Issue",
      "field": "title",
      "code": "missing_field"
    }
  ]
}
```

## Common Errors
| Status | Error | Description |
|--------|-------|-------------|
| 401 | Unauthorized | Bad credentials or missing authentication |
| 403 | Forbidden | No permission to create issues in this repo |
| 404 | Not Found | Repository does not exist |
| 410 | Gone | Issues are disabled for this repository |
| 422 | Validation Failed | Invalid input (e.g., missing title) |

## Markdown Support
The `body` field supports GitHub Flavored Markdown:
- **Bold**: `**text**`
- *Italic*: `*text*`
- Code: `` `code` ``
- Code blocks: ` ```language ... ``` `
- Lists: `- item` or `1. item`
- Headers: `## Header`
- Links: `[text](url)`
- Task lists: `- [ ] task`

## Liquid Template Example
For a workflow with `summary` variable:
```liquid
{
  "title": "Scrape Failed - Automated Report",
  "body": "## Error Details\n\n{{ summary }}\n\n---\n*This issue was automatically created.*",
  "labels": ["bug", "automated"]
}
```
