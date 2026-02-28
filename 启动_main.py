import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import load_config, save_config
import subprocess
import os  
# 在导入部分添加
from tkinter.scrolledtext import ScrolledText

class MCPConfigApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("小智联网查询MCP配置")
        self.config = load_config()
        
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_widgets(self):
        # 配置参数框架
        frame = ttk.LabelFrame(self.root, text="API配置")
        frame.pack(padx=10, pady=10, fill="x")
        
        # MCP端点
        ttk.Label(frame, text="MCP端点:").grid(row=0, column=0, sticky="w")
        self.mcp_entry = ttk.Entry(frame, width=50)
        self.mcp_entry.insert(0, self.config["MCP_ENDPOINT"])
        self.mcp_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # API密钥
        ttk.Label(frame, text="智谱API密钥:").grid(row=1, column=0, sticky="w")
        self.api_entry = ttk.Entry(frame, width=50)
        self.api_entry.insert(0, self.config["ZHIPU_API_KEY"])
        self.api_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 按钮框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="保存配置", command=self.save_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="启动服务", command=self.start_service).pack(side="left", padx=5)
        
        # 新增日志框架
        log_frame = ttk.LabelFrame(self.root, text="操作日志")
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.log_text = ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.log_text.configure(state='disabled')
        
    def save_config(self):
        self.log("正在保存配置...")
        new_config = {
            "MCP_ENDPOINT": self.mcp_entry.get(),
            "ZHIPU_API_KEY": self.api_entry.get()
        }
        save_config(new_config)
        messagebox.showinfo("保存成功", "配置已保存！")
        self.log("配置保存成功")
        
    def start_service(self):
        try:
            self.log("正在启动服务...")
            # 修改为绝对路径执行方式
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_script = os.path.join(current_dir, "mcp_pipe.py")
            web_search_script = os.path.join(current_dir, "联网查询.py")
            subprocess.Popen(["python", mcp_script, web_search_script], cwd=current_dir)
            messagebox.showinfo("启动成功", "服务已在后台运行")
            self.log("服务启动成功")
        except Exception as e:
            self.log(f"服务启动失败: {str(e)}")
            messagebox.showerror("启动失败", str(e))
            
    def on_close(self):
        self.root.destroy()
        
    # 新增日志记录方法
    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

if __name__ == "__main__":
    app = MCPConfigApp()
    app.root.mainloop()