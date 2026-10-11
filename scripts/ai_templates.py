"""Embedded HF Space templates for AI CLI."""

from __future__ import annotations

from scripts.ai_config import AIConfig

TRAINER_APP_TEMPLATE = '''import gradio as gr
import subprocess
import sys
import os


def install_dependencies():
    """Install training dependencies."""
    deps = [
        "diffusers[torch]", "transformers", "accelerate",
        "peft", "bitsandbytes", "datasets", "torchvision"
    ]
    for dep in deps:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", dep],
            check=True
        )


def train_lora(progress=gr.Progress()):
    """Run LoRA training on persistent GPU."""
    logs = []
    try:
        if 'OMP_NUM_THREADS' in os.environ:
            del os.environ['OMP_NUM_THREADS']
        os.environ['OMP_NUM_THREADS'] = '4'
        logs.append("Environment configured")
        yield "\\n".join(logs)

        progress(0.05, desc="Installing dependencies...")
        install_dependencies()
        logs.append("Dependencies installed")
        yield "\\n".join(logs)

        progress(0.1, desc="Downloading training script...")
        import requests
        script_url = "https://raw.githubusercontent.com/huggingface/diffusers/v0.36.0/examples/text_to_image/train_text_to_image_lora_sdxl.py"
        response = requests.get(script_url)
        with open("train_text_to_image_lora_sdxl.py", "w") as f:
            f.write(response.text)
        logs.append("Training script ready")
        yield "\\n".join(logs)

        progress(0.15, desc="Configuring accelerate...")
        subprocess.run(["accelerate", "config", "default"], check=True)
        logs.append("Accelerate configured")
        yield "\\n".join(logs)

        progress(0.2, desc="Starting LoRA training...")
        output_dir = "lora-output"
        train_cmd = [
            "accelerate", "launch", "train_text_to_image_lora_sdxl.py",
            "--pretrained_model_name_or_path={base_model}",
            "--pretrained_vae_model_name_or_path={vae_model}",
            "--dataset_name={dataset}",
            "--image_column=image",
            "--caption_column=text",
            f"--output_dir={{output_dir}}",
            "--mixed_precision=fp16",
            "--resolution={resolution}",
            "--train_batch_size=1",
            "--gradient_accumulation_steps={gradient_accumulation}",
            "--gradient_checkpointing",
            "--learning_rate={learning_rate}",
            "--snr_gamma=5.0",
            "--lr_scheduler=constant",
            "--lr_warmup_steps=0",
            "--use_8bit_adam",
            "--max_train_steps={steps}",
            "--checkpointing_steps=500",
            "--seed={seed}",
        ]

        process = subprocess.Popen(
            train_cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        for line in process.stdout:
            line = line.strip()
            if line:
                logs.append(line)
                if len(logs) > 100:
                    logs = logs[-100:]
                yield "\\n".join(logs)
        process.wait()

        if process.returncode != 0:
            logs.append(f"Training failed (exit {{process.returncode}})")
            yield "\\n".join(logs)
            return

        progress(0.92, desc="Uploading to Hub...")
        from huggingface_hub import HfApi
        hub_api = HfApi(token=os.environ.get("HF_TOKEN", ""))
        hub_api.create_repo("{output_repo}", exist_ok=True)
        hub_api.upload_folder(
            folder_path=output_dir,
            repo_id="{output_repo}",
            commit_message="LoRA trained on {dataset} ({steps} steps, SDXL, {resolution}px)"
        )

        progress(1.0, desc="Done!")
        logs.append("TRAINING COMPLETE")
        logs.append("Model: https://huggingface.co/{output_repo}")
    except Exception as e:
        logs.append(f"Error: {{e}}")
    yield "\\n".join(logs)


demo = gr.Interface(
    fn=train_lora, inputs=[],
    outputs=gr.Textbox(label="Training Progress", lines=30, max_lines=50, show_copy_button=True),
    title="SkyyRose LoRA Training",
    description="LoRA training for SkyyRose. Dataset: {dataset}. Trigger: {trigger_word}",
    api_name="predict"
)
demo.queue().launch()
'''

REQUIREMENTS_TEMPLATE = """gradio==5.50.0
huggingface_hub>=0.33.5,<2
requests>=2.32.0
torch>=2.1.0
accelerate>=1.0.0
diffusers[torch]>=0.31.0
transformers>=4.47.0
peft>=0.14.0
bitsandbytes>=0.45.0
datasets>=3.2.0
torchvision>=0.20.0
"""


def render_trainer_app(config: AIConfig) -> str:
    """Render the trainer Space app.py with config values."""
    return TRAINER_APP_TEMPLATE.format(
        base_model=config.base_model,
        vae_model=config.vae_model,
        dataset=config.dataset,
        resolution=config.resolution,
        gradient_accumulation=config.gradient_accumulation,
        learning_rate=config.learning_rate,
        steps=config.steps,
        seed=config.seed,
        output_repo=config.output_repo,
        trigger_word=config.trigger_word,
    )


def render_requirements() -> str:
    """Render requirements.txt for trainer Space."""
    return REQUIREMENTS_TEMPLATE
