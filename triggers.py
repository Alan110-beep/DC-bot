# triggers.py

TRIGGERS = [
    # (觸發字, 回覆內容/類型, 分組, 是否顯示在help, help說明)
    # === 互動回覆 ===
    ("抽", "omikuji", "互動回覆", True, "抽御神籤"),
    ("笑話", "joke", "互動回覆", True, "隨機冷笑話"),
    ("再來一個笑話", "joke", "互動回覆", True, "再聽一個笑話"),
    ("冷笑話", "joke", "互動回覆", True, "冷笑話"),
    ("早安", "greet_morning", "互動回覆", True, "早安問候"),
    ("午安", "greet_noon", "互動回覆", True, "午安問候"),
    ("晚安", "greet_night", "互動回覆", True, "晚安問候"),
    ("安安", "greet_anan", "互動回覆", True, "安安打招呼"),
    ("吃飯了嗎", "eat_remind", "互動回覆", True, "吃飯提醒"),
    ("喝水了嗎", "drink_remind", "互動回覆", True, "喝水提醒"),
    ("貼貼", "hug_sticker", "互動回覆", True, "貼貼貼心一下"),
    ("抱抱", "hug", "互動回覆", True, "給你一個抱抱"),
    ("拍拍", "pat", "互動回覆", True, "溫柔拍拍"),
    ("安慰我", "comfort", "互動回覆", True, "給你安慰鼓勵"),
    ("嗆我", "taunt", "互動回覆", True, "善意小嗆爆"),
    ("加油", "cheer", "互動回覆", True, "給你打氣鼓勵"),
    ("讚美我", "praise", "互動回覆", True, "隨機一句讚美"),
    ("罵我", "scold", "互動回覆", True, "善意罵醒你"),
    ("哭哭", "cry", "互動回覆", True, "可愛哭哭安慰"),
    ("生氣", "angry", "互動回覆", True, "逗趣哄哄你"),
    # === 趣味互動 ===
    ("真心話", "truth", "互動回覆", True, "真心話小遊戲"),
    ("大冒險", "dare", "互動回覆", True, "大冒險小遊戲"),
    ("骰子", "dice", "互動回覆", True, "擲骰子"),
    ("猜數字", "guess_number", "互動回覆", True, "猜一個1~100的數字"),
    ("今日運勢", "fortune", "互動回覆", True, "簡易星座運勢"),
    ("今日幸運色", "lucky_color", "互動回覆", True, "隨機幸運色"),
    # === 彩蛋/隱藏指令（不顯示於help）===
    ("我想中樂透", "easter_lotto", "彩蛋", False, "彩蛋"),
    ("你會說台語嗎", "easter_taiyu", "彩蛋", False, "彩蛋"),
    ("你會唱歌嗎", "easter_sing", "彩蛋", False, "彩蛋"),
    ("你是誰", "easter_who", "彩蛋", False, "彩蛋"),
    ("主人是誰", "easter_master", "彩蛋", False, "彩蛋"),
    ("講一個秘密", "easter_secret", "彩蛋", False, "彩蛋")
]
