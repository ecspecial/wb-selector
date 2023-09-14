import asyncio
import random
import time
from playwright.async_api import async_playwright

# Асинхронная функция для медленного ввода текста
async def type_slowly(page, selector, text):
    element = await page.query_selector(selector)
    for char in text:
        # Вводим по одному символу с случайной задержкой
        await element.type(char, delay=random.uniform(500, 700))

# Асинхронная функция для загрузки страницы
async def load_page(page):
    try:
        await page.goto("https://www.wildberries.ru/")
        await page.wait_for_selector('[class*=banner]', state='visible')
        print('-------> WB открыт (Wildberries открыт)')

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

# Асинхронная функция для ввода поискового запроса
async def type_search(page):
    try:
        print('-------> Начали поиск...')
        # Находим и фокусируемся на элементе ввода
        search_input = await page.wait_for_selector('#searchInput')
        print('-------> Нашли строку поиска')
        
        await search_input.click()
        print('-------> Кликнули на строку поиска')

        await type_slowly(page, '#searchInput', 'Блузка')
        print('-------> Вставили текстовый запрос')

        await page.keyboard.press('Enter')
        print('-------> Отправили поисковой запрос')

        await page.wait_for_selector(':has-text("По запросу")')
        print('-------> Карточки по запросу загрузились')

    except Exception as e:
        print(f"-------> Произошла ошибка: {str(e)}")

# Асинхронная функция для плавной прокрутки страницы
async def scroll_gradually(page):
    print('-------> Скроллим вниз страницы')
    try:
        previous_scroll_height = 0
        consecutive_no_height_change = 0  # Счетчик последовательных прокруток без изменения высоты

        while True:
            # Получаем текущую высоту прокрутки страницы
            current_scroll_height = await page.evaluate("document.body.scrollHeight")
            # print(f"Текущая высота страницы: {current_scroll_height}, Повторений скролла без изменений: {consecutive_no_height_change}")

            # Прокручиваем вниз на большой шаг (например, 300 пикселей)
            await page.evaluate("window.scrollBy(0, 300)")  # Можно настроить шаг прокрутки

            # Ждем некоторое время, чтобы прокрутка выглядела плавной
            await asyncio.sleep(0.8)

            # Проверяем, достигли ли мы конца страницы
            at_bottom = (await page.evaluate("window.innerHeight + window.scrollY")) >= current_scroll_height

            # Проверяем, не изменилась ли высота прокрутки
            if current_scroll_height == previous_scroll_height:
                consecutive_no_height_change += 1
            else:
                consecutive_no_height_change = 0  # Сбрасываем счетчик, если высота изменилась

            # Если мы достигли конца или не произошло изменение высоты в течение нескольких прокруток, завершаем цикл
            if at_bottom or consecutive_no_height_change >= 7:
                print('-------> Докрутили до конца страницу')
                break

            previous_scroll_height = current_scroll_height

    except Exception as e:
        print(f"-------> Произошла ошибка при прокрутке: {str(e)}")

# Асинхронная функция для поиска элемента по артикулу
async def find_element(page, id):
    try:
        page_number = 1  # Инициализируем номер страницы 1
        print(f'-------> Ищем товар с артикулом {id} на странице {page_number}')
        while True:
            # Вызываем функцию плавной прокрутки страницы
            await scroll_gradually(page)
            
            # Проверяем, есть ли элементы с data-nm-id равным заданному id
            element = await page.query_selector(f'[data-nm-id="{id}"]')

            # Если элементы найдены, вызываем функцию взаимодействия с элементом и завершаем цикл
            if element:
                print(f'-------> Найден товар с артикулом {id}, страница {page_number}')
                return element  # Возвращаем найденный элемент
                break

            # В противном случае проверяем наличие кнопки "Следующая страница"
            next_page_button = await page.query_selector('a.pagination-next.pagination__next.j-next-page')

            # Проверяем наличие текста "Следующая страница"
            next_page_text = await page.query_selector('a.pagination-next.pagination__next.j-next-page:has-text("Следующая страница")')

            # Если есть кнопка "Следующая страница", кликаем на нее и ждем следующей страницы
            if next_page_button or next_page_text:
                page_number += 1  # Увеличиваем номер страницы
                print(f'-------> Переходим на следующую страницу {page_number}')
                await page.click('a.pagination-next.pagination__next.j-next-page')
                await asyncio.sleep(5)
            else:
                print('-------> Нет следующей страницы, завершаем поиск')
                break

    except Exception as e:
        print(f"-------> Произошла ошибка при поиске: {str(e)}")

