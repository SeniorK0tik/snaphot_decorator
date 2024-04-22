# Requirements
Поддерживает только оборачивание асинхронных функций

# Installation
`poetry add git+https://github.com/SeniorK0tik/snaphot_decorator.git`

# Examples
```python
# Директория куда будут складываться снепшоты
_snapshot_dir = os.path.join(PROJECT_DIR, "package_name", "snapshots", "exchange_client")
# Объект таймера ответственный за одну конкретную функцию
_sn_timer = SnapShotTimer(timeout=1800)
```
### Асинхронная функция
```python
@snapshot(
    dirpath=_snapshot_dir,
    snapshot_timer=_sn_timer,
    max_files_count=5
)
async def main():
    return {"KOTIK": "BARON"}
```
- Каждые 30 мин после запуска будет производиться снепшот результатов в виде json локально
- Максимальное количество файлов 5. После достижения максимального количества. Самый старый файл в каталоге будет заменен новым.

