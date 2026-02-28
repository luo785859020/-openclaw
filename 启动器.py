import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from config_manager import load_config, save_config
import subprocess
import os
import sys
import requests
import threading
import time

class OpenClawLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenClaw MCP 启动器")
        self.root.geometry("600x500")
        
        self.config = load_config()
        self.process = None
        self.checking_connection = False
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 启动后自动检查连接
        self.root.after(1000, self.check_openclaw_connection)
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="OpenClaw MCP 集成", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)
        
        # 配置框架
        config_frame = ttk.LabelFrame(self.root, text="配置参数")
        config_frame.pack(padx=10, pady=5, fill="x")
        
        # OpenClaw 地址
        ttk.Label(config_frame, text="OpenClaw 地址:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.openclaw_url_entry = ttk.Entry(config_frame, width=40)
        self.openclaw_url_entry.insert(0, self.config.get("OPENCLAW_URL", "http://38.76.206.70:18789"))
        self.openclaw_url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Webhook Token
        ttk.Label(config_frame, text="Webhook Token:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.token_entry = ttk.Entry(config_frame, width=40)
        self.token_entry.insert(0, self.config.get("HOOK_TOKEN", "openclaw123"))
        self.token_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # MCP 接入点（小智服务器地址）
        ttk.Label(config_frame, text="小智MCP接入点:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.mcp_entry = ttk.Entry(config_frame, width=40)
        self.mcp_entry.insert(0, self.config.get("MCP_ENDPOINT", "wss://api.xiaozhi.me/mcp/?token=你的token"))
        self.mcp_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 智谱API（保留）
        ttk.Label(config_frame, text="智谱API密钥:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.zhipu_entry = ttk.Entry(config_frame, width=40)
        self.zhipu_entry.insert(0, self.config.get("ZHIPU_API_KEY", ""))
        self.zhipu_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        self.save_btn = ttk.Button(btn_frame, text="保存配置", command=self.save_config)
        self.save_btn.pack(side="left", padx=5)
        
        self.start_btn = ttk.Button(btn_frame, text="启动服务", command=self.start_service)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止服务", command=self.stop_service, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # 状态框架
        status_frame = ttk.LabelFrame(self.root, text="连接状态")
        status_frame.pack(padx=10, pady=5, fill="x")
        
        self.status_label = tk.Label(status_frame, text="● 未检测", foreground="gray")
        self.status_label.pack(pady=5)
        
        # 日志框架
        log_frame = ttk.LabelFrame(self.root, text="运行日志")
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
        
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        
    def save_config(self):
        """保存配置"""
        new_config = {
            "MCP_ENDPOINT": self.mcp_entry.get().strip(),
            "OPENCLAW_URL": self.openclaw_url_entry.get().strip(),
            "HOOK_TOKEN": self.token_entry.get().strip(),
            "ZHIPU_API_KEY": self.zhipu_entry.get().strip()
        }
        save_config(new_config)
        self.log("配置已保存")
        messagebox.showinfo("保存成功", "配置已保存！")
        
    def check_openclaw_connection(self):
        """检查 OpenClaw 连接"""
        if self.checking_connection:
            return
            
        self.checking_connection = True
        
        def check():
            url = self.openclaw_url_entry.get().strip()
            token = self.token_entry.get().strip()
            
            try:
                response = requests.get(
                    f"{url}/health",
                    timeout=3
                )
                if response.status_code == 200:
                    self.root.after(0, lambda: self.status_label.config(text="● 已连接", foreground="green"))
                    self.root.after(0, lambda: self.log("OpenClaw 连接成功"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="● 连接异常", foreground="orange"))
            except:
                self.root.after(0, lambda: self.status_label.config(text="● 未连接", foreground="gray"))
            
            self.checking_connection = False
            
        threading.Thread(target=check, daemon=True).start()
        
    def start_service(self):
        """启动 MCP 服务"""
        # 先保存配置
        self.save_config()
        
        try:
            self.log("正在启动服务...")
            
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 启动 mcp_pipe.py
            mcp_script = os.path.join(current_dir, "mcp_pipe.py")
            openclaw_script = os.path.join(current_dir, "openclaw_mcp.py")
            
            # 读取配置设置环境变量
            config = load_config()
            env = os.environ.copy()
            env["MCP_ENDPOINT"] = config.get("MCP_ENDPOINT", "")
            
            self.process = subprocess.Popen(
                ["python", mcp_script, openclaw_script],
                cwd=current_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )
            
            # 启动日志读取线程
            threading.Thread(target=self.read_output, daemon=True).start()
            
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.log("服务已启动")
            
            messagebox.showinfo("启动成功", "MCP 服务已启动！")
            
        except Exception as e:
            self.log(f"启动失败: {str(e)}")
            messagebox.showerror("启动失败", str(e))
            
    def read_output(self):
        """读取子进程输出"""
        try:
            for line in self.process.stdout:
                if line.strip():
                    self.root.after(0, lambda l=line.strip(): self.log(l))
        except:
            pass
            
    def stop_service(self):
        """停止服务"""
        if self.process:
            self.process.terminate()
            self.process = None
            self.log("服务已停止")
            
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
    def on_close(self):
        """关闭程序"""
        self.stop_service()
        self.root.destroy()

if __name__ == "__main__":
    app = OpenClawLauncher()
    app.root.mainloop()
