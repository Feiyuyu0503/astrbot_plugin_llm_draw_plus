import random
import aiohttp
import asyncio
import base64
from astrbot import logger

async def generate_image(prompt, api_key, model="stabilityai/stable-diffusion-3-5-large", seed=None, image_size="1024x1024", timeout=120):
    url = "https://api.siliconflow.cn/v1/images/generations"

    if seed is None:
        seed = random.randint(0, 9999999999)

    payload = {
        "model": model,
        "prompt": prompt,
        "image_size": image_size,
        "seed": seed
    }
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
                    data = await response.json()

                    if data.get("code") == 50505:
                        logger.error("Model service overloaded. Please try again later.")
                        await asyncio.sleep(1)
                        continue

                    if 'images' in data and data['images']:
                        image = data['images'][0]  # 获取第一个生成的图像
                        image_url = image['url']
                        # 添加info级别的日志输出
                        logger.info(f"成功获取图像URL: {image_url}")
                        try:
                            async with session.get(image_url, timeout=timeout) as img_response:
                                if img_response.status == 200:
                                    image_data = await img_response.read()
                                    # 转换为base64
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    logger.info(f"成功获取图像数据，长度: {len(image_base64)}")
                                    return image_url, image_base64
                                else:
                                    logger.error(f"下载图像失败，HTTP状态码: {img_response.status}")
                                    return image_url, None
                        except asyncio.TimeoutError:
                            logger.error(f"下载图像超时，尝试直接返回URL")
                            return image_url, None
                    else:
                        logger.error("API响应中未包含图像数据")
                        return None, None
            except asyncio.TimeoutError:
                logger.error("API请求超时")
                return None, None
            except Exception as e:
                logger.error(f"生成图像时发生错误: {str(e)}")
                return None, None


if __name__ == "__main__":
    # Example call
    prompt = (
        "A cute catgirl with blue hair, realistic and anthropomorphic, "
        "wearing a stylish outfit, standing in a serene forest with soft sunlight, "
        "detailed fur texture, expressive eyes, and a gentle smile."
    )
    api_key = ""
    
    async def test():
        image_url, image_base64 = await generate_image(prompt, api_key, model="black-forest-labs/FLUX.1-schnell")
        print(f"Image URL: {image_url}")
        print(f"Base64 data length: {len(image_base64) if image_base64 else 0}")
    
    asyncio.run(test())