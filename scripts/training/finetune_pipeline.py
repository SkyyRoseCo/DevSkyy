#!/usr/bin/env python3
"""
SkyyRose Unified Fine-Tuning Pipeline
======================================

Fine-tune models on Replicate and HuggingFace for SkyyRose brand consistency.

Supports:
1. Image LoRA (Replicate) - Flux/SDXL for product generation
2. LLM Fine-tuning (HuggingFace) - Brand voice for descriptions

Usage:
    # Train image LoRA on Replicate
    python scripts/training/finetune_pipeline.py image --provider replicate

    # Train LLM on HuggingFace
    python scripts/training/finetune_pipeline.py llm --provider huggingface

    # Train both
    python scripts/training/finetune_pipeline.py all

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
for env_file in [PROJECT_ROOT / ".env", PROJECT_ROOT / ".env.hf"]:
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    value = value.strip().strip('"').strip("'")
                    if value:
                        os.environ.setdefault(key.strip(), value)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


class TrainingProvider(StrEnum):
    """Training providers."""

    REPLICATE = "replicate"
    HUGGINGFACE = "huggingface"


class ModelType(StrEnum):
    """Model types for fine-tuning."""

    IMAGE_LORA = "image_lora"
    LLM = "llm"


@dataclass
class TrainingConfig:
    """Unified training configuration."""

    # Common
    model_type: ModelType
    provider: TrainingProvider
    dataset_name: str = "skyyrose-training-data"
    output_name: str = "skyyrose-finetuned"

    # Image LoRA config (Replicate)
    image_trigger_word: str = "skyyrose"
    image_steps: int = 1000
    image_lora_rank: int = 16
    image_learning_rate: float = 4e-4
    image_resolution: str = "512,768,1024"

    # LLM config (HuggingFace)
    llm_base_model: str = "meta-llama/Llama-3.2-3B-Instruct"
    llm_epochs: int = 3
    llm_batch_size: int = 4
    llm_learning_rate: float = 2e-5
    llm_lora_rank: int = 8
    llm_max_length: int = 512


@dataclass
class TrainingResult:
    """Result from a training run."""

    success: bool
    model_type: ModelType
    provider: TrainingProvider
    model_url: str | None = None
    training_id: str | None = None
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.utcnow)


# =============================================================================
# Brand Training Data
# =============================================================================

SKYYROSE_BRAND_EXAMPLES = [
    # Product descriptions (input -> ideal output pairs)
    {
        "input": "Write a product description for a rose gold hoodie.",
        "output": """Introducing the SkyyRose Signature Hoodie - where Oakland street culture meets luxury craftsmanship.

Draped in our iconic rose gold hue, this premium heavyweight hoodie embodies the essence of elevated streetwear. Each piece is meticulously crafted with attention to detail that speaks to our commitment to excellence.

Features:
- Premium 400gsm cotton blend for ultimate comfort
- Embroidered SkyyRose monogram with metallic thread
- Relaxed fit for effortless style
- Double-lined hood with rose gold drawstrings

This isn't just clothing - it's a statement of refined rebellion, a testament to those who dare to stand out while standing tall.

Limited pieces. Timeless style. Exclusively SkyyRose.""",
    },
    {
        "input": "Describe the Black Rose collection aesthetic.",
        "output": """The Black Rose Collection emerges from the shadows where midnight meets elegance.

This limited edition line channels dark romantic energy through noir photography aesthetics and gothic florals. Each piece tells a story of mysterious allure and sophisticated rebellion.

The collection features:
- Deep obsidian blacks with subtle rose undertones
- Embroidered thorned roses in silver thread
- Premium materials that drape like shadows
- Limited numbering for exclusivity

For those who find beauty in darkness and luxury in the unconventional. The Black Rose Collection speaks to the bold souls who wear their complexity with pride.

Oakland born. Luxury refined. Unmistakably SkyyRose.""",
    },
    {
        "input": "Create marketing copy for Love Hurts windbreaker.",
        "output": """Love Hurts - but it never looked this good.

The Love Hurts Windbreaker transforms vulnerability into visual poetry. Our heart motif bleeds with intention, each droplet a reminder that authentic connection requires courage.

Crafted for the romantics who refuse to play it safe:
- Water-resistant shell with satin finish
- Embroidered bleeding heart on back panel
- Mesh-lined for breathability
- Hidden pocket with heart zipper pull

