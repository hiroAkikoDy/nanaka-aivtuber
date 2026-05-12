"""
YouTube Live コメント取得エージェント

YouTube Data API v3を使用してリアルタイムコメントを取得し、
重複排除と処理状態の管理を行う。
"""

import os
import time
from typing import Optional, List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yaml


class YouTubeAgent:
    """YouTube Live コメント取得エージェント"""

    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.youtube_config = self.config.get("youtube", {})

        self.credentials_path = self.youtube_config.get("credentials_path", "credentials/client_secret.json")
        self.token_path = self.youtube_config.get("token_path", "credentials/token.json")

        self.youtube = None

        self.video_id = self.youtube_config.get("video_id")
        self.live_chat_id = None

        self.polling_interval = self.youtube_config.get("polling_interval", 5)
        self.max_results = self.youtube_config.get("max_results", 10)

        self.processed_comment_ids = set()

        self.next_page_token = None

        self.quota_used = 0
        self.quota_limit = self.youtube_config.get("quota_limit_per_day", 10000)
        self.quota_warning_threshold = self.youtube_config.get("quota_warning_threshold", 8000)

    def authenticate(self):
        """OAuth 2.0 認証を実行"""
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self.youtube = build("youtube", "v3", credentials=creds)
        print("[YouTubeAgent] 認証完了")

    def get_live_chat_id(self, video_id: Optional[str] = None) -> Optional[str]:
        """
        配信のライブチャットIDを取得

        Args:
            video_id: 動画ID（Noneの場合は自動検出）

        Returns:
            str: ライブチャットID
        """
        if video_id is None:
            video_id = self._get_active_live_video_id()
            if video_id is None:
                print("[YouTubeAgent] アクティブな配信が見つかりません")
                return None

        try:
            request = self.youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            )
            response = request.execute()
            self._update_quota(1)

            if response["items"]:
                live_chat_id = response["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
                print(f"[YouTubeAgent] ライブチャットID取得: {live_chat_id}")
                return live_chat_id
            else:
                print(f"[YouTubeAgent] 動画ID {video_id} が見つかりません")
                return None

        except HttpError as e:
            print(f"[YouTubeAgent] エラー: {e}")
            return None

    def _get_active_live_video_id(self) -> Optional[str]:
        """
        現在アクティブな配信の動画IDを自動検出

        Returns:
            str: 動画ID
        """
        try:
            request = self.youtube.liveBroadcasts().list(
                part="id,snippet",
                broadcastStatus="active",
                maxResults=1
            )
            response = request.execute()
            self._update_quota(1)

            if response["items"]:
                video_id = response["items"][0]["id"]
                title = response["items"][0]["snippet"]["title"]
                print(f"[YouTubeAgent] アクティブな配信検出: {title} (ID: {video_id})")
                return video_id
            else:
                return None

        except HttpError as e:
            print(f"[YouTubeAgent] エラー: {e}")
            return None

    def fetch_comments(self) -> List[Dict[str, str]]:
        """
        ライブチャットからコメントを取得

        Returns:
            list[dict]: [
                {"author": "ユーザー名", "text": "コメント内容", "id": "コメントID"},
                ...
            ]
        """
        if self.youtube is None:
            print("[YouTubeAgent] 認証が必要です。先にauthenticate()を実行してください")
            return []

        if self.live_chat_id is None:
            print("[YouTubeAgent] ライブチャットIDが設定されていません")
            return []

        try:
            request = self.youtube.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                maxResults=self.max_results,
                pageToken=self.next_page_token
            )
            response = request.execute()
            self._update_quota(5)

            self.next_page_token = response.get("nextPageToken")
            polling_interval_ms = response.get("pollingIntervalMillis", self.polling_interval * 1000)

            new_comments = []
            for item in response.get("items", []):
                comment_id = item["id"]

                if comment_id in self.processed_comment_ids:
                    continue

                author = item["authorDetails"]["displayName"]
                text = item["snippet"]["displayMessage"]

                new_comments.append({
                    "author": author,
                    "text": text,
                    "id": comment_id
                })

                self.processed_comment_ids.add(comment_id)

            return new_comments

        except HttpError as e:
            print(f"[YouTubeAgent] エラー: {e}")
            return []

    def _update_quota(self, units: int):
        """
        API クォータ使用量を更新

        Args:
            units: 消費したユニット数
        """
        self.quota_used += units

        if self.quota_used >= self.quota_warning_threshold:
            print(f"[YouTubeAgent] 警告: クォータ使用量 {self.quota_used}/{self.quota_limit}")

        if self.quota_used >= self.quota_limit:
            print(f"[YouTubeAgent] エラー: クォータ上限に達しました ({self.quota_used}/{self.quota_limit})")

    def start_monitoring(self, video_id: Optional[str] = None):
        """
        配信モニタリングを開始

        Args:
            video_id: 動画ID（Noneの場合は自動検出）
        """
        self.authenticate()

        self.live_chat_id = self.get_live_chat_id(video_id)

        if self.live_chat_id is None:
            print("[YouTubeAgent] モニタリングを開始できません")
            return

        print(f"[YouTubeAgent] モニタリング開始（ポーリング間隔: {self.polling_interval}秒）")


if __name__ == "__main__":
    agent = YouTubeAgent()

    agent.start_monitoring()

    for i in range(10):
        print(f"\n=== ポーリング {i+1} ===")
        comments = agent.fetch_comments()

        if comments:
            for comment in comments:
                print(f"[{comment['author']}] {comment['text']}")
        else:
            print("新しいコメントなし")

        time.sleep(agent.polling_interval)
