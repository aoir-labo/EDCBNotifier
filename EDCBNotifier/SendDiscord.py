import io
import json
import os
import requests

class Discord:
    """
    Discord の Webhook でメッセージを送信するクラス (EDCBNotifier魔改造版)
    """

    def __init__(self, webhook_url:str):
        self.webhook_url = webhook_url

    def sendMessage(self, message:str, image_path:str=None) -> dict:
        # メッセージを改行で分割（空行除外）
        lines = [l.strip() for l in message.split('\n') if l.strip()]
        
        # 1行目をタイトルに、残りを本文にする
        title = lines[0] if len(lines) > 0 else "Notification"
        body_lines = lines[1:] if len(lines) > 1 else []
        
        # 本文の整形：全角スペースを半角に置換して（ＫＥＹ　ＴＯ　ＬＩＴ）等の改行崩れを防止
        description = "\n".join(body_lines).replace("　", " ")

        # 状態に合わせて色を変更
        # 赤色: 開始(START), 追加(ADD), 変更(CHG) / 青色: 終了(END), 通知(Notify)
        embed_color = 0x3498db # デフォルトは青
        if any(keyword in title for keyword in ["START", "ADD", "CHG"]):
            embed_color = 0xe74c3c # 赤

        embed = {
            "title": title,
            "description": description,
            "color": embed_color,
            "footer": {"text": "tsdump notifier"}
        }

        # アイコン（アバター）の設定
        avatar_url = 'https://raw.githubusercontent.com/tsukumijima/EDCBNotifier/master/EDCBNotifier/EDCBNotifier.png'

        if image_path is not None and os.path.isfile(image_path):
            payload = {
                'username': 'EDCBNotifier魔改造版',
                'avatar_url': avatar_url,
                'embeds': [embed],
                'attachments': [{'id': 0, 'filename': os.path.basename(image_path)}]
            }
            payload['embeds'][0]['image'] = {'url': f'attachment://{os.path.basename(image_path)}'}
            
            files = {
                'payload_json': ('', io.BytesIO(json.dumps(payload).encode('utf-8')), 'application/json'),
                'files[0]': (os.path.basename(image_path), open(image_path, 'rb')),
            }
            response = requests.post(self.webhook_url, files=files)
        else:
            payload = {
                'username': 'EDCBNotifier魔改造版',
                'avatar_url': avatar_url,
                'embeds': [embed]
            }
            response = requests.post(self.webhook_url, json=payload)

        if response.status_code not in [200, 204]:
            try:
                err = response.json().get('message', 'Unknown Error')
            except:
                err = response.text
            return {'status': False, 'message': f"Discord Error: {err}"}
        
        return {'status': True, 'message': 'Success'}