This piece doesn't just protect you from the elements - it announces your arrival. For those who've loved deeply and emerged stronger.

Wear your heart on your sleeve. Literally.

SkyyRose.""",
    },
    {
        "input": "Write Instagram caption for new collection drop.",
        "output": """New drop just landed.

The Signature Collection isn't about following trends - it's about setting them. Rose gold meets Oakland attitude in every stitch.

Limited pieces. Unlimited confidence.

Link in bio. Don't sleep on this.

#SkyyRose #OaklandFashion #LuxuryStreetwear #SignatureCollection""",
    },
    {
        "input": "Describe SkyyRose brand values.",
        "output": """SkyyRose stands at the intersection of love and luxury, where Oakland's authentic street culture elevates into refined expression.

Our Core Values:

AUTHENTICITY - Born from real community, real stories, real passion. We don't manufacture culture; we celebrate it.

QUALITY - Every piece is crafted with meticulous attention. Premium materials, thoughtful construction, lasting value.

INCLUSIVITY - Luxury without boundaries. Our designs celebrate all bodies, all genders, all walks of life.

ELEVATION - We take the familiar and make it extraordinary. Street roots, luxury branches.

LOVE - At our core, we believe fashion should feel like coming home. Comfortable. Confident. Complete.

""",
    },
]

# System prompt for the fine-tuned model
SKYYROSE_SYSTEM_PROMPT = """You are SkyyRose's brand voice - a luxury streetwear brand from Oakland, California.

Brand Guidelines:
- Tone: Sophisticated yet accessible, bold yet elegant
- Style: Poetic, evocative, with street culture authenticity
- Colors: Rose gold (#B76E79), black (#1A1A1A), pastels
- Collections: Signature (classic), Black Rose (dark romantic), Love Hurts (edgy)

Always emphasize:
- Premium quality and craftsmanship
- Oakland heritage and authenticity
- Gender-neutral inclusivity
- Limited edition exclusivity
- Emotional connection through fashion

Never use: cheap, discount, basic, generic, mass-produced"""


# =============================================================================
# Replicate Image LoRA Training
# =============================================================================


