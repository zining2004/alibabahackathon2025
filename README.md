# Hello, we are team super4!

# 🎬 From Slides to Stories: AI-Powered Comic & Video Generation

## 🚀 Project Overview

This project transforms traditionally boring academic slides into **binge-worthy comics and videos** using the power of AI. Our goal is to make studying more **engaging**, **visual**, and **fun**—especially for learners who benefit from multimedia or narrative-based learning formats.

We achieve this through a custom pipeline that integrates **Qwen** (a large language model) for text generation and **WAN 2.1** (a visual diffusion model) for comic/video generation.

---

## 🧠 What It Does

1. **PDF Upload & Parsing**  
   Users upload academic slides (PDFs), which are parsed to extract the textual content.

2. **Summary & Script Generation**  
   Using **Qwen**, we generate:
   - A **summary** of key concepts from the slides
   - A **scene-based script**, formatted as simple dialogues or narratives that can be visualised

3. **Comic/Video Generation**  
   The **scene script** is then passed to **WAN 2.1**, which interprets it to generate stylised **comic panels** or **animated video scenes**.

---

## 🧩 How It Works

### 1. **Model Studio + Qwen Fine-Tuning**
We used **Alibaba's Model Studio** to personalise Qwen before deploying Qwen-Turbo. To fine-tune the model, we uploaded our lecture notes from multiple domains:
- Business
- Mathematics
- Sustainability
- Computing

This ensured that Qwen understood our content style, structure, and language use.

### 2. **Prompt Engineering for Content Generation**
We created custom prompts to make Qwen generate:
- Concise, accessible summaries
- Scene-based scripts (e.g., dialogues between characters, narrations, and transitions)

These are designed to feed directly into WAN 2.1 as visual generation prompts.

### 3. **Integration with WAN 2.1**
The output script is sent to **WAN 2.1**, a generative model for stylised image and video synthesis. WAN 2.1 turns the scenes into:
- Illustrated comics
- Animated video segments

The result? Academic content that looks and feels like storytelling media.

---

## 📦 Tech Stack

| Component | Description |
|----------|-------------|
| 📄 PDFs | Academic slides (lecture notes, study materials) |
| 🧠 Qwen (via Model Studio) | Language model used for summarising and script generation |
| 🎨 WAN 2.1 | Visual model used to generate comics and video from text |
| 🧰 Model Studio | Alibaba Cloud platform for model fine-tuning and prompt testing |
| 🧾 Prompt Templates | Custom prompts structured to extract summaries and scenes |

---

## 🎯 Use Cases

- Students struggling with dry or text-heavy content  
- Visual learners who benefit from comics and scenes  
- Educators seeking more engaging teaching tools  
- Self-learners and revision aids before exams

---

## 🌱 Future Enhancements

- Add voiceovers and narration to generated videos  
- Allow users to edit or customise characters in scenes  
- Multi-language support (e.g., Chinese, Malay, Tamil)  
- Adaptive scene generation based on learner preferences

---

## 👩‍💻 Contributors
- **Rochelle Chong Li Han** -- Project Leader, Frontend developer
- **Neo Zi Ning** -- Backend developer
- **Lee Pei Xin** — Backend developer
- **Jodie Lim Zhuo Ying** -- Frontend and backend developer  
- Additional collaborators and advisors to be added!


---

## 📝 License

This project is currently under development and shared for educational and prototyping purposes only.
