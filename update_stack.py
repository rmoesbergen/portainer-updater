#!/usr/bin/env python3

""" Small tool to update a stack in Portainer """

import argparse
import syslog

import requests


def update_stack(stack_name: str, api_key: str, base_url) -> None:
    """Update a stack in Portainer"""
    headers = {"X-API-Key": api_key}
    stacks = requests.get(f"{base_url}/stacks", headers=headers, timeout=10).json()
    for stack in stacks:
        if stack["Name"] == stack_name:
            stack_id = stack["Id"]
            endpoint_id = stack["EndpointId"]
            compose_file = requests.get(
                f"{base_url}/stacks/{stack_id}/file", headers=headers, timeout=10
            ).json()

            response = requests.put(
                f"{base_url}/stacks/{stack_id}?endpointId={endpoint_id}",
                headers=headers,
                json={
                    "prune": True,
                    "pullImage": True,
                    "stackFileContent": compose_file["StackFileContent"],
                },
                timeout=300,
            )
            if response.ok:
                syslog.syslog(
                    syslog.LOG_INFO, f"Updated portainer stack {stack['Name']}"
                )
            else:
                syslog.syslog(
                    syslog.LOG_ERR,
                    f"Updating portainer stack {stack['Name']} failed: {response.content}",
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stack_name", help="Name of the stack in portainer to update")
    parser.add_argument("api_key", help="API key for portainer")
    parser.add_argument(
        "--url",
        help="URL for portainer (default http://localhost:9000/api)",
        default="http://localhost:9000/api",
    )
    config = parser.parse_args()
    update_stack(config.stack_name, config.api_key, config.url)
