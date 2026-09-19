"""Classify an image into one of 20 categories using Azure OpenAI GPT-4o.

Usage:
    python image_classifier.py images/sample.png
"""

import base64
import os
import re
import sys
from mimetypes import guess_type

from openai import OpenAI


# Azure OpenAI credentials
AZURE_OPENAI_ENDPOINT = "https://YOUR-RESOURCE.openai.azure.com/openai/v1"
AZURE_OPENAI_KEY = "YOUR_AZURE_OPENAI_KEY"
AZURE_OPENAI_DEPLOYMENT = "gpt-5"

# Predefined categories
LABELS = [
    "cat",
    "dog",
    "car",
    "bicycle",
    "truck",
    "bus",
    "airplane",
    "boat",
    "train",
    "person",
    "tree",
    "flower",
    "building",
    "computer",
    "phone",
    "book",
    "chair",
    "food",
    "animal",
    "landscape",
]

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
)


def image_to_data_url(path: str) -> str:
    """Convert a local image into a Base64 data URL."""
    mime_type, _ = guess_type(path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("The selected file is not a supported image.")

    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def classify_image(image_path: str) -> str:
    """Classify the image and return one allowed label."""
    data_url = image_to_data_url(image_path)
    allowed_labels = ", ".join(LABELS)

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an image classifier. Choose exactly one allowed label. "
                    "If none applies, return other."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Allowed labels: [{allowed_labels}]. "
                            "Return only the lowercase label name."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "auto"},
                    },
                ],
            },
        ],
        max_completion_tokens=1000,
    )

    label = response.choices[0].message.content or "other"
    label = re.sub(r"[^a-zA-Z0-9_-]", "", label).lower()
    return label if label in LABELS else "other"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python image_classifier.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.isfile(image_path):
        print(f"Image not found: {image_path}")
        sys.exit(1)

    try:
        print(f"Classifying image: {image_path}")
        predicted_label = classify_image(image_path)
        print(f"Predicted label: {predicted_label}")
    except Exception as error:
        print(f"Classification failed: {error}")
        sys.exit(1)
