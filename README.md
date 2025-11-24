# Todoist-Notion Integration

Custom Notion-Todist integration for my own workflow. Runs weekly using Github Actions. 


## Setup

### 1. Environment Variables

The following environment variables are required:
- `TODOIST_TOKEN`: Your Todoist API Bearer token
- `NOTION_TOKEN`: Your Notion integration token

### 2. Notion Setup

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Share your "Journal" page with the integration
3. Copy the integration token

### 3. Todoist Setup

1. Get your API token from Todoist settings
2. Make sure you have a "Reflections" project
