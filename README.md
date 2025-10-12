上传文件 Post -> http://localhost:8000/api/v1/projects/upload 
{
    "id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
    "name": "guanshui",
    "description": "Video: guanshui.mp4, Subtitle: Whisper自动生成",
    "project_type": "knowledge",
    "status": "pending",
    "source_url": null,
    "source_file": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
    "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
    "thumbnail": null,
    "settings": {
        "video_category": "default",
        "video_file": "guanshui.mp4",
        "srt_file": "Whisper自动生成"
    },
    "created_at": "2025-10-12T15:49:20.494717",
    "updated_at": "2025-10-12T15:49:20.796681",
    "completed_at": null,
    "total_clips": 0,
    "total_collections": 0,
    "total_tasks": 0,
    "clips": null,
    "collections": null
}

get : http://localhost:8000/api/v1/projects/
{
    "items": [
        {
            "id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "name": "guanshui",
            "description": "Video: guanshui.mp4, Subtitle: Whisper自动生成",
            "project_type": "knowledge",
            "status": "pending",
            "source_url": null,
            "source_file": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
            "thumbnail": "data:image/jpeg;base64,",
            "settings": {
                "video_category": "default",
                "video_file": "guanshui.mp4",
                "srt_file": "Whisper自动生成"
            },
            "created_at": "2025-10-12T23:49:20.494717+08:00",
            "updated_at": "2025-10-12T23:49:20.796681+08:00",
            "completed_at": null,
            "total_clips": 0,
            "total_collections": 0,
            "total_tasks": 0,
            "clips": null,
            "collections": null
        }
    ],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 1,
        "pages": 1,
        "has_next": false,
        "has_prev": false
    }
}


GET -> http://localhost:8000/api/v1/simple-progress/snapshot?project_ids=b738965b-8619-4e12-a4bc-6a730ae8e540
[
    {
        "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
        "stage": "SUBTITLE",
        "percent": 10,
        "message": "开始字幕处理",
        "ts": 1760284190
    }
]

GET -> http://localhost:8000/api/v1/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/logs?lines=20
{
    "logs": [
        {
            "timestamp": "2025-08-01T13:30:00.000Z",
            "module": "processing",
            "level": "INFO",
            "message": "开始处理项目"
        },
        {
            "timestamp": "2025-08-01T13:30:05.000Z",
            "module": "processing",
            "level": "INFO",
            "message": "Step 1: 提取大纲完成"
        },
        {
            "timestamp": "2025-08-01T13:30:10.000Z",
            "module": "processing",
            "level": "INFO",
            "message": "Step 2: 时间定位完成"
        },
        {
            "timestamp": "2025-08-01T13:30:15.000Z",
            "module": "processing",
            "level": "INFO",
            "message": "Step 3: 内容评分进行中..."
        }
    ]
}

GET -> http://localhost:8000/api/v1/simple-progress/snapshot?project_ids=b738965b-8619-4e12-a4bc-6a730ae8e540
请求进度：
[
    {
        "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
        "stage": "DONE",
        "percent": 100,
        "message": "处理完成",
        "ts": 1760284321
    }
]


GET -> http://localhost:8000/api/v1/projects/
请求所有项目
{
    "items": [
        {
            "id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "name": "guanshui",
            "description": "Video: guanshui.mp4, Subtitle: Whisper自动生成",
            "project_type": "knowledge",
            "status": "completed",
            "source_url": null,
            "source_file": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
            "thumbnail": "data:image/jpeg;base64,/9j",
            "settings": {
                "video_category": "default",
                "video_file": "guanshui.mp4",
                "srt_file": "Whisper自动生成"
            },
            "created_at": "2025-10-12T23:49:20.494717+08:00",
            "updated_at": "2025-10-12T23:52:01.333609+08:00",
            "completed_at": "2025-10-12T23:52:01.333122+08:00",
            "total_clips": 5,
            "total_collections": 1,
            "total_tasks": 1,
            "clips": null,
            "collections": null
        }
    ],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 1,
        "pages": 1,
        "has_next": false,
        "has_prev": false
    }

