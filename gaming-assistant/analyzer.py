"""Claude vision API integration for screen analysis."""
import base64
import json
import io
from PIL import Image
import anthropic

SYSTEM_PROMPT = """You are a gaming assistant AI embedded in a HUD overlay.
Your job is to analyze game screenshots and extract genuinely useful information
the player should remember or act on — such as: passwords, access codes, quest
objectives, coordinates, item stats, NPC names, puzzle solutions, or critical tips.

ONLY respond if there is actionable or memorable information worth surfacing.
If the screen shows nothing noteworthy (menus, loading screens, combat with no
special info, etc.), return has_info: false.

Respond ONLY with valid JSON in this exact format:
{
  "has_info": true,
  "title": "SHORT CATEGORY LABEL",
  "items": [
    {"label": "FIELD", "value": "data here"},
    {"label": "FIELD2", "value": "data here"}
  ],
  "summary": "One sentence of context"
}

Or if nothing noteworthy:
{"has_info": false}

Keep labels SHORT (1-2 words, uppercase). Values concise. Max 6 items."""

_client = None


def get_client(api_key: str) -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def analyze_screenshot(image: Image.Image, api_key: str) -> dict | None:
    """Send screenshot to Claude and return parsed info dict or None."""
    buffer = io.BytesIO()
    # Downscale to reduce tokens/cost while keeping readable
    img = image.copy()
    img.thumbnail((1280, 720), Image.LANCZOS)
    img.save(buffer, format="JPEG", quality=75)
    image_data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

    client = get_client(api_key)
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Analyze this game screenshot for important information.",
                        },
                    ],
                }
            ],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        if data.get("has_info"):
            return data
        return None
    except (json.JSONDecodeError, anthropic.APIError, IndexError):
        return None
