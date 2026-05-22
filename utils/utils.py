from config_data.config_data import Config, load_config

from xml.etree import ElementTree
from datetime import datetime, timedelta
from pathlib import Path
import requests
import logging
import asyncio
import openai
import aiohttp
import base64
import os
import re

config: Config = load_config()


async def convert_image_to_base64(filename: str) -> str:
    """Конвертирование изоражение в base64 строку"""
    logging.info('convert_image_to_base64')
    with open(filename, 'rb') as f:
        image_bytes = f.read()

    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # Определяем MIME тип по расширению
    ext = Path(filename).suffix.lower()
    mime_map = {'.jpg': 'jpeg', '.jpeg': 'jpeg', '.png': 'png', '.webp': 'webp'}
    mime_type = mime_map.get(ext, 'png')

    image_url = f"data:image/{mime_type};base64,{image_base64}"
    return image_url


async def calculate_cost_main(type: str, agent: str, quality: str, long: int):
    """Выбор типа генерации для подсчета стоимости"""
    logging.info('calculate_cost_main')
    if type == 'generate-photo':
        return await calculate_cost_photo(agent, quality)

    if type == 'generate-video':
        return await calculate_cost_video(agent, long)

    if type == 'edit-photo':
        return await calculate_cost_edit_photo(agent, quality)


async def calculate_cost_edit_photo(agent: str, quality: str) -> int:
    """Подсчет стоимости для обработки изоюражения"""
    logging.info('calculate_cost_edit_photo')
    agents_cost = {
        "google/gemini-2.5-flash-image": 16,
        "google/gemini-3.1-flash-image-preview": 16,
        "google/gemini-3-pro-image-preview": 16,
        "openai/gpt-5-image": 16,
        "openai/gpt-5-image-mini": 16
    }

    quality_cost = {
        '1k': 4,
        '2k': 6,
        '4k': 8
    }

    total_summ = agents_cost[agent] + quality_cost[quality]
    return total_summ


async def calculate_cost_photo(agent: str, quality: str) -> int:
    """Подсчет стоимости генерации для фото"""
    logging.info('calculate_cost_photo')
    agents_cost = {
        "google/gemini-2.5-flash-image": 16,
        "google/gemini-3.1-flash-image-preview": 16,
        "google/gemini-3-pro-image-preview": 16,
        "openai/gpt-5-image": 16,
        "openai/gpt-5-image-mini": 16
    }

    quality_cost = {
        '1k': 4,
        '2k': 6,
        '4k': 8
    }

    total_summ = agents_cost[agent] + quality_cost[quality]
    return total_summ


async def calculate_cost_video(agent: str, long: int) -> int:
    """подсчет стоимости генерации видео"""
    logging.info('calculate_cost_video')
    agents_cost = {
        "google/veo-3.1-fast": 18,
        "google/veo-3.1-lite": 12,
        "kwaivgi/kling-v3.0-pro": 25,
        "kwaivgi/kling-v3.0-std": 20
    }

    total_summ = agents_cost[agent] * long
    return total_summ


async def check_data(text: str):
    """Проверка наличия данных в тексте"""
    logging.info('check_data')
    quality = '1k'
    format = '16:9'

    if '1k' in text.lower() or '1к' in text.lower():
        quality = '1k'
    if '2k' in text.lower() or '2к' in text.lower():
        quality = '2k'
    if '4k' in text.lower() or '4к' in text.lower():
        quality = '4k'



    if '1:1' in text.lower():
        format = '1:1'
    if '16:9' in text.lower():
        format = '16:9'
    if '9:16' in text.lower():
        format = '9:16'
    if '4:3' in text.lower():
        format = '4:3'
    if '3:4' in text.lower():
        format = '3:4'

    return quality, format


