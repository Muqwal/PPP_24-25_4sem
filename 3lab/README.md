# 1. Запуск компонентов системы
В разных терминалах выполнить следующие команды:

    1.1. Установка зависимостей
    pip install -r requirements.txt
        --> успешное скачивание без ошибок
    
    1.2. Запуск Redis
    redis-server --port 6380
        --> [21000] 03 Jun 20:49:33.465 # Server started, Redis version 3.0.504
            [21000] 03 Jun 20:49:33.465 * The server is now ready to accept connections on port 6380
    
    1.3. Проверка Redis
    redis-cli -p 6380 ping
        --> PONG
    
    1.4. Запуск Celery worker
    celery -A app.celery.tasks worker -l info --pool=solo
        --> [2025-06-03 20:49:40,564: INFO/MainProcess] celery@LAPTOP-ILMTQP88 ready.

    1.5. Запуск FastAPI сервера
    uvicorn main:app --reload
        --> INFO:     Waiting for application startup.
            INFO:     Application startup complete.

    1.6. Запуск клиента
    python client.py interactive
        --> Enter your user ID:

# 2. Тестирование функциональности

    2.1. Кодирование данных
    
        2.1.1. При запросе ID пользователя введите:
            Enter your user ID: user123

        2.1.2. В меню выберите опцию 1:
            Available commands:
            1. Encode data
            2. Decode data
            3. Exit
            Enter your choice (1-3): 1

        2.1.3. Введите тестовый текст:
            Enter data to encode: Hello, World!
            --> Starting encoding task 79ea2de4-241f-4e97-bd7d-aa35e274906b
                Encoding:   0%|                                                                                  | 0/100 [00:05<?, ?it/s]

                Encoding result:
                Encoded data: gr6nPaNA
                Huffman codes: {
                "d": "000",
                "e": "001",
                "l": "01",
                "H": "1000",
                " ": "1001",
                ",": "1010",
                "r": "1011",
                "W": "1100",
                "!": "1101",
                "o": "111"
                }
                Padding: 6

    2.2. Декодирование данных

        2.2.1. В меню выберите опцию 2:
            Available commands:
            1. Encode data
            2. Decode data
            3. Exit
            Enter your choice (1-3): 2

        2.2.2. Введите данные из предыдущего шага:
            Enter encoded data: gr6nPaNA
            Enter Huffman codes (as JSON): {"d": "000", "e": "001", "l": "01", "H": "1000", " ": "1001", ",": "1010", "r": "1011", "W": "1100", "!": "1101", "o": "111"}
            Enter padding: 6
            --> Starting decoding task fc567d5c-3d9d-4bee-ac84-60dc89e027f3
                Decoding:   0%|                                                                                  | 0/100 [00:05<?, ?it/s] 

                Decoded result:
                Hello, World!

# 3. Проверка параллельной обработки

    3.1. Откройте еще один терминал и запустите второй клиент:
    python client.py interactive

    3.2. Используйте другой ID пользователя:
    Enter your user ID: user456

    3.3. Запустите операции кодирования одновременно в обоих клиентах