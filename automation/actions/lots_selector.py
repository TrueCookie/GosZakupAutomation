from config.data_classes import Config

class LotSelector:
    def __init__(self, config: Config):
        # ... предыдущий код инициализации ...
        self.config = config
        self.remaining_lots = set(self.config.lots)  # для отслеживания невыбранных лотов
        self.selected_lots = set()  # для отслеживания выбранных лотов

    def should_select_lot(self, lot_number: str) -> bool:
        if self.config.include_all:
            return True
        elif self.config.exclude_lots:
            return lot_number not in self.config.lots
        else:  # include_specific
            return lot_number in self.config.lots

    def mark_lot_processed(self, lot_number: str):
        """Отмечаем лот как обработанный"""
        if not self.config.include_all:
            if self.config.exclude_lots:
                self.selected_lots.add(lot_number)
            else:
                self.remaining_lots.discard(lot_number)

    def has_remaining_lots(self) -> bool:
        """Проверяем, остались ли необработанные лоты"""
        if self.config.include_all or self.config.exclude_lots:
            return True
        return bool(self.remaining_lots)

    def get_selection_mode(self) -> str:
        """Возвращает текущий режим выбора для логирования"""
        if self.config.include_all:
            return "Выбрать все лоты"
        elif self.config.exclude_lots:
            return f"Исключить лоты: {', '.join(sorted(self.config.lots))}"
        else:
            return f"Выбрать лоты: {', '.join(sorted(self.config.lots))}"