async def start_generate(type: str, agent: str, quality: str, format: str, prompt: str, long: int, user_id: int, file_path: str):
    """Определение типа генерации"""
    logging.info(f'start_generate type" {type} agent: {agent} quality: {quality} format: {format} long: {long}')
    if type == 'generate-photo':
        return await generate_image(agent, quality, format, prompt, user_id)

    if type == 'generate-video':
        return await generate_video(agent, format, prompt, user_id, long)

    if type == 'edit-photo':
        return await edit_image(agent, quality, format, prompt, user_id, file_path)


async def edit_image(agent: str, quality: str, format: str, prompt: str, user_id: int, file_path: str):
    """Редактирование существующего изображения"""
    logging.info(f'edit_image: {agent}, file_path={file_path}')
    filename = ""
    message = ""
    image_bytes = None

    client = openai.OpenAI(
        api_key=config.tg_bot.ai_token,
        base_url="https://openrouter.ai/api/v1"
    )

    # Читаем изображение и конвертируем в base64
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        file_base64 = base64.b64encode(file_bytes).decode('utf-8')

        # Определяем MIME тип по расширению
        ext = Path(file_path).suffix.lower()
        mime_map = {
            '.jpg': 'jpeg',
            '.jpeg': 'jpeg',
            '.png': 'png',
            '.webp': 'webp',
            '.gif': 'gif'
        }
        mime_type = mime_map.get(ext, 'png')

        image_url = f"data:image/{mime_type};base64,{file_base64}"
        logging.info(f"Image loaded, size: {len(file_bytes)} bytes, mime: image/{mime_type}")

    except Exception as e:
        logging.error(f"Failed to read image file: {e}")
        return "", f"❌ Не удалось прочитать файл: {str(e)}"

    # Формируем content как массив (текст + изображение)
    content_parts = [
        {"type": "text", "text": prompt},
        {
            "type": "image_url",
            "image_url": {"url": image_url}
        }
    ]

    # Формируем запрос
    request_params = {
        "model": agent,
        "messages": [
            {
                "role": "user",
                "content": content_parts  # 👈 Массив, а не строка!
            }
        ],
        "modalities": ["image", "text"],
    }

    # Добавляем параметры изображения, если они есть
    extra_body = {}
    if format and format != "auto":
        extra_body["aspect_ratio"] = format
    if quality and quality != "auto":
        extra_body["resolution"] = quality
    if extra_body:
        request_params["extra_body"] = extra_body

    try:
        response = client.chat.completions.create(**request_params)
        msg = response.choices[0].message
        message = msg.content or ""
        logging.info(f"Response received, finish_reason: {response.choices[0].finish_reason}")
    except Exception as e:
        logging.error(f"API error: {e}")
        return "", f"❌ Ошибка API: {str(e)}"

    # ----- ИЗВЛЕКАЕМ СГЕНЕРИРОВАННОЕ ИЗОБРАЖЕНИЕ -----
    # (код полностью совпадает с вашим существующим)

    # СПОСОБ 1: message.images
    if hasattr(msg, 'images') and msg.images and len(msg.images) > 0:
        logging.info("Found message.images, attempting to extract...")
        try:
            img = msg.images[0]

            # Получаем URL изображения
            url = None
            if isinstance(img, dict):
                url = img.get('image_url', {}).get('url')
            elif hasattr(img, 'image_url'):
                if hasattr(img.image_url, 'url'):
                    url = img.image_url.url
                elif isinstance(img.image_url, dict):
                    url = img.image_url.get('url')

            if url:
                logging.info(f"Image URL type: {type(url)}, starts with data:image? {url.startswith('data:image')}")

                if url.startswith('data:image/png;base64,'):
                    base64_string = url.replace('data:image/png;base64,', '')
                    image_bytes = base64.b64decode(base64_string)
                    logging.info(f"✅ Extracted PNG image, size: {len(image_bytes)} bytes")

                elif url.startswith('data:image/jpeg;base64,') or url.startswith('data:image/jpg;base64,'):
                    base64_string = url.replace('data:image/jpeg;base64,', '').replace('data:image/jpg;base64,', '')
                    image_bytes = base64.b64decode(base64_string)
                    logging.info(f"✅ Extracted JPEG image, size: {len(image_bytes)} bytes")

                else:
                    # Пробуем любой data:image формат
                    match = re.match(r'data:image/(\w+);base64,(.+)$', url)
                    if match:
                        image_format = match.group(1)
                        base64_string = match.group(2)
                        image_bytes = base64.b64decode(base64_string)
                        logging.info(f"✅ Extracted {image_format.upper()} image, size: {len(image_bytes)} bytes")
                    else:
                        logging.warning(f"Unknown image format in URL: {url[:100]}")

        except Exception as e:
            logging.error(f"Failed to extract from message.images: {e}")
            import traceback
            logging.error(traceback.format_exc())

    # СПОСОБ 2: Поиск base64 в message.content
    if not image_bytes and message:
        pattern = r'data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=]+)'
        match = re.search(pattern, message)
        if match:
            try:
                image_format = match.group(1)
                base64_string = match.group(2)
                image_bytes = base64.b64decode(base64_string)
                message = re.sub(pattern, '', message).strip()
                logging.info(f"✅ Extracted {image_format} from content, size: {len(image_bytes)} bytes")
            except Exception as e:
                logging.error(f"Failed to decode base64 from content: {e}")

    # ------ СОХРАНЯЕМ РЕДАКТИРОВАННОЕ ИЗОБРАЖЕНИЕ ------

    if image_bytes:
        os.makedirs("generations/photo", exist_ok=True)

        # Определяем расширение файла
        extension = "png"
        if hasattr(msg, 'images') and msg.images:
            try:
                img = msg.images[0]
                url = None
                if isinstance(img, dict):
                    url = img.get('image_url', {}).get('url')
                elif hasattr(img, 'image_url') and hasattr(img.image_url, 'url'):
                    url = img.image_url.url

                if url and 'image/jpeg' in url:
                    extension = "jpg"
                elif url and 'image/png' in url:
                    extension = "png"
            except:
                pass

        filename = f"generations/photo/edit_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"

        with open(filename, 'wb') as f:
            f.write(image_bytes)

        logging.info(f"✅ Edited image saved: {filename}")

        if not message or message.strip() == "":
            message = "✅ Изображение успешно отредактировано!"

        return filename, message

    # ------ НЕ НАШЛИ ИЗОБРАЖЕНИЕ ------

    logging.warning(f"❌ No image extracted. message.content length: {len(message) if message else 0}")

    if not message:
        message = "❌ Не удалось отредактировать изображение. Проверьте баланс OpenRouter."

    return "", message


