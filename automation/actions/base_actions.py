class BaseActions:
    def __init__(self, page):
        self.page = page

    async def wait_and_click(self, selector: str):
        await self.page.wait_for_selector(selector)
        await self.page.click(selector)

    async def wait_and_fill(self, selector: str, text: str):
        await self.page.wait_for_selector(selector)
        await self.page.fill(selector, text)