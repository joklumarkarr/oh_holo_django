import json

from channels.generic.websocket import AsyncWebsocketConsumer

GROUP_NAME = "vtuber_updates"

class LiveStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(GROUP_NAME, self.channel_name)

    # Channels maps a group_send's "type": "vtuber.update" to this method name
    # (dots become underscores). Whatever gets sent to the group lands here,
    # per-connection, and we just forward it straight to the browser as JSON.
    async def vtuber_update(self, event):
        await self.send(text_data=json.dumps(event["vtuber"]))