GET: -> http://localhost:8000/api/v1/projects/b738965b-8619-4e12-a4bc-6a730ae8e540
查看某个项目
{
    "id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
    "name": "guanshui",
    "description": "Video: guanshui.mp4, Subtitle: Whisper自动生成",
    "project_type": "knowledge",
    "status": "completed",
    "source_url": null,
    "source_file": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
    "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/raw/input.mp4",
    "thumbnail": "data:image/jpeg;base64,/9j",
    "settings": {
        "video_category": "default",
        "video_file": "guanshui.mp4",
        "srt_file": "Whisper自动生成"
    },
    "created_at": "2025-10-12T23:49:20.494717+08:00",
    "updated_at": "2025-10-12T23:52:01.333609+08:00",
    "completed_at": "2025-10-12T23:52:01.333122+08:00",
    "total_clips": 5,
    "total_collections": 1,
    "total_tasks": 1,
    "clips": null,
    "collections": null
}

GET -> http://localhost:8000/api/v1/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/status
{
    "task_id": "cc64a4fd-1be0-42d7-880a-cd57cf88ebd5",
    "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
    "task_status": "completed",
    "task_progress": 100.0,
    "current_step": "初始化",
    "error_message": null,
    "created_at": "2025-10-12T15:49:50.255816",
    "updated_at": "2025-10-12T15:52:01.333991"
}

