import os
import sys
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import time
import urllib.parse
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

LIST_URL = 'https://shiraoka-housedo.com/list/'
BASE_URL = 'https://shiraoka-housedo.com'
IMG_FOLDER = 'images'
CSV_FILE = 'export.csv'
JSON_FILE = 'export.json'
HISTORY_FILE = 'scraping_history.json'  # 取得履歴ファイル

# ユーザーエージェント付き共通ヘッダ
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9",
    "Referer": "https://shiraoka-housedo.com/list/"
}

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("不動産スクレイピングツール v2")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        self.is_running = False
        self.scraped_ids = self.load_history()  # 取得済み物件番号
        self.create_widgets()
        
    def load_history(self):
        """取得履歴を読み込む"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('scraped_ids', []))
            except Exception:
                return set()
        return set()
    
    def save_history(self):
        """取得履歴を保存"""
        try:
            data = {
                'scraped_ids': list(self.scraped_ids),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as ex:
            print(f'履歴保存エラー: {ex}')
        
    def create_widgets(self):
        # タイトル
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🏠 不動産スクレイピングツール v2", 
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # 設定フレーム
        settings_frame = tk.LabelFrame(self.root, text="設定", font=("Arial", 10, "bold"), padx=20, pady=15)
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 取得件数
        items_frame = tk.Frame(settings_frame)
        items_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(items_frame, text="取得件数:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.max_items_var = tk.StringVar(value="15")
        self.max_items_entry = tk.Entry(items_frame, textvariable=self.max_items_var, width=10, font=("Arial", 10))
        self.max_items_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Label(items_frame, text="件（全件取得する場合は大きな数値を入力）", font=("Arial", 9), fg="gray").pack(side=tk.LEFT)
        
        # スキップ設定
        skip_frame = tk.Frame(settings_frame)
        skip_frame.pack(fill=tk.X, pady=5)
        
        self.skip_scraped_var = tk.BooleanVar(value=True)
        self.skip_checkbox = tk.Checkbutton(
            skip_frame,
            text="取得済み物件をスキップする",
            variable=self.skip_scraped_var,
            font=("Arial", 10)
        )
        self.skip_checkbox.pack(side=tk.LEFT)
        
        # 取得済み件数表示
        self.scraped_count_label = tk.Label(
            skip_frame,
            text=f"（取得済み: {len(self.scraped_ids)}件）",
            font=("Arial", 9),
            fg="gray"
        )
        self.scraped_count_label.pack(side=tk.LEFT, padx=10)
        
        # 履歴クリアボタン
        self.clear_history_button = tk.Button(
            skip_frame,
            text="履歴クリア",
            command=self.clear_history,
            font=("Arial", 9),
            bg="#e67e22",
            fg="white",
            cursor="hand2"
        )
        self.clear_history_button.pack(side=tk.LEFT, padx=5)
        
        # URL表示
        url_frame = tk.Frame(settings_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(url_frame, text="対象サイト:", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(url_frame, text=LIST_URL, font=("Arial", 9), fg="blue").pack(side=tk.LEFT, padx=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="スクレイピング開始",
            command=self.start_scraping,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="停止",
            command=self.stop_scraping,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 進捗バー
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = tk.Label(progress_frame, text="待機中...", font=("Arial", 9))
        self.progress_label.pack(pady=5)
        
        # ログ表示
        log_frame = tk.LabelFrame(self.root, text="実行ログ", font=("Arial", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # ステータスバー
        status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="準備完了",
            font=("Arial", 9),
            bg="#34495e",
            fg="white",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def clear_history(self):
        """取得履歴をクリア"""
        if messagebox.askyesno("確認", "取得履歴をクリアしますか？\n次回実行時、すべての物件を再取得します。"):
            self.scraped_ids.clear()
            self.save_history()
            self.scraped_count_label.config(text=f"（取得済み: 0件）")
            self.log("✓ 取得履歴をクリアしました")
            messagebox.showinfo("完了", "取得履歴をクリアしました")
        
    def log(self, message):
        """ログを表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, current, total):
        """進捗バーを更新"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{current}/{total} 件処理中... ({progress:.1f}%)")
        self.root.update_idletasks()
        
    def start_scraping(self):
        """スクレイピング開始"""
        try:
            max_items = int(self.max_items_var.get())
            if max_items <= 0:
                messagebox.showerror("エラー", "取得件数は1以上の数値を入力してください")
                return
        except ValueError:
            messagebox.showerror("エラー", "取得件数は数値で入力してください")
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.max_items_entry.config(state=tk.DISABLED)
        self.skip_checkbox.config(state=tk.DISABLED)
        self.clear_history_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_label.config(text="実行中...")
        
        # 別スレッドで実行
        thread = threading.Thread(target=self.run_scraping, args=(max_items,))
        thread.daemon = True
        thread.start()
        
    def stop_scraping(self):
        """スクレイピング停止"""
        self.is_running = False
        self.log("⚠️ 停止リクエストを受信しました...")
        self.status_label.config(text="停止中...")
        
    def run_scraping(self, max_items):
        """スクレイピング実行"""
        try:
            skip_scraped = self.skip_scraped_var.get()
            
            self.log("=" * 60)
            self.log("🚀 不動産スクレイピング開始")
            if skip_scraped:
                self.log(f"📋 取得済みスキップモード: ON（{len(self.scraped_ids)}件スキップ）")
            else:
                self.log("📋 取得済みスキップモード: OFF（すべて取得）")
            self.log("=" * 60)
            
            # 一覧ページから物件URLを取得
            self.log("📄 一覧ページを取得中...")
            list_soup = self.fetch_list_page()
            detail_urls = self.get_detail_urls(list_soup, max_items)
            
            if not detail_urls:
                self.log("❌ エラー: 物件URLが取得できませんでした")
                self.finish_scraping(False)
                return
            
            self.log(f"✓ {len(detail_urls)}件の物件URLを取得しました\n")
            
            rows = []
            skipped_count = 0
            new_count = 0
            
            for idx, url in enumerate(detail_urls, 1):
                if not self.is_running:
                    self.log("⚠️ ユーザーによって停止されました")
                    break
                
                # 物件番号を抽出（URLから）
                estate_id = url.rstrip('/').split('/')[-1]
                
                # スキップチェック
                if skip_scraped and estate_id in self.scraped_ids:
                    self.log(f"[{idx}/{len(detail_urls)}] ⏭️ スキップ: 物件番号 {estate_id}（取得済み）")
                    skipped_count += 1
                    self.update_progress(idx, len(detail_urls))
                    continue
                
                self.log(f"[{idx}/{len(detail_urls)}] 処理中: {url}")
                self.update_progress(idx - 1, len(detail_urls))
                
                try:
                    # 詳細ページを取得
                    soup = self.fetch_detail_page(url)
                    
                    # 物件情報を抽出
                    d = self.extract_detail(soup, url)
                    
                    # 画像を取得
                    if d['物件番号']:
                        img_urls = self.extract_images(soup, d['物件番号'])
                        d['画像URL'] = ', '.join(img_urls) if img_urls else ''
                        d['画像枚数'] = len(img_urls)
                        
                        # 取得済みリストに追加
                        self.scraped_ids.add(d['物件番号'])
                        new_count += 1
                    else:
                        d['画像URL'] = ''
                        d['画像枚数'] = 0
                    
                    rows.append(d)
                    self.log(f"  ✓ 物件番号 {d['物件番号']} - 画像{d['画像枚数']}枚取得")
                    
                    # アクセス間隔を空ける
                    if idx < len(detail_urls):
                        time.sleep(1)
                    
                except Exception as ex:
                    self.log(f"  ❌ エラー: {ex}")
                    continue
            
            self.update_progress(len(detail_urls), len(detail_urls))
            
            # 履歴を保存
            self.save_history()
            self.scraped_count_label.config(text=f"（取得済み: {len(self.scraped_ids)}件）")
            
            if not rows:
                self.log("\n⚠️ 新規データがありませんでした")
                self.log(f"  スキップ: {skipped_count}件")
                self.finish_scraping(True)
                return
            
            # CSV/JSON出力
            self.log("\n💾 データを出力中...")
            
            # 既存データと結合
            if os.path.exists(CSV_FILE):
                existing_df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
                new_df = pd.DataFrame(rows)
                df = pd.concat([existing_df, new_df], ignore_index=True)
                # 物件番号で重複削除（最新を保持）
                df = df.drop_duplicates(subset=['物件番号'], keep='last')
            else:
                df = pd.DataFrame(rows)
            
            df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
            self.log(f"  ✓ CSV出力完了: {CSV_FILE}")
            
            # JSON出力
            all_data = df.to_dict('records')
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            self.log(f"  ✓ JSON出力完了: {JSON_FILE}")
            
            # 画像フォルダの確認
            if os.path.exists(IMG_FOLDER):
                img_files = os.listdir(IMG_FOLDER)
                self.log(f"  ✓ 画像保存完了: {IMG_FOLDER}/ ({len(img_files)}ファイル)")
            
            self.log("\n" + "=" * 60)
            self.log(f"🎉 完了:")
            self.log(f"  新規取得: {new_count}件")
            self.log(f"  スキップ: {skipped_count}件")
            self.log(f"  合計: {len(df)}件（CSV/JSON）")
            self.log("=" * 60)
            
            self.finish_scraping(True)
            
        except Exception as ex:
            self.log(f"\n❌ エラーが発生しました: {ex}")
            self.finish_scraping(False)
    
    def finish_scraping(self, success):
        """スクレイピング終了処理"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.max_items_entry.config(state=tk.NORMAL)
        self.skip_checkbox.config(state=tk.NORMAL)
        self.clear_history_button.config(state=tk.NORMAL)
        
        if success:
            self.status_label.config(text="完了")
            messagebox.showinfo("完了", "スクレイピングが完了しました！\n\n出力ファイル:\n- export.csv\n- export.json\n- images/")
            
            # 結果フォルダを開く
            if messagebox.askyesno("確認", "結果フォルダを開きますか？"):
                self.open_output_folder()
        else:
            self.status_label.config(text="エラー")
    
    def open_output_folder(self):
        """出力フォルダを開く"""
        try:
            if sys.platform == 'win32':
                os.startfile(os.getcwd())
            elif sys.platform == 'darwin':
                os.system(f'open "{os.getcwd()}"')
            else:
                os.system(f'xdg-open "{os.getcwd()}"')
        except Exception as ex:
            self.log(f"フォルダを開けませんでした: {ex}")
    
    # 以下、スクレイピング関連のメソッド
    
    def fetch_list_page(self):
        res = requests.get(LIST_URL, headers=HEADERS)
        return BeautifulSoup(res.text, 'html.parser')
    
    def get_detail_urls(self, soup, max_items):
        urls = []
        scripts = soup.find_all('script', {'type':'application/ld+json'})
        for script in scripts:
            if 'ItemList' in script.text:
                try:
                    data = json.loads(script.text)
                    for item in data.get('itemListElement', []):
                        url = item.get('item')
                        urls.append(url)
                        if len(urls) >= max_items:
                            break
                except Exception:
                    pass
        return urls
    
    def fetch_detail_page(self, url):
        detail_headers = HEADERS.copy()
        detail_headers["Referer"] = LIST_URL
        res = requests.get(url, headers=detail_headers)
        return BeautifulSoup(res.text, 'html.parser')
    
    def extract_images(self, soup, estate_id):
        img_urls = []
        
        # ギャラリータグから取得
        img_tags = soup.select('a.mainContents_gallery-colorbox')
        
        # preloadタグから取得
        preload_tags = soup.select('link[rel="preload"][as="image"]')
        
        if img_tags:
            for tag in img_tags:
                href = tag.get('href')
                if href:
                    img_urls.append(href)
        elif estate_id and preload_tags:
            for tag in preload_tags:
                href = tag.get('href', '')
                if estate_id in href and 'exterior' in href.lower():
                    img_urls.append(href)
        
        for idx, img_url in enumerate(img_urls):
            img_url = urllib.parse.urljoin(BASE_URL, img_url)
            
            try:
                res = requests.get(img_url, headers=HEADERS, timeout=10)
                
                if res.status_code == 200:
                    img_ext = img_url.split('.')[-1].split('?')[0]
                    if img_ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        img_ext = 'jpg'
                    
                    img_name = f"{estate_id}_{idx+1}.{img_ext}"
                    img_dir = IMG_FOLDER
                    os.makedirs(img_dir, exist_ok=True)
                    
                    img_path = os.path.join(img_dir, img_name)
                    with open(img_path, 'wb') as f:
                        f.write(res.content)
            except Exception:
                pass
            
            time.sleep(0.5)
        
        return [urllib.parse.urljoin(BASE_URL, url) for url in img_urls]
    
    def extract_detail(self, soup, url):
        estate_elem = soup.find('td', class_='estateID')
        estate_id = estate_elem.text.strip() if estate_elem else ''
        
        table = soup.find('table')
        data = {}
        
        if table:
            all_cells = table.find_all(['th', 'td'])
            
            i = 0
            while i < len(all_cells):
                cell = all_cells[i]
                
                if cell.name == 'th':
                    key = cell.text.strip()
                    j = i + 1
                    while j < len(all_cells):
                        next_cell = all_cells[j]
                        if next_cell.name == 'td':
                            value = next_cell.text.strip()
                            data[key] = value
                            i = j
                            break
                        elif next_cell.name == 'th':
                            break
                        j += 1
                
                i += 1
        
        summary = {
            '物件番号': estate_id,
            '価格': data.get('価格', ''),
            '間取り': data.get('間取り', ''),
            '物件種別': data.get('物件種別', ''),
            '所在地': data.get('所在地', ''),
            'アクセス': data.get('アクセス', ''),
            '建物面積': data.get('建物面積', ''),
            '駐車場': data.get('駐車場', ''),
            '築年月': data.get('築年月', ''),
            '建物構造': data.get('建物構造', ''),
            '工法': data.get('工法', ''),
            '主要採光': data.get('主要採光', ''),
            'バルコニー': data.get('バルコニー', ''),
            '保証・評価': data.get('保証・評価', ''),
            'リフォーム': data.get('リフォーム', ''),
            '土地面積': data.get('土地面積', ''),
            '接道': data.get('接道', ''),
            'セットバック': data.get('セットバック', ''),
            '私道': data.get('私道', ''),
            '地目': data.get('地目', ''),
            '地勢': data.get('地勢', ''),
            '権利': data.get('権利', ''),
            '都市計画': data.get('都市計画', ''),
            '用途地域': data.get('用途地域', ''),
            '建ぺい/容積率': data.get('建ぺい/容積率', ''),
            '土地国土法': data.get('土地国土法', ''),
            '許可番号': data.get('許可番号', ''),
            '建築基準法': data.get('建築基準法', ''),
            '法令制限': data.get('法令制限', ''),
            '小学区': data.get('小学区', ''),
            '中学区': data.get('中学区', ''),
            '現況': data.get('現況', ''),
            '引渡': data.get('引渡', ''),
            'その他費用': data.get('その他費用', ''),
            '備考': data.get('備考', ''),
            '取引態様': data.get('取引態様', ''),
            '詳細ページ': url
        }
        return summary


def main():
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

