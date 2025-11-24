#!/usr/bin/env python3
"""
Reflections Sync Script

This script fetches tasks from the "Reflections" project in Todoist
and creates a new page in the "Journal" database in Notion with these tasks.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from notion_client import Client


class TodoistClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.base_url = "https://api.todoist.com/rest/v2"

    def get_project_id(self, project_name: str) -> Optional[str]:
        """Get project ID by name"""
        response = requests.get(f"{self.base_url}/projects", headers=self.headers)
        response.raise_for_status()
        projects = response.json()
        
        for project in projects:
            if project["name"] == project_name:
                return project["id"]
        return None

    def get_project_tasks(self, project_id: str) -> List[Dict]:
        """Get all tasks from a specific project"""
        params = {"project_id": project_id}
        response = requests.get(f"{self.base_url}/tasks", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()


class NotionClient:
    def __init__(self, token: str):
        self.client = Client(auth=token)

    def find_page_by_name(self, name: str) -> Optional[str]:
        """Find page ID by name"""
        try:
            response = self.client.search(query=name)
            for result in response["results"]:
                if result.get("object") == "page" and result.get("properties"):
                    # Check if it has a title property
                    title_prop = result["properties"].get("title") or result["properties"].get("Name")
                    if title_prop and title_prop.get("title") and len(title_prop["title"]) > 0:
                        if title_prop["title"][0]["plain_text"] == name:
                            return result["id"]
        except Exception as e:
            print(f"Error finding page {name}: {e}")
        return None

    def create_reflections_child_page(self, parent_page_id: str, title: str, tasks: List[Dict]) -> str:
        """Create a new child page under the Journal page with reflection tasks"""
        # Create page content from tasks
        content_blocks = []
        
        if tasks:
            content_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Reflection Tasks"}}]
                }
            })
            
            for task in tasks:
                content_blocks.append({
                    "object": "block", 
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": task["content"]}}]
                    }
                })
        else:
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "No reflection tasks found for this week."}}]
                }
            })

        # Create the child page
        page = self.client.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "title": [{"text": {"content": title}}]
            },
            children=content_blocks
        )
        
        return page["id"]


def get_week_title(date: datetime) -> str:
    """Generate week title in format 'Nov 25 Week 1'"""
    # Get the first day of the month
    first_day = date.replace(day=1)
    
    # Calculate which week of the month this is
    days_passed = date.day - 1
    week_number = (days_passed // 7) + 1
    
    # Format the title
    month_day = date.strftime("%b %d")
    return f"{month_day} Week {week_number}"


def main():
    # Load environment variables
    todoist_token = os.getenv("TODOIST_TOKEN")
    notion_token = os.getenv("NOTION_TOKEN")
    
    if not all([todoist_token, notion_token]):
        print("Missing required environment variables: TODOIST_TOKEN, NOTION_TOKEN")
        return

    # Initialize clients
    todoist = TodoistClient(todoist_token)
    notion = NotionClient(notion_token)

    # Get Reflections project
    project_id = todoist.get_project_id("Reflections")
    if not project_id:
        print("Reflections project not found in Todoist")
        return

    print(f"Found Reflections project with ID: {project_id}")

    # Get tasks from the project
    tasks = todoist.get_project_tasks(project_id)
    print(f"Found {len(tasks)} tasks in Reflections project")

    # Find Journal page
    journal_page_id = notion.find_page_by_name("Journal")
    if not journal_page_id:
        journal_page_id = "22a44c06-f763-809c-8fa7-cf92cb21f61e"

    print(f"Found Journal page")
    
    # Test if we can access the page
    try:
        notion.client.pages.retrieve(journal_page_id)
    except Exception as e:
        print(f"Cannot access Journal page: {e}")
        return

    # Generate title for this week
    today = datetime.now()
    week_title = f"Reflections {get_week_title(today)}"
    print(f"Creating page with title: {week_title}")

    # Create the child page
    try:
        page_id = notion.create_reflections_child_page(journal_page_id, week_title, tasks)
        print(f"Successfully created page with ID: {page_id}")
        print(f"Page contains {len(tasks)} reflection tasks")
    except Exception as e:
        print(f"Error creating page: {e}")


if __name__ == "__main__":
    main()