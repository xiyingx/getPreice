from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import requests
import json
from datetime import datetime  # 用于生成带时间戳的文件名

def fetch_data():
    """发送请求获取数据，组织成字符串并保存为TXT文件"""
    try:
        # 请求参数
        payload = json.dumps({
            "page_index": 1,
            "page_size": 20,
            "task_id": "3870"  # 替换为实际task_id
        })
        headers = {
            "ApiToken": "XJWEQ1P795V5P0S7X7Q9S844",  # 替换为实际令牌
            "Content-Type": "application/json"
        }
        url = "https://api.csqaq.com/api/v1/task/get_task_info"

        print("正在发送请求...")
        response = requests.post(url, headers=headers, data=payload, timeout=45)
        response.raise_for_status()
        data = response.json()

        # 字段映射关系（数字转文字）
        type_mapping = {
            0: "默认库存",
            1: "买入",
            2: "卖出",
            3: "存入",
            4: "取出",
            5: "cd恢复",
            6: "取出/恢复",
            7: "卖出/存入"
        }
        tradable_mapping = {
            0: "禁止",
            1: "允许"
        }

        # 组织字符串内容
        result_str = []
        # 1. 基础响应信息
        result_str.append(f"===== 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
        result_str.append(f"响应状态：{data.get('code')}({data.get('msg')})")
        result_str.append(f"是否本用户创建：{'是' if data['data']['is_user'] else '否'}")
        result_str.append(f"是否已订阅：{'是' if data['data']['is_subscribe'] else '否'}\n")

        # 2. 用户信息
        user_info = data['data']['info'][0] if data['data']['info'] else {}
        result_str.append("=== 用户信息 ===")
        result_str.append(f"Steam名称：{user_info.get('steam_name', '未知')}")
        result_str.append(f"Steam ID：{user_info.get('steam_id', '未知')}")
        result_str.append(f"资产数量：{user_info.get('asset_cnt', 0)}")
        result_str.append(f"最后更新时间：{user_info.get('updated_at', '未知')}\n")
        
        # 3. 库存变动记录
        result_str.append("=== 库存变动记录 ===")
        trades = data['data'].get('trades', [])
        trades = trades[:20]
        if not trades:
            result_str.append("暂无变动记录")
        else:
            for i, trade in enumerate(trades, 1):
                trade_type = type_mapping.get(trade.get('type'), f"未知类型({trade.get('type')})")
                tradable_status = tradable_mapping.get(trade.get('tradable'), "未知状态")
                result_str.append(f"\n第{i}条记录：")
                result_str.append(f"物品名称：{trade.get('market_name', '未知')}")
                result_str.append(f"变动时间：{trade.get('created_at', '未知')}")
                result_str.append(f"数量：{trade.get('count', 0)}")
                result_str.append(f"类型：{trade_type}")
                result_str.append(f"是否可交易：{tradable_status}")
                result_str.append(f"物品ID：{trade.get('good_id', '未知')}")

        # 拼接最终字符串
        final_str = "\n".join(result_str)

        # save_file(final_str)

        return final_str  # 返回字符串供其他使用

    except Exception as e:
        error_msg = f"获取数据失败：{str(e)}"
        print(error_msg)
        # 保存错误信息到文件
        with open(f"错误日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        return error_msg

@register("get", "steam库存监控", "一个简单的steam库存监控插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("get")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        #查询库存
        res = fetch_data()
        yield event.plain_result(f"{res}") # 发送一条纯文本消息

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