class ReplicateTrainer:
    """Train image LoRA on Replicate."""

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def prepare_dataset(self) -> str:
        """Prepare and upload training dataset to HuggingFace."""
        import shutil
        import zipfile

        from PIL import Image

        dataset_dir = PROJECT_ROOT / "datasets" / "skyyrose_lora_v3"
        images_dir = dataset_dir / "images"
        metadata_path = dataset_dir / "metadata.jsonl"

        # Try v1 if v3 doesn't exist
        if not images_dir.exists():
            dataset_dir = PROJECT_ROOT / "datasets" / "skyyrose_lora_v1"
            images_dir = dataset_dir / "images"
            metadata_path = dataset_dir / "metadata.jsonl"

        if not images_dir.exists():
            raise FileNotFoundError(f"Dataset not found: {images_dir}")

        # Load captions
        captions = {}
        if metadata_path.exists():
            with open(metadata_path) as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        captions[entry.get("file_name", "")] = entry.get("text", "")

        # Create temp directory
        temp_dir = PROJECT_ROOT / "temp_training_data"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        image_count = 0
        target_size = 512

        for img_path in sorted(images_dir.glob("*")):
            if img_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                try:
                    img = Image.open(img_path).convert("RGB")
                    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

                    # Pad to square
                    if img.size != (target_size, target_size):
                        new_img = Image.new("RGB", (target_size, target_size), (255, 255, 255))
                        offset = (
                            (target_size - img.size[0]) // 2,
                            (target_size - img.size[1]) // 2,
                        )
                        new_img.paste(img, offset)
                        img = new_img

                    output_name = f"{img_path.stem}.jpg"
                    img.save(temp_dir / output_name, "JPEG", quality=85, optimize=True)

                    # Caption file
                    caption = captions.get(
                        img_path.name, f"{self.config.image_trigger_word} luxury streetwear product"
                    )
                    with open(temp_dir / f"{img_path.stem}.txt", "w") as f:
                        f.write(caption)

                    image_count += 1
                except Exception as e:
                    logger.warning(f"Skipped {img_path.name}: {e}")

        logger.info(f"Prepared {image_count} images")

        # Create zip
        zip_path = PROJECT_ROOT / "skyyrose_training_data.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in temp_dir.iterdir():
                zf.write(file, file.name)

        shutil.rmtree(temp_dir)

        size_mb = zip_path.stat().st_size / 1024 / 1024
        logger.info(f"Created {zip_path} ({size_mb:.1f} MB)")

        # Upload to HuggingFace
        return self._upload_to_hf(str(zip_path))

    def _upload_to_hf(self, zip_path: str) -> str:
        """Upload to HuggingFace Hub."""
        from huggingface_hub import HfApi

        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_ACCESS_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found")

        api = HfApi(token=hf_token)
        repo_id = "damBruh/skyyrose-lora-dataset-v3"
        filename = Path(zip_path).name

        api.upload_file(
            path_or_fileobj=zip_path,
            path_in_repo=f"training/{filename}",
            repo_id=repo_id,
            repo_type="dataset",
        )

        return f"https://huggingface.co/datasets/{repo_id}/resolve/main/training/{filename}"

    def train(self) -> TrainingResult:
        """Start LoRA training on Replicate."""
        logger.info("Preparing training dataset...")
        data_url = self.prepare_dataset()

        logger.info("Starting Flux LoRA training on Replicate...")

        training_input = {
            "input_images": data_url,
            "trigger_word": self.config.image_trigger_word,
            "steps": self.config.image_steps,
            "lora_rank": self.config.image_lora_rank,
            "optimizer": "adamw8bit",
            "batch_size": 1,
            "resolution": self.config.image_resolution,
            "autocaption": False,
            "autocaption_prefix": self.config.image_trigger_word,
            "lr_scheduler": "constant",
            "learning_rate": self.config.image_learning_rate,
        }

        # Flux trainer
        trainer_version = "26dce37af90b9d997eeb970d92e47de3064d46c300504ae376c75bef6a9022d2"

        response = httpx.post(
            f"https://api.replicate.com/v1/models/ostris/flux-dev-lora-trainer/versions/{trainer_version}/trainings",
            headers=self.headers,
            json={
                "destination": f"dambruh/{self.config.output_name}",
                "input": training_input,
            },
            timeout=60.0,
        )

        if response.status_code not in (200, 201):
            return TrainingResult(
                success=False,
                model_type=ModelType.IMAGE_LORA,
                provider=TrainingProvider.REPLICATE,
                error=f"Training failed: {response.text}",
            )

        training = response.json()
        training_id = training.get("id")

        logger.info(f"Training started: {training_id}")
        logger.info(f"Monitor: https://replicate.com/p/{training_id}")

        return TrainingResult(
            success=True,
            model_type=ModelType.IMAGE_LORA,
            provider=TrainingProvider.REPLICATE,
            training_id=training_id,
            model_url=f"https://replicate.com/dambruh/{self.config.output_name}",
            metrics={"steps": self.config.image_steps, "lora_rank": self.config.image_lora_rank},
        )


# =============================================================================
# HuggingFace LLM Fine-tuning
# =============================================================================


