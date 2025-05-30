from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from .ttp import generate_image

@register("pic-gen", "喵喵", "使用硅基流动api 让llm帮你画图", "0.0.2")
class MyPlugin(Star):
    def __init__(self, context: Context,config: dict):
        super().__init__(context)
        self.api_key = config.get("api_key")
        # self.model = config.get("model")
        self.image_size = config.get("image_size")
        self.timeout = config.get("timeout")
        self.seed = config.get("seed")
        
    @llm_tool(name="pic-gen")
    async def pic_gen(self, event: AstrMessageEvent, prompt: str, model: str = "black-forest-labs/FLUX.1-schnell") -> MessageEventResult:
        """
        When a user requires image generation or drawing, and asks you to create an image, 
        or when you need to create a drawing to demonstrate or present something to the user, 
        call this function. If the image description provided by the user is not in English,
        translate it into English and reformat it to facilitate generation by the stable-diffusion model.
        **Autonomously enrich the prompt with additional details to achieve better results**,
        focusing on clarity, specificity, and context, without asking the user for further requirements.
        Autonomously select the most suitable model based on the request: 
        use `black-forest-labs/FLUX.1-schnell` for high-resolution images with rich details and a focus on anatomical precision,
        and use `stabilityai/stable-diffusion-3-5-large` for realistic skin textures and diverse artistic styles. **Only these two models should be used**.

        Args:  
            prompt (string): Image description provided by the user, which will be enriched autonomously.  
            model (string): Model name (`black-forest-labs/FLUX.1-schnell` or `stabilityai/stable-diffusion-3-5-large`).
        """
        # 确保从配置中正确加载
        api_key = self.api_key
        image_size = self.image_size
        timeout = self.timeout
        seed = self.seed

        # 如果 seed 为 0，设置为 None
        if seed == 0:
            seed = None

        # 调用生成图像的函数
        image_url, image_base64 = await generate_image(prompt, api_key, model=model, image_size=image_size, seed=seed, timeout=timeout)

        # 返回生成的图像
        if image_base64 is None:
            if image_url is not None:
                # 网络不佳，下载超时时，尝试直接发送图像URL
                chain = [
                    Plain(f"已生成图像，提示词：{prompt}\n模型：{model}\n图像URL：{image_url}"),
                    ]
            else:
                # 处理API响应失败的情况
                chain = [Plain("图像生成失败，请稍后重试。")]
        else:
            # 同时返回文本和图像
            chain = [
                Plain(f"已生成图像，提示词：{prompt}\n模型：{model}"),
                Image.fromBase64(image_base64)
            ]
        yield event.chain_result(chain)