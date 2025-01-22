from config.data_classes import Config
from config.data_classes import Order

class GosZakupAutomation:
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.page = None

    def process_order(self, order: Order):
        """Обработка одного заказа"""
        try:
            self.navigate_to_order(order.number)
            self.sign_participation_application()
            self.sign_goods_list()
            self.sign_technical_spec(order.lots_count)
            self.copy_qualification_data()
            self.submit_application()
        except Exception as e:
            print(f"Error processing order {order.number}: {str(e)}")
            # Можно добавить логирование ошибки

    def navigate_to_order(self, order_number: str):
        """Переход на страницу заказа"""
        url = f"{self.config.base_url}/order/{order_number}"
        self.page.goto(url)
        # Добавить проверку загрузки страницы

    # ... остальные методы класса GosZakupAutomation ...