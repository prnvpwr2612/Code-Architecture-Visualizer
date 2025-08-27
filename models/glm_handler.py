# models/glm_handler.py

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from huggingface_hub import login, snapshot_download
import gc

class GLMHandler:
    def __init__(self, model_id="THUDM/glm-4-9b-chat", hf_token=None, local_dir="./models/glm4"):
        print("🚀 GLMHandler initialization started")
        self.model_id = model_id
        self.hf_token = hf_token or os.environ.get("HF_TOKEN", None)
        self.local_dir = local_dir
        self.model = None
        self.tokenizer = None
        self.load_success = False
        self._setup()

    def _setup(self):
        print(f"💾 Preparing environment for {self.model_id}")
        try:
            if self.hf_token:
                login(token=self.hf_token, add_to_git_credential=True)
                print("🔐 HuggingFace authentication: Success")
            else:
                print("⚠️ HuggingFace token not provided, proceeding in public mode")

            gpu_mem = torch.cuda.get_device_properties(0).total_memory // 1024**3 if torch.cuda.is_available() else 0
            quant_use = gpu_mem < 16

            if not os.path.exists(self.local_dir):
                print("⬇️ Downloading model from HuggingFace Hub...")
                snapshot_download(repo_id=self.model_id, local_dir=self.local_dir, resume_download=True, max_workers=4)
                print("✅ Model download complete!")
            else:
                print("📁 Model found locally.")

            self.tokenizer = AutoTokenizer.from_pretrained(self.local_dir, trust_remote_code=True, padding_side="left")
            print(f"🔠 Tokenizer loaded: {type(self.tokenizer).__name__}")

            if quant_use:
                print("🧮 Loading model with 4-bit quantization")
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.local_dir,
                    quantization_config=quant_config,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
            else:
                print("🧮 Loading full-precision float16 model")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.local_dir,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
            self.load_success = True
            print("🌟 GLM-4 model ready and loaded on device!")
        except Exception as e:
            print(f"❌ Model setup error: {str(e)}")
            print("Resolution strategies:\n- Verify HuggingFace access\n- Check VRAM availability\n- Try again after restarts\n- Test with smaller model\n- Contact support for persistent failures")

    def generate(self, prompt, max_new_tokens=300, temperature=0.7, top_p=0.9):
        print("✏️ GLM-4 Prompt received.")
        if not self.load_success:
            print("❌ Model not loaded, cannot generate output.")
            return "GLM Model unavailable."
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                inputs = inputs.to("cuda")
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    do_sample=False,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print("✅ GLM-4 generation successful!")
            return response
        except Exception as e:
            print(f"❌ GLM-4 inference error: {str(e)}")
            print("Resolution strategies:\n- Restart runtime\n- Check VRAM\n- Remove large input\n- Inspect input for errors\n- Ensure compatible CUDA/cuDNN")

    def generate_documentation(self, parsing_results):
        print("📝 AI Documentation requested for codebase.")
        gen_fn = lambda code: self.generate(f"Document this code in markdown (for developer handoff):\n\n{code}", max_new_tokens=400)
        auto_docs = {}
        try:
            parsed_files = parsing_results.get("parsed_files", {})
            for fname, meta in parsed_files.items():
                if meta.get("parsing_successful"):
                    code_lines = meta.get("source_code", None)
                    if code_lines and "docstring" not in meta:
                        result = gen_fn(code_lines[:512] if isinstance(code_lines, str) else "")
                        auto_docs[fname] = result
            print("✅ All AI documentation generated.")
            return auto_docs, "✅ Documentation complete"
        except Exception as e:
            print(f"❌ AI doc generation failed: {str(e)}")
            print("Resolution strategies:\n- Decrease file count/length\n- Try again after kernel restart\n- Verify tokenizer/model setup\n- Debug single file\n- Validate code integrity")
            return None, "❌ Documentation failure"

# Test print for GLMHandler cell
print("🎯 models/glm_handler.py module export ready.")