GET: -> http://localhost:8000/api/v1/clips/?project_id=b738965b-8619-4e12-a4bc-6a730ae8e540
{
    "items": [
        {
            "id": "e34c68ee-e2a5-4928-90b5-a8e54e22c85f",
            "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "title": "企鹅跳海逃关税？这个荒诞寓言揭穿了国际贸易博弈的潜规则",
            "description": "用荒诞寓言解构严肃议题，创意十足，金句频出，极具传播爆点。",
            "start_time": 77,
            "end_time": 139,
            "duration": 62,
            "score": 0.95,
            "status": "completed",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/1_片段_1.mp4",
            "tags": [],
            "clip_metadata": {
                "id": "1",
                "outline": {
                    "title": "开场隐喻与关税博弈的象征性讨论",
                    "subtopics": [
                        "以“企鹅逃税”寓言引入对国际贸易摩擦的讽刺性解读",
                        "通过虚构对话揭示双方在关税加征问题上的心理博弈与策略对抗",
                        "强调“不按套路出牌”的非常规手段在国际谈判中的运用"
                    ]
                },
                "content": [
                    "以每小时八十迈的速度奔向海边",
                    "咣当跳海里跑了全跑了呀",
                    "这企鹅的环境是不是被破坏",
                    "绝对都是原生态的",
                    "会不会有什么人捕杀他们",
                    "这是个无人小岛",
                    "那怎么全跑了呢",
                    "那群企鹅不想交关税的哦",
                    "我说你这个人不讲究啊",
                    "你不按套路出牌呀",
                    "无人小岛你也加征关税呀",
                    "那既然这样的话",
                    "我也咨询个问题",
                    "你说这两年我心心念念看上一块地地主",
                    "就是不愿意让给我",
                    "你说我是明着抢呢",
                    "还是暗着来呢",
                    "给你们两个机会",
                    "明着抢",
                    "明月抢",
                    "恭喜你答对了",
                    "大毛也是这么想的"
                ],
                "start_time": "00:01:17,870",
                "end_time": "00:02:19,430",
                "chunk_index": 0,
                "final_score": 0.95,
                "recommend_reason": "用荒诞寓言解构严肃议题，创意十足，金句频出，极具传播爆点。",
                "generated_title": "企鹅跳海逃关税？这个荒诞寓言揭穿了国际贸易博弈的潜规则",
                "clip_metadata": {
                    "actual_duration_seconds": 64.459
                },
                "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/1_片段_1.mp4"
            },
            "created_at": "2025-10-12T15:52:01.258893",
            "updated_at": "2025-10-12T15:52:01.258898",
            "collection_ids": []
        },
        {
            "id": "6c660702-53ec-43bb-9736-c69114982580",
            "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "title": "从忍气吞声到两头开怼，大国崛起背后的地缘焦虑有多深？",
            "description": "洞察深刻，战略视角宏大，揭示大国博弈背后的权力焦虑与连锁反应。",
            "start_time": 139,
            "end_time": 168,
            "duration": 29,
            "score": 0.86,
            "status": "completed",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/2_片段_2.mp4",
            "tags": [],
            "clip_metadata": {
                "id": "2",
                "outline": {
                    "title": "地缘政治竞争与强国战略转变",
                    "subtopics": [
                        "分析某大国从“韬光养晦”到“两头怼人”的外交姿态演变",
                        "讨论对特定地区（如格林兰岛）的战略意图受阻及其背后权力博弈",
                        "指出当前国际格局中“老大”地位面临的挑战及小弟阵营的动摇风险"
                    ]
                },
                "content": [
                    "那里黑暗大哥安排来",
                    "好",
                    "那格林兰岛就没戏了",
                    "看见没",
                    "他已经从当年的一直忍",
                    "现在成长到两头怼了大哥",
                    "他太厉害了",
                    "咱放弃吧",
                    "不能放弃欧洲肌肉贸易学了",
                    "日本广场协议粘了",
                    "这个清明节",
                    "不把它摆平",
                    "小弟们就要跟我这个老大告别了",
                    "好",
                    "你们给弟们照亮",
                    "每个人好看我的眼色行事"
                ],
                "start_time": "00:02:19,430",
                "end_time": "00:02:48,550",
                "chunk_index": 0,
                "final_score": 0.86,
                "recommend_reason": "洞察深刻，战略视角宏大，揭示大国博弈背后的权力焦虑与连锁反应。",
                "generated_title": "从忍气吞声到两头开怼，大国崛起背后的地缘焦虑有多深？",
                "clip_metadata": {
                    "actual_duration_seconds": 30.571
                },
                "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/2_片段_2.mp4"
            },
            "created_at": "2025-10-12T15:52:01.258902",
            "updated_at": "2025-10-12T15:52:01.258903",
            "collection_ids": []
        },
        {
            "id": "292dd989-5e01-4221-9345-96f02288e6c2",
            "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "title": "关税从10%加到104%：一场失控的贸易报复循环是如何形成的？",
            "description": "层层递进，逻辑炸裂，把贸易战讲成一场高智商对决，令人拍案叫绝。",
            "start_time": 168,
            "end_time": 252,
            "duration": 84,
            "score": 0.93,
            "status": "completed",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/3_片段_3.mp4",
            "tags": [],
            "clip_metadata": {
                "id": "3",
                "outline": {
                    "title": "贸易争端升级机制与反制逻辑解析",
                    "subtopics": [
                        "梳理关税层层加码的过程：从初始加税到多次追加至104%的极端情形",
                        "解读“反制”概念的语义争夺与话语权斗争，强调术语使用的政治意义",
                        "揭示谈判破裂后双方陷入报复循环的非理性动态与结构性困境"
                    ]
                },
                "content": [
                    "哎",
                    "哪位",
                    "我是向你忏悔来了",
                    "苦肉计啊",
                    "有小孩小人儿坐不好好使了么个只要我们爱好和平的人对你提高警惕了",
                    "你还会什么啊",
                    "不就会个胡萝卜加打扮嘛",
                    "还自由贸易去封锁科技",
                    "搞霸权主义",
                    "还好自己小弟",
                    "我不陪你玩",
                    "今天我就给你加关税来",
                    "哥",
                    "你太没诚心了",
                    "又搞贸易霸凌这出戏强烈呼吁双方尊重市场规律不行",
                    "全球都加了",
                    "对等关税你怎么能例外呢",
                    "加多少税",
                    "你说吧",
                    "十个点十个点",
                    "我反对",
                    "再加十个点",
                    "我我反对",
                    "再加三十四反制啊",
                    "还变成反制了",
                    "哎哎哎哎哎",
                    "你加的关税",
                    "我对得等反制没有不对啊",
                    "你判错字了啊",
                    "应该是反制反制反制呀",
                    "老兄伸头是一刀",
                    "缩头还是一刀",
                    "对不对",
                    "对不对啊",
                    "这样啊乱了啊",
                    "既然咱哥俩呢谈判有分歧啊",
                    "是吧",
                    "咱们再理一次",
                    "共同确认这关税到底是多少",
                    "刚才多少五十四",
                    "再加五十一百零四",
                    "曾经你真往上加呀",
                    "对警告不要尝试报复",
                    "还是赶紧跪吧"
                ],
                "start_time": "00:02:48,830",
                "end_time": "00:04:12,665",
                "chunk_index": 0,
                "final_score": 0.93,
                "recommend_reason": "层层递进，逻辑炸裂，把贸易战讲成一场高智商对决，令人拍案叫绝。",
                "generated_title": "关税从10%加到104%：一场失控的贸易报复循环是如何形成的？",
                "clip_metadata": {
                    "actual_duration_seconds": 84.684
                },
                "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/3_片段_3.mp4"
            },
            "created_at": "2025-10-12T15:52:01.258914",
            "updated_at": "2025-10-12T15:52:01.258918",
            "collection_ids": []
        },
        {
            "id": "1881fb5d-6c79-4585-869a-6530ed1ed9e2",
            "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "title": "要面子还是要制造业回流？美国谈判底线里的矛盾真相",
            "description": "精准拆解美方话术与策略矛盾，观点犀利，具有强烈现实批判力。",
            "start_time": 253,
            "end_time": 293,
            "duration": 40,
            "score": 0.88,
            "status": "completed",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/4_片段_4.mp4",
            "tags": [],
            "clip_metadata": {
                "id": "4",
                "outline": {
                    "title": "美国制造业回流目标与谈判条件对峙",
                    "subtopics": [
                        "阐述美方以“让美国再次伟大”为口号推动产业回归的核心诉求",
                        "分析美方将取消反制作为谈判前提的政治姿态与实际操作矛盾",
                        "指出美方使用多重施压手段（安全威胁、外交孤立、科技封锁）的组合策略"
                    ]
                },
                "content": [
                    "那行",
                    "那行",
                    "哎哎别别动",
                    "别动啊",
                    "别动坐下来看个乐子",
                    "老钟按理说不该加关税",
                    "但是我要面子要让美国再次伟大制造业要回流",
                    "但是但是取消反制才能谈判",
                    "这次我继续反制",
                    "从你搞三零零条款",
                    "你分别用了恐吓计危害安全剂外交围堵孤立镜",
                    "这俩跟班搞芯片封锁剂",
                    "我只用了一计",
                    "将计就计送你一计走",
                    "为上计",
                    "不送失败了",
                    "知道因为啥失败吗",
                    "这头狮子现在睡醒了",
                    "要开始练功了"
                ],
                "start_time": "00:04:13,690",
                "end_time": "00:04:53,155",
                "chunk_index": 0,
                "final_score": 0.88,
                "recommend_reason": "精准拆解美方话术与策略矛盾，观点犀利，具有强烈现实批判力。",
                "generated_title": "要面子还是要制造业回流？美国谈判底线里的矛盾真相",
                "clip_metadata": {
                    "actual_duration_seconds": 41.193
                },
                "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/4_片段_4.mp4"
            },
            "created_at": "2025-10-12T15:52:01.258923",
            "updated_at": "2025-10-12T15:52:01.258924",
            "collection_ids": []
        },
        {
            "id": "65d88ad6-80b9-4590-9504-c5504ba7cf25",
            "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "title": "红包与挽联齐飞，这场贸易战里的心理战你听懂了吗？",
            "description": "心理战+文化梗双杀，幽默中见锋芒，堪称舆论反击的教科书级操作。",
            "start_time": 294,
            "end_time": 350,
            "duration": 56,
            "score": 0.96,
            "status": "completed",
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/5_片段_5.mp4",
            "tags": [],
            "clip_metadata": {
                "id": "5",
                "outline": {
                    "title": "中国应对策略与反制手段的效果评估",
                    "subtopics": [
                        "总结中方采取“将计就计”与“反间计”等传统谋略在现代贸易战中的应用",
                        "回应关于美股暴跌与全球市场联动的问题，提出“关税周期可控”的观点",
                        "强调中方技高一筹的心理战优势，并以“挽联”“红包”等符号完成话语反击"
                    ]
                },
                "content": [
                    "吃",
                    "嗯",
                    "大客请松手啊",
                    "来",
                    "哎呀哎呀",
                    "妈呀呀呀呀呀呀呀呀呀呀",
                    "这个世界太疯狂了吧",
                    "后头都被猫当伴娘了",
                    "好吧",
                    "一人一个红包拿好呀呀呀呀呀呀呀呀呀呀呀呀呀呀",
                    "哎呀呀",
                    "哎呀",
                    "师傅拿下反间计防不胜防啊",
                    "可是大麻咖我不明白你霸权来霸权去美股",
                    "它不也暴跌吗",
                    "一起下跌",
                    "这就是为你定做的关税周期随时可以加长",
                    "哎",
                    "为了我",
                    "你是煞费苦心心",
                    "嗯",
                    "多亏我技高一筹",
                    "打开红包",
                    "清明节送你一副挽联儿",
                    "你加税",
                    "我奉陪缘分哪不作死",
                    "不会死",
                    "第二首"
                ],
                "start_time": "00:04:54,370",
                "end_time": "00:05:50,725",
                "chunk_index": 0,
                "final_score": 0.96,
                "recommend_reason": "心理战+文化梗双杀，幽默中见锋芒，堪称舆论反击的教科书级操作。",
                "generated_title": "红包与挽联齐飞，这场贸易战里的心理战你听懂了吗？",
                "clip_metadata": {
                    "actual_duration_seconds": 56.75
                },
                "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/clips/5_片段_5.mp4"
            },
            "created_at": "2025-10-12T15:52:01.258926",
            "updated_at": "2025-10-12T15:52:01.258927",
            "collection_ids": []
        }
    ],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 5,
        "pages": 1,
        "has_next": false,
        "has_prev": false
    }
}

