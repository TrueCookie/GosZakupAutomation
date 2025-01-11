from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Открываем тестовый сайт
    page.goto('https://demo.playwright.dev/todomvc/')
    
    # Добавляем задачу
    page.fill('.new-todo', 'Изучить Playwright')
    page.keyboard.press('Enter')
    
    # Добавим ещё одну задачу
    page.fill('.new-todo', 'Написать первый скрипт')
    page.keyboard.press('Enter')
    
    # Отметим первую задачу как выполненную
    page.click('.toggle')   
    
    # Пауза для просмотра результата
    page.wait_for_timeout(3000)
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)