async def generate_image(agent: str, quality: str, format: str, prompt, user_id: int):
    """Генерация фото + сохранение """
    logging.info(f'generate_image: {agent}')
    filename = ""
    message = ""
    image_bytes = None

    client = openai.OpenAI(
        api_key=config.tg_bot.ai_token,
        base_url="https://openrouter.ai/api/v1"
    )

    # Формируем запрос
    request_params = {
        "model": agent,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "extra_body": {
            "aspect_ratio": format,
            "resolution": quality
        }
    }

    response = client.chat.completions.create(**request_params)
    msg = response.choices[0].message
    message = msg.content or ""


    # СПОСОБ 1: message.images
    if hasattr(msg, 'images') and msg.images and len(msg.images) > 0:
        logging.info("Found message.images, attempting to extract...")
        try:
            img = msg.images[0]

            # Получаем URL изображения
            url = None
            if isinstance(img, dict):
                url = img.get('image_url', {}).get('url')
            elif hasattr(img, 'image_url'):
                if hasattr(img.image_url, 'url'):
                    url = img.image_url.url
                elif isinstance(img.image_url, dict):
                    url = img.image_url.get('url')

            if url:
                logging.info(f"Image URL type: {type(url)}, starts with data:image? {url.startswith('data:image')}")

                if url.startswith('data:image/png;base64,'):
                    base64_string = url.replace('data:image/png;base64,', '')
                    image_bytes = base64.b64decode(base64_string)
                    logging.info(f"✅ Extracted PNG image, size: {len(image_bytes)} bytes")

                elif url.startswith('data:image/jpeg;base64,') or url.startswith('data:image/jpg;base64,'):
                    base64_string = url.replace('data:image/jpeg;base64,', '').replace('data:image/jpg;base64,', '')
                    image_bytes = base64.b64decode(base64_string)
                    logging.info(f"✅ Extracted JPEG image, size: {len(image_bytes)} bytes")

                else:
                    # Пробуем любой data:image формат
                    import re
                    match = re.match(r'data:image/(\w+);base64,(.+)$', url)
                    if match:
                        image_format = match.group(1)
                        base64_string = match.group(2)
                        image_bytes = base64.b64decode(base64_string)
                        logging.info(f"✅ Extracted {image_format.upper()} image, size: {len(image_bytes)} bytes")
                    else:
                        logging.warning(f"Unknown image format in URL: {url[:100]}")

        except Exception as e:
            logging.error(f"Failed to extract from message.images: {e}")
            import traceback
            logging.error(traceback.format_exc())

    # СПОСОБ 2: Поиск base64 в message.content
    if not image_bytes and message:
        import re
        # Ищем любой data:image формат
        pattern = r'data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=]+)'
        match = re.search(pattern, message)
        if match:
            try:
                image_format = match.group(1)
                base64_string = match.group(2)
                image_bytes = base64.b64decode(base64_string)
                message = re.sub(pattern, '', message).strip()
                logging.info(f"✅ Extracted {image_format} from content, size: {len(image_bytes)} bytes")
            except Exception as e:
                logging.error(f"Failed to decode base64 from content: {e}")

    # ------ СОХРАНЯЕМ ИЗОБРАЖЕНИЕ ------

    if image_bytes:
        import os
        os.makedirs("generations/photo", exist_ok=True)

        # Определяем расширение файла (по умолчанию PNG)
        extension = "png"
        if hasattr(msg, 'images') and msg.images:
            try:
                img = msg.images[0]
                url = None
                if isinstance(img, dict):
                    url = img.get('image_url', {}).get('url')
                elif hasattr(img, 'image_url') and hasattr(img.image_url, 'url'):
                    url = img.image_url.url

                if url and 'image/jpeg' in url:
                    extension = "jpg"
                elif url and 'image/png' in url:
                    extension = "png"
            except:
                pass

        filename = f"generations/photo/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"

        with open(filename, 'wb') as f:
            f.write(image_bytes)

        logging.info(f"✅ Image saved: {filename}")

        if not message or message.strip() == "":
            message = "✅ Изображение сгенерировано!"

        return filename, message

    # ------ НЕ НАШЛИ ИЗОБРАЖЕНИЕ ------

    logging.warning(f"❌ No image extracted. message.content length: {len(message) if message else 0}")

    if not message:
        message = "❌ Не удалось сгенерировать изображение. Проверьте баланс OpenRouter."

    return "", message