GET: -> http://localhost:8000/api/v1/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/clips/65d88ad6-80b9-4590-9504-c5504ba7cf25
GET: -> http://localhost:8000/api/v1/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/clips/292dd989-5e01-4221-9345-96f02288e6c2
GET: -> http://localhost:8000/api/v1/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/clips/e34c68ee-e2a5-4928-90b5-a8e54e22c85f

GET -> http://localhost:8000/api/v1/collections/?project_id=b738965b-8619-4e12-a4bc-6a730ae8e540
{
    "items": [
        {
            "id": "a95b4365-4936-46a8-b7c0-e1eb3ddd7a50",
            "project_id": "b738965b-8619-4e12-a4bc-6a730ae8e540",
            "name": "精选高分片段",
            "description": "评分最高的精彩片段合集",
            "theme": null,
            "status": "completed",
            "tags": [],
            "metadata": {
                "clip_ids": [
                    "e34c68ee-e2a5-4928-90b5-a8e54e22c85f",
                    "6c660702-53ec-43bb-9736-c69114982580",
                    "292dd989-5e01-4221-9345-96f02288e6c2",
                    "1881fb5d-6c79-4585-869a-6530ed1ed9e2",
                    "65d88ad6-80b9-4590-9504-c5504ba7cf25"
                ],
                "original_clip_ids": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5"
                ],
                "collection_type": "ai_recommended",
                "original_id": "1"
            },
            "video_path": "/home/zhanglingwen/business_conda/data/projects/b738965b-8619-4e12-a4bc-6a730ae8e540/output/collections/精选高分片段.mp4",
            "thumbnail_path": null,
            "created_at": "2025-10-12T15:52:01.274630",
            "updated_at": "2025-10-12T15:52:01.274634",
            "total_clips": 0,
            "clip_ids": [
                "e34c68ee-e2a5-4928-90b5-a8e54e22c85f",
                "6c660702-53ec-43bb-9736-c69114982580",
                "292dd989-5e01-4221-9345-96f02288e6c2",
                "1881fb5d-6c79-4585-869a-6530ed1ed9e2",
                "65d88ad6-80b9-4590-9504-c5504ba7cf25"
            ]
        }
    ],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 1,
        "pages": 1,
        "has_next": false,
        "has_prev": false
    }
}
