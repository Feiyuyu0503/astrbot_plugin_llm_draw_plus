import random
import aiohttp
import asyncio
import base64

async def generate_image(prompt, api_key, model="stabilityai/stable-diffusion-3-5-large", seed=None, image_size="1024x1024", timeout=30):
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
                        await asyncio.sleep(1)
                        continue

                    if 'images' in data and data['images']:
                        image = data['images'][0]  # 获取第一个生成的图像
                        image_url = image['url']
                        try:
                            async with session.get(image_url, timeout=timeout) as img_response:
                                if img_response.status == 200:
                                    image_data = await img_response.read()
                                    # 转换为base64
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    return image_url, image_base64
                                else:
                                    return None, None
                        except asyncio.TimeoutError:
                            return None, None
                    else:
                        return None, None
            except asyncio.TimeoutError:
                return None, None
            except Exception as e:
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