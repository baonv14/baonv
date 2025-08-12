#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Optional


OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"


def env_default(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)


def call_openai_images(prompt: str, size: str, api_key: str, quality: str = "standard") -> bytes:
    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(OPENAI_IMAGES_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp_body = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI API error {e.code}: {body}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e}") from None

    parsed = json.loads(resp_body)
    if "data" not in parsed or not parsed["data"]:
        raise RuntimeError(f"Unexpected API response: {parsed}")

    b64 = parsed["data"][0].get("b64_json")
    if not b64:
        raise RuntimeError(f"No image data in response: {parsed}")

    return base64.b64decode(b64)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate an image from a text prompt using OpenAI Images API (gpt-image-1)",
    )
    p.add_argument("--prompt", required=True, help="Text prompt describing the image")
    p.add_argument("--size", default=env_default("IMG_SIZE", "1024x1024"), help="Image size, e.g. 1024x1024")
    p.add_argument("--quality", default=env_default("IMG_QUALITY", "standard"), help="Image quality: standard or high")
    p.add_argument("--output", default=env_default("IMG_OUT", "output.png"), help="Output image file path")
    p.add_argument("--openai-api-key", default=env_default("OPENAI_API_KEY"), help="OpenAI API key (or set OPENAI_API_KEY)")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.openai_api_key:
        parser.error("Missing --openai-api-key or environment variable OPENAI_API_KEY")
        return 2

    try:
        image_bytes = call_openai_images(
            prompt=args.prompt,
            size=args.size,
            api_key=args.openai_api_key,
            quality=args.quality,
        )
        with open(args.output, "wb") as f:
            f.write(image_bytes)
        print(f"Saved image to {args.output}")
        return 0
    except Exception as exc:
        print(f"Failed to generate image: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())