async def generate_video(agent: str, format: str, prompt: str, user_id: int, duration: int):
    """Генерация видео через асинхронный API OpenRouter"""
    logging.info(f'generate_video')
    filename = ""
    message = ""

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {config.tg_bot.ai_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": agent,
                "prompt": prompt,
                "aspect_ratio": format,
                "duration": duration,
            }

            # Отправляем запрос
            async with session.post(
                    "https://openrouter.ai/api/v1/videos",
                    headers=headers,
                    json=payload) as resp:

                if resp.status not in [200, 202]:
                    error_text = await resp.text()
                    logging.error(f"Video submission failed: {error_text}")
                    return "", f"❌ Ошибка при отправке запроса: {resp.status}"

                job_data = await resp.json()
                job_id = job_data.get('id')
                polling_url = job_data.get('polling_url')

                if not job_id or not polling_url:
                    logging.error(f"Invalid response: {job_data}")
                    return "", "❌ Не удалось получить ID задачи"

                logging.info(f"Video job submitted: {job_id}")

            # ШАГ 2: Ожидаем завершения генерации (полинг)
            max_attempts = 60  # 60 * 10 сек = 10 минут
            attempt = 0

            while attempt < max_attempts:
                await asyncio.sleep(10)
                attempt += 1

                async with session.get(polling_url, headers=headers) as poll_resp:
                    if poll_resp.status != 200:
                        logging.warning(f"Polling failed: {poll_resp.status}")
                        continue

                    status_data = await poll_resp.json()
                    status = status_data.get('status')
                    logging.info(f"Video status: {status}, attempt {attempt}/{max_attempts}")

                    if status == 'completed':
                        video_urls = status_data.get('unsigned_urls', [])

                        if not video_urls:
                            logging.error(f"No unsigned_urls in completed response: {status_data}")
                            return "", "❌ Видео сгенерировано, но ссылка не найдена"

                        video_url = video_urls[0]
                        logging.info(f"Downloading video from: {video_url[:80]}...")

                        # Скачиваем видео (unsigned_urls уже публичные, headers не нужны)
                        async with session.get(video_url, headers=headers) as video_resp:
                            if video_resp.status == 200:
                                video_bytes = await video_resp.read()

                                import os
                                os.makedirs("generations/video", exist_ok=True)
                                filename = f"generations/video/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

                                with open(filename, 'wb') as f:
                                    f.write(video_bytes)

                                logging.info(f"✅ Video saved: {filename}")

                                message = f"✅ Видео успешно сгенерировано!\n"

                                return filename, message
                            else:
                                logging.error(f"Failed to download video: {video_resp.status}")
                                return "", "❌ Не удалось скачать видео"

                    elif status == 'failed':
                        error = status_data.get('error', 'Неизвестная ошибка')
                        logging.error(f"Video generation failed: {error}")
                        return "", f"❌ Ошибка генерации: {error}"

                    elif status in ['pending', 'processing', 'queued']:
                        continue  # Просто продолжаем ждать

                    else:
                        logging.warning(f"Unknown status: {status}")

            return "", "❌ Превышено время ожидания генерации видео (10 минут)"

    except Exception as e:
        logging.error(f"Video generation error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return "", f"❌ Ошибка: {str(e)}"


async def convert_function(rub_summ: int, currency: str):
    """Конвертация рублей в другую валюту"""
    logging.info('convert_function')
    if currency != "RUB":
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = requests.get(url)

        # Парсим XML-ответ
        root = ElementTree.fromstring(response.content)
        for valute in root.findall('Valute'):
            if valute.find('CharCode').text == currency:
                # Курс записан как 70,9509 (с запятой)
                rate_str = valute.find('Value').text.replace(',', '.')
                usd_rate = float(rate_str)

                dollars = rub_summ / usd_rate
                return round(dollars, 1)
    else:
        return rub_summ


async def create_invoice(cost: int, currency: str, index: str):
    """Создание платежной ссылки"""
    logging.info('create_invoice')
    url = 'https://gate.lava.top/api/v3/invoice'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        "X-Api-Key": config.tg_bot.money_token
    }

    json = {
        "email": 'client@gmail.com',
        "offerId": "e6d516a8-c09e-4283-bc4c-3bcc473536b7",
        "currency": currency,
        "amount": cost
    }

    data = requests.post(headers=headers, json=json, url=url)
    data = data.json()

    logging.info(data)

    url = data['paymentUrl']
    payment_id = data['id']

    return url, payment_id


