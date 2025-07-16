import asyncio
import base64
import os
import urllib
import httpx
import subprocess
import sys
from pathlib import Path
import random
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any

from uuid import uuid4

import asyncclick as click

from a2a.client import A2AClient, A2ACardResolver

from a2a.types import (
    Part,
    TextPart,
    FilePart,
    FileWithBytes,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    MessageSendConfiguration,
    SendMessageRequest,
    SendStreamingMessageRequest,
    MessageSendParams,
    GetTaskRequest,
    TaskQueryParams,
    JSONRPCErrorResponse,
)
from common.utils.push_notification_auth import PushNotificationReceiverAuth


@click.command()
@click.option("--agent", default="http://localhost:10000")
@click.option("--session", default=0)
@click.option("--history", default=False)
@click.option("--use_push_notifications", default=False)
@click.option("--push_notification_receiver", default="http://localhost:5000")
@click.option("--header", multiple=True)
async def cli(
    agent,
    session,
    history,
    use_push_notifications: bool,
    push_notification_receiver: str,
    header,
):
    headers = {h.split("=")[0]: h.split("=")[1] for h in header}
    print(f"Will use headers: {headers}")
    async with httpx.AsyncClient(timeout=30, headers=headers) as httpx_client:
        card_resolver = A2ACardResolver(httpx_client, agent)
        card = await card_resolver.get_agent_card()

        print("======= Agent Card ========")
        print(card.model_dump_json(exclude_none=True))

        notif_receiver_parsed = urllib.parse.urlparse(push_notification_receiver)
        notification_receiver_host = notif_receiver_parsed.hostname
        notification_receiver_port = notif_receiver_parsed.port

        if use_push_notifications:
            from hosts.cli.push_notification_listener import (
                PushNotificationListener,
            )

            notification_receiver_auth = PushNotificationReceiverAuth()
            await notification_receiver_auth.load_jwks(f"{agent}/.well-known/jwks.json")

            push_notification_listener = PushNotificationListener(
                host=notification_receiver_host,
                port=notification_receiver_port,
                notification_receiver_auth=notification_receiver_auth,
            )
            push_notification_listener.start()

        client = A2AClient(httpx_client, agent_card=card)

        continue_loop = True
        streaming = card.capabilities.streaming
        context_id = session if session > 0 else uuid4().hex

        # Generate 6 videos with random number of animals
        for i in range(6):
            # Generate random attributes for the video
            num_animals = random.randint(1, 5)
            background_colors = ['blue', 'white', 'green', 'orange', 'yellow']
            ground_types = ['grass', 'concrete', 'soil', 'leaves', 'sand']
            
            # Select random attributes
            background = random.choice(background_colors)
            ground = random.choice(ground_types)
            
            print(f"\n=========  Generating video {i+1}/6 ======== ")
            print(f"Number of baby foxes: {num_animals}")
            print(f"Background color: {background}")
            print(f"Ground type: {ground}")
            
            # Create the enhanced prompt
            kitten_prompt = (
                f"Generate a video of {num_animals} baby foxes and a chicken playing together "
                f"on {ground} with a {background} background. "
                f"The scene should be bright, cheerful, and well-lit, with the animals "
                f"clearly visible against the {background} background."
            )
            
            # Send the prompt to generate the video
            continue_loop, _, taskId = await completeTask(
                client,
                streaming,
                use_push_notifications,
                notification_receiver_host,
                notification_receiver_port,
                None,
                context_id,
                initial_prompt=kitten_prompt
            )
            
            # Video generation completed
            if continue_loop and taskId:
                print("\nVideo generation completed successfully!")
                
                # If it's not the last iteration, wait for 1 minute before the next video
                if i < 5:
                    print("\nWaiting 1 minute before generating the next video...")
                    await asyncio.sleep(60)  # 60 seconds = 1 minute

            if history and continue_loop:
                print("========= history ======== ")
                # Create a proper request object for history
                history_request = GetTaskRequest(
                    params={
                        'id': taskId,
                        'history_length': 10
                    }
                )
                task_response = await client.get_task(history_request)
                print(
                    task_response.model_dump_json(include={"result": {"history": True}})
                )