# Асинхронная функция для взаимодействия с найденным элементом (например, клик)
async def element_open(element):
    try:
        await element.click() 
        print('-------> Открыта карточка товара')

    except Exception as e:
        print(f"-------> Произошла ошибка при открытии карточки товара: {str(e)}")

async def move_mouse_randomly(page):
    try:
        viewport_size = await page.evaluate('''() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        }''')

        # Определите диапазон для случайного перемещения мыши
        min_x = 0
        max_x = viewport_size['width']
        min_y = 0
        max_y = viewport_size['height']

        while True:
            # Генерируйте случайные координаты в пределах видимой области
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)

            # Переместите мышь в случайные координаты
            await page.mouse.move(x, y)
            print('-------> Рандомно подвигали мышкой')

            # Подождите случайное количество времени (например, от 1 до 5 секунд)
            await asyncio.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"-------> Произошла ошибка при перемещении мыши: {str(e)}")

async def element_interact(page):
    try:
        print('-------> Начало взаимодействия с карточкой товара')

        timeout = 30
        # Установите время начала взаимодействия
        end_time = time.time() + 30

        async def interaction_actions():
            await page.evaluate("window.scrollBy(0, 300)")

            await page.get_by_text("Развернуть характеристики").click()
            print('-------> Развернули характеристики товара')
            await page.get_by_text("Свернуть характеристики").click()
            print('-------> Свернули характеристики товара')

            await page.get_by_text("Развернуть описание").click()
            print('-------> Развернули описание товара')
            await page.get_by_text("Свернуть описание").click()
            print('-------> Свернули описание товара')

            await page.evaluate("window.scrollBy(300, 0)")
            await move_mouse_randomly(page)

        await asyncio.wait_for(interaction_actions(), timeout=timeout)

    except asyncio.TimeoutError:
        print('-------> Прошло 30 секунд. Взаимодействие с карточкой товара завершено.')
        pass

    except Exception as e:
        print(f"-------> Произошла ошибка в эмуляции интерактива на карточке товара: {str(e)}")

async def add_to_cart(page): 
    try:
        ul_class = "sizes-list"

        # first_li = page.locator(f".{ul_class} li").first()
        # await first_li.click()

        await page.locator("div.product-page__sizes-wrap ul.sizes-list>li:first-of-type").click()
        print('-------> Выбрали размер.')

        await page.click('span:text("Добавить в корзину")')
        print('-------> Добавили товар в корзину.')

    except Exception as e:
        print(f"-------> Произошла ошибка при взаимодействии с карточкой товара: {str(e)}")

# Главная асинхронная функция
async def main():
    async with async_playwright() as playwright:
        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Загрузим страницу
            await load_page(page)

            # Взаимодействуем со страницей
            await type_search(page)

            # Ищем элемент с заданным артикулом
            found_element = await find_element(page, "82097325")

            if found_element:
                # Вызовем функцию element_open с найденным элементом
                await element_open(found_element)

                await element_interact(page)
                
                await add_to_cart(page)
            
        finally:
            # Приостановим страницу перед закрытием браузера
            await page.pause()
            
            await browser.close()
            print('-------> Работа скрипта завершена.')

asyncio.run(main())