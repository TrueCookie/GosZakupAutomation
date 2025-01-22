from playwright.sync_api import sync_playwright

def run(playwright):
    #browser = playwright.chromium.launch(headless=False)
    #page = browser.new_page()
    
    # Проходим авторизацию
    
    # Подключаемся к открытому браузеру
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    default_context = browser.contexts[0]
    page = default_context.pages[0]

    # Print the title of the page.
    print(page.title())

    # Print the URL of the page.
    print(page.url)
    
    # Открываем заявку
    #page.goto('https://v3bl.goszakup.gov.kz/ru/application/docs/13564243/61487249')
    #page.goto('https://v3bl.goszakup.gov.kz/ru/application/docs/13564243/61487249')

    # Открываем документ на подписание
    #page.click('//a[contains(text(), \'Заявка на участие в конкурсе для юридических лиц (Приложение 4)\')]')   
    
    # Нажимаем подписать
    page.click('//span[contains(text(), \'Подписать\')]')   

    # Пауза для просмотра результата
    #page.wait_for_timeout(3000)
    
    # browser.close()

with sync_playwright() as playwright:
    run(playwright)