import os
from openai import OpenAI
from PyPDF2 import PdfReader
from gradio_client import Client
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.utils import export_to_video
import torch



try:
    client = OpenAI(
        # If the environment variable is not configured, replace the following line with your API key: api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )
    print("success")
except Exception as e:
    print(f"Error message: {e}")

#main function
#get the pdf file from the html
reader = PdfReader("example.pdf")
all_text = ""
for page_num, page in enumerate(reader.pages, start=1):
    text = page.extract_text()
    if text:
        all_text += text + "\n"
summary = summaryfunction(all_text)
text_to_audio = audiofunction(all_text)
generateaudio(text_to_audio)
generatevideo(summary)
#combine the video and audio
#post the video the html



#qwen for summary function
def summaryfunction(text):
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",  # Model list: https://www.alibabacloud.com/help/en/model-studio/getting-started/models
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Who are you?'}
                ]
        )
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error message: {e}")
    return completion.choices[0].message.content

#qwen for audio function
def audiofunction(text):
    pass



#using wan to generate video
def generatevideo(text):
    try:
        model_id = "Wan-AI/Wan2.1-T2V-14B-Diffusers"
        vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
        pipe = WanPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
        pipe.to("cuda")

        prompt = "A cat walks on the grass, realistic"
        negative_prompt = "Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, still picture, messy background, three legs, many people in the background, walking backwards"

        output = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            height=480,
            width=832,
            num_frames=81,
            guidance_scale=5.0
        ).frames[0]
        export_to_video(output, "output.mp4", fps=15)

    except Exception as e:
        print(f"Error message: {e}")

    

#generate audio
def generateaudio(text):
    pass