async def completeTask(
    client: A2AClient,
    streaming,
    use_push_notifications: bool,
    notification_receiver_host: str,
    notification_receiver_port: int,
    taskId,
    contextId,
    initial_prompt=None,
):
    if initial_prompt is not None:
        prompt = initial_prompt
    else:
        prompt = click.prompt(
            "\nWhat do you want to send to the agent? (:q or quit to exit)"
        )
        if prompt == ":q" or prompt == "quit":
            return False, None, None

    message = Message(
        role="user",
        parts=[TextPart(text=prompt)],
        messageId=str(uuid4()),
        taskId=taskId,
        contextId=contextId,
    )

    payload = MessageSendParams(
        id=str(uuid4()),
        message=message,
        configuration=MessageSendConfiguration(
            acceptedOutputModes=["text"],
        ),
    )

    if use_push_notifications:
        payload["pushNotification"] = {
            "url": f"http://{notification_receiver_host}:{notification_receiver_port}/notify",
            "authentication": {
                "schemes": ["bearer"],
            },
        }

    taskResult = None
    message = None
    if streaming:
        response_stream = client.send_message_streaming(
            SendStreamingMessageRequest(
                id=str(uuid4()),
                params=payload,
            )
        )
        async for result in response_stream:
            if isinstance(result.root, JSONRPCErrorResponse):
                print("Error: ", result.root.error)
                return False, contextId, taskId
            event = result.root.result
            contextId = event.contextId
            if isinstance(event, Task):
                taskId = event.id
            elif isinstance(event, TaskArtifactUpdateEvent):
                print(f"\n[DEBUG] Received TaskArtifactUpdateEvent")
                print(f"[DEBUG] Task ID: {event.taskId}")
                print(f"[DEBUG] Artifact name: {getattr(event.artifact, 'name', 'N/A')}")
                print(f"[DEBUG] Number of parts: {len(event.artifact.parts) if hasattr(event.artifact, 'parts') else 0}")
                
                taskId = event.taskId
                
                if not hasattr(event.artifact, 'parts') or not event.artifact.parts:
                    print("[DEBUG] No parts found in artifact")
                    continue
                    
                # Print GCS URI for video artifacts
                for i, part in enumerate(event.artifact.parts):
                    print(f"\n[DEBUG] Processing part {i+1}")
                    print(f"[DEBUG] Part data: {part}")
                    
                    # Handle case where part is wrapped in 'root' attribute
                    if hasattr(part, 'root') and part.root:
                        print("[DEBUG] Found part wrapped in 'root' attribute")
                        part = part.root
                    
                    # Check if this is a file part
                    part_type = getattr(part, 'type', None) or getattr(part, 'kind', None)
                    if part_type != 'file':
                        print(f"[DEBUG] Part is not a file, found type/kind: {part_type}")
                        continue
                        
                    # Access file data directly from the part
                    file_data = getattr(part, 'file', None)
                    if not file_data:
                        print("[DEBUG] Part has no 'file' data")
                        continue
                        
                    file_data = part.file
                    print(f"[DEBUG] File data: {file_data}")
                    
                    if not hasattr(file_data, 'mimeType') or not file_data.mimeType:
                        print("[DEBUG] No mimeType found in file data")
                        continue
                        
                    print(f"[DEBUG] MIME type: {file_data.mimeType}")
                    
                    if 'video/' not in file_data.mimeType:
                        print("[DEBUG] Not a video MIME type, skipping")
                        continue
                        
                    if not hasattr(file_data, 'uri') or not file_data.uri:
                        print("[DEBUG] No URI found in file data")
                        continue
                        
                    # Extract GCS URI from the signed URL
                    uri = file_data.uri
                    print(f"[SUCCESS] Video available at: {uri}")
                    print(f"[DEBUG] Full video URI: {uri}")
                    
                    if 'storage.googleapis.com' in uri:
                        # Convert signed URL to GCS URI
                        try:
                            path = uri.split('storage.googleapis.com', 1)[1].split('?')[0]
                            gcs_uri = f"gs:/{path}"
                            print(f"\n[VIDEO GENERATED] GCS URI: {gcs_uri}")
                            
                            # Upload to YouTube
                            print("\n[YOUTUBE] Starting YouTube upload...")
                            try:
                                # Get the absolute path to the upload script
                                script_dir = Path(__file__).parent.parent.parent
                                upload_script = script_dir / "youtube-video-upload" / "upload_video_now.py"
                                
                                # Run the upload script
                                # Generate dynamic metadata based on the task
                                title = f"AI Generated Video: {prompt[:50]}..." if prompt else "AI Generated Video"
                                description = f"Video generated from user prompt: {prompt}" if prompt else "AI Generated Video"
                                tags = ["AI", "generated", "video", "content"]
                                
                                # Run the upload script with dynamic parameters
                                result = subprocess.run(
                                    [sys.executable, str(upload_script), gcs_uri, title, description] + tags,
                                    capture_output=True,
                                    text=True
                                )
                                
                                # Print the output
                                if result.stdout:
                                    print(f"[YOUTUBE] {result.stdout}")
                                if result.stderr:
                                    print(f"[YOUTUBE ERROR] {result.stderr}")
                                
                                print(f"[YOUTUBE] Upload process completed with return code: {result.returncode}")
                                
                            except Exception as e:
                                print(f"[YOUTUBE ERROR] Failed to start upload process: {e}")
                            
                        except Exception as e:
                            print(f"[ERROR] Error parsing GCS URI: {e}")
                            print(f"[DEBUG] Original URI: {uri}")
                    else:
                        print(f"\n[VIDEO GENERATED] Non-GCS URI: {uri}")
                
                print("[DEBUG] Finished processing TaskArtifactUpdateEvent\n")
            elif isinstance(event, TaskStatusUpdateEvent):
                taskId = event.taskId
            elif isinstance(event, Message):
                message = event
            print(f"stream event => {event.model_dump_json(exclude_none=True)}")
        # Upon completion of the stream. Retrieve the full task if one was made.
        if taskId:
            taskResult = await client.get_task(
                GetTaskRequest(
                    id=str(uuid4()),
                    params=TaskQueryParams(id=taskId),
                )
            )
            taskResult = taskResult.root.result
    else:
        try:
            # For non-streaming, assume the response is a task or message.
            event = await client.send_message(
                SendMessageRequest(
                    id=str(uuid4()),
                    params=payload,
                )
            )
            event = event.root.result
        except Exception as e:
            print("Failed to complete the call", e)
        if not contextId:
            contextId = event.contextId
        if isinstance(event, Task):
            if not taskId:
                taskId = event.id
            taskResult = event
        elif isinstance(event, Message):
            message = event

    if message:
        print(f"\n{message.model_dump_json(exclude_none=True)}")
        return True, contextId, taskId
    if taskResult:
        # Don't print the contents of a file.
        task_content = taskResult.model_dump_json(
            exclude={
                "history": {
                    "__all__": {
                        "parts": {
                            "__all__": {"file"},
                        },
                    },
                },
            },
            exclude_none=True,
        )
        print(f"\n{task_content}")
        ## if the result is that more input is required, loop again.
        state = TaskState(taskResult.status.state)
        if state.name == TaskState.input_required.name:
            return (
                await completeTask(
                    client,
                    streaming,
                    use_push_notifications,
                    notification_receiver_host,
                    notification_receiver_port,
                    taskId,
                    contextId,
                ),
                contextId,
                taskId,
            )
        ## task is complete
        return True, contextId, taskId
    ## Failure case, shouldn't reach
    return True, contextId, taskId


if __name__ == "__main__":
    asyncio.run(cli())