class HuggingFaceTrainer:
    """Fine-tune LLM on HuggingFace."""

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_ACCESS_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN not found in environment")

    def prepare_dataset(self) -> str:
        """Prepare training dataset in chat format."""
        from datasets import Dataset

        # Format as chat conversations
        conversations = []
        for example in SKYYROSE_BRAND_EXAMPLES:
            conversations.append(
                {
                    "messages": [
                        {"role": "system", "content": SKYYROSE_SYSTEM_PROMPT},
                        {"role": "user", "content": example["input"]},
                        {"role": "assistant", "content": example["output"]},
                    ]
                }
            )

        # Create HuggingFace dataset
        dataset = Dataset.from_list(conversations)

        # Upload to Hub
        repo_id = f"damBruh/{self.config.dataset_name}-llm"
        dataset.push_to_hub(repo_id, token=self.hf_token, private=False)

        logger.info(f"Dataset uploaded: https://huggingface.co/datasets/{repo_id}")
        return repo_id

    def train(self) -> TrainingResult:
        """Start LLM fine-tuning on HuggingFace."""
        logger.info("Preparing LLM training dataset...")
        dataset_repo = self.prepare_dataset()

        logger.info("Starting LLM fine-tuning via HuggingFace AutoTrain...")

        # Create training config for AutoTrain
        autotrain_config = {
            "task": "llm-sft",
            "base_model": self.config.llm_base_model,
            "project_name": self.config.output_name + "-llm",
            "log": "tensorboard",
            "backend": "spaces-a10g-small",
            "data": {
                "path": dataset_repo,
                "train_split": "train",
                "valid_split": None,
                "chat_template": "chatml",
            },
            "params": {
                "epochs": self.config.llm_epochs,
                "batch_size": self.config.llm_batch_size,
                "lr": self.config.llm_learning_rate,
                "peft": True,
                "quantization": "int4",
                "lora_r": self.config.llm_lora_rank,
                "lora_alpha": self.config.llm_lora_rank * 2,
                "target_modules": "all-linear",
                "max_seq_length": self.config.llm_max_length,
                "padding": "right",
                "model_max_length": self.config.llm_max_length,
                "push_to_hub": True,
                "repo_id": f"damBruh/{self.config.output_name}-llm",
            },
        }

        # Save config
        config_path = PROJECT_ROOT / "config" / "autotrain_config.yaml"
        import yaml

        with open(config_path, "w") as f:
            yaml.dump(autotrain_config, f, default_flow_style=False)

        logger.info(f"AutoTrain config saved: {config_path}")
        logger.info("\nTo start training, run:")
        logger.info(f"  autotrain --config {config_path}")
        logger.info("\nOr via HuggingFace Spaces:")
        logger.info("  https://huggingface.co/spaces/autotrain-projects/autotrain-advanced")

        return TrainingResult(
            success=True,
            model_type=ModelType.LLM,
            provider=TrainingProvider.HUGGINGFACE,
            model_url=f"https://huggingface.co/damBruh/{self.config.output_name}-llm",
            metrics={
                "base_model": self.config.llm_base_model,
                "epochs": self.config.llm_epochs,
                "lora_rank": self.config.llm_lora_rank,
                "examples": len(SKYYROSE_BRAND_EXAMPLES),
            },
        )


# =============================================================================
# Main Pipeline
# =============================================================================


def run_training(
    model_type: str = "all",
    provider: str | None = None,
) -> list[TrainingResult]:
    """Run fine-tuning pipeline.

    Args:
        model_type: "image", "llm", or "all"
        provider: "replicate", "huggingface", or None for auto

    Returns:
        List of training results
    """
    results = []

    if model_type in ("image", "all"):
        config = TrainingConfig(
            model_type=ModelType.IMAGE_LORA,
            provider=TrainingProvider.REPLICATE,
            output_name="skyyrose-lora-v4",
        )
        trainer = ReplicateTrainer(config)
        result = trainer.train()
        results.append(result)

        if result.success:
            logger.info(f"Image LoRA training started: {result.model_url}")
        else:
            logger.error(f"Image LoRA training failed: {result.error}")

    if model_type in ("llm", "all"):
        config = TrainingConfig(
            model_type=ModelType.LLM,
            provider=TrainingProvider.HUGGINGFACE,
            output_name="skyyrose-brand-voice",
        )
        trainer = HuggingFaceTrainer(config)
        result = trainer.train()
        results.append(result)

        if result.success:
            logger.info(f"LLM training config ready: {result.model_url}")
        else:
            logger.error(f"LLM training failed: {result.error}")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="SkyyRose Fine-Tuning Pipeline")
    parser.add_argument(
        "model_type",
        choices=["image", "llm", "all"],
        help="Type of model to fine-tune",
    )
    parser.add_argument(
        "--provider",
        choices=["replicate", "huggingface"],
        help="Training provider (auto-selected if not specified)",
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("  SKYYROSE FINE-TUNING PIPELINE")
    logger.info(f"  Model Type: {args.model_type}")
    logger.info("=" * 70 + "\n")

    results = run_training(args.model_type, args.provider)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("  TRAINING SUMMARY")
    logger.info("=" * 70)

    for result in results:
        status = "SUCCESS" if result.success else "FAILED"
        logger.info(f"\n{result.model_type.value.upper()} ({result.provider.value}):")
        logger.info(f"  Status: {status}")
        if result.model_url:
            logger.info(f"  Model URL: {result.model_url}")
        if result.training_id:
            logger.info(f"  Training ID: {result.training_id}")
        if result.error:
            logger.info(f"  Error: {result.error}")
        if result.metrics:
            logger.info(f"  Metrics: {json.dumps(result.metrics, indent=4)}")

    return 0 if all(r.success for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
