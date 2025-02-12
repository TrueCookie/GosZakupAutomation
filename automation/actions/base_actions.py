class BaseActions:
    def __init__(self, page):
        self.page = page

    async def wait_and_click(self, selector: str, timeout=60*5):
        await self.page.wait_for_selector(selector, timeout)
        await self.page.click(selector)

    async def wait_and_fill(self, selector: str, text: str, timeout=60*5):
        await self.page.wait_for_selector(selector, timeout)
        await self.page.fill(selector, text)