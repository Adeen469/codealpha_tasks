import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  
except Exception:
    pass
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, StringVar
import threading
from datetime import datetime
import re
import time
import random
from urllib.parse import urlparse
class WikipediaScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wikipedia Article Scraper - Professional Edition")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f0f0")
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        self.create_frames()
        
        self.create_widgets()
    def create_frames(self):
        self.control_frame = tk.Frame(self.root, bg="#3498db", padx=10, pady=10)
        self.control_frame.pack(fill=tk.X)
        self.result_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    def create_widgets(self):
        tk.Label(self.control_frame, text="Wikipedia URL:", bg="#3498db", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.url_entry = tk.Entry(self.control_frame, width=50, font=("Arial", 9))
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.url_entry.insert(0, "https://en.wikipedia.org/wiki/Python_(programming_language)")
        self.scrape_btn = tk.Button(self.control_frame, text="Scrape Article", command=self.start_scraping, 
                                   bg="#9b59b6", fg="white", font=("Arial", 9, "bold"), padx=20)
        self.scrape_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(self.control_frame, text="Clear", command=self.clear_output,
                                  bg="#9b59b6", fg="white", font=("Arial", 9, "bold"), padx=20)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn = tk.Button(self.control_frame, text="Save Results", command=self.save_results, bg="#9b59b6", fg="white", font=("Arial", 9, "bold"), padx=20)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        options_frame = tk.Frame(self.control_frame, bg="#3498db")
        options_frame.pack(side=tk.LEFT, padx=10)
        self.extract_summary = tk.BooleanVar(value=True)
        self.extract_infobox = tk.BooleanVar(value=True)
        self.extract_sections = tk.BooleanVar(value=True)
        self.extract_references = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Summary", variable=self.extract_summary, bg="#3498db", fg="white", 
                      selectcolor="#3498db", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Checkbutton(options_frame, text="Infobox", variable=self.extract_infobox, bg="#3498db", fg="white", 
                      selectcolor="#3498db", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Checkbutton(options_frame, text="Sections", variable=self.extract_sections, bg="#3498db", fg="white", 
                      selectcolor="#3498db", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Checkbutton(options_frame, text="References", variable=self.extract_references, bg="#3498db", fg="white", 
                      selectcolor="#3498db", font=("Arial", 10)).pack(side=tk.LEFT)
        self.advanced_btn = tk.Button(self.control_frame, text="Advanced Options", command=self.show_advanced_options,
                                     bg="#9b59b6", fg="white", font=("Arial", 10, "bold"))
        self.advanced_btn.pack(side=tk.LEFT, padx=5)
        tk.Label(self.result_frame, text="Scraped Article Data:", bg="#f0f0f0", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        self.notebook = ttk.Notebook(self.result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        self.overview_frame = tk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")
        columns = ("Section", "Content")
        self.tree = ttk.Treeview(self.overview_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=400)
        scrollbar = ttk.Scrollbar(self.overview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.detail_frame = tk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text="Detailed View")
        self.text_area = scrolledtext.ScrolledText(self.detail_frame, wrap=tk.WORD, width=80, height=20, font=("Arial", 10))
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, wrap=tk.WORD, width=80, height=20, font=("Arial", 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.troubleshoot_frame = tk.Frame(self.notebook)
        self.notebook.add(self.troubleshoot_frame, text="Troubleshooting")
        self.troubleshoot_text = scrolledtext.ScrolledText(self.troubleshoot_frame, wrap=tk.WORD, width=80, height=20, font=("Arial", 10))
        self.troubleshoot_text.pack(fill=tk.BOTH, expand=True)
        self.troubleshoot_text.insert(tk.END, "Troubleshooting information will appear here if any issues occur during scraping.")
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var, bg="#34495e", fg="white", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10)
        self.progress = ttk.Progressbar(self.status_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
    def show_advanced_options(self):
        adv_window = tk.Toplevel(self.root)
        adv_window.title("Advanced Options")
        adv_window.geometry("400x300")
        adv_window.configure(bg="#f0f0f0")
        tk.Label(adv_window, text="Request Delay (seconds):", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.delay_var = tk.DoubleVar(value=1.0)
        delay_scale = tk.Scale(adv_window, from_=0.5, to=5.0, resolution=0.5, orient=tk.HORIZONTAL, variable=self.delay_var, length=200)
        delay_scale.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(adv_window, text="Request Timeout (seconds):", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.timeout_var = tk.IntVar(value=10)
        timeout_scale = tk.Scale(adv_window, from_=5, to=30, resolution=1, orient=tk.HORIZONTAL, variable=self.timeout_var, length=200)
        timeout_scale.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(adv_window, text="Retry Attempts:", bg="#f0f0f0", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.retry_var = tk.IntVar(value=3)
        retry_scale = tk.Scale(adv_window, from_=1, to=10, resolution=1, orient=tk.HORIZONTAL, variable=self.retry_var, length=200)
        retry_scale.grid(row=2, column=1, padx=10, pady=10)
        self.use_proxy_var = tk.BooleanVar(value=False)
        proxy_check = tk.Checkbutton(adv_window, text="Use Proxy", variable=self.use_proxy_var, bg="#f0f0f0", font=("Arial", 10))
        proxy_check.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        tk.Label(adv_window, text="Proxy Address:", bg="#f0f0f0", font=("Arial", 10)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.proxy_entry = tk.Entry(adv_window, width=30)
        self.proxy_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        self.proxy_entry.insert(0, "http://your.proxy.address:port")
        save_btn = tk.Button(adv_window, text="Save Settings", command=lambda: self.save_advanced_settings(adv_window),
                            bg="#3498db", fg="white", font=("Arial", 10, "bold"))
        save_btn.grid(row=5, column=0, columnspan=2, padx=10, pady=20)
    def save_advanced_settings(self, window):
        self.request_delay = self.delay_var.get()
        self.request_timeout = self.timeout_var.get()
        self.retry_attempts = self.retry_var.get()
        self.use_proxy = self.use_proxy_var.get()
        self.proxy_address = self.proxy_entry.get()
        messagebox.showinfo("Settings Saved", "Advanced settings have been saved.")
        window.destroy()
    def clear_output(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.text_area.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.troubleshoot_text.delete(1.0, tk.END)
        self.troubleshoot_text.insert(tk.END, "Troubleshooting information will appear here if any issues occur during scraping.")
        self.progress['value'] = 0
        self.status_var.set("Output cleared. Ready for new scraping.")
        self.save_btn.config(state=tk.DISABLED)
        if hasattr(self, 'article_data'):
            delattr(self, 'article_data')
        if hasattr(self, 'article_stats'):
            delattr(self, 'article_stats')
        if hasattr(self, 'article_title'):
            delattr(self, 'article_title')
    def start_scraping(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a Wikipedia URL to scrape")
            return
        if "wikipedia.org" not in url:
            messagebox.showwarning("Input Error", "Please enter a valid Wikipedia URL")
            return
        if not hasattr(self, 'request_delay'):
            self.request_delay = 1.0
        if not hasattr(self, 'request_timeout'):
            self.request_timeout = 10
        if not hasattr(self, 'retry_attempts'):
            self.retry_attempts = 3
        if not hasattr(self, 'use_proxy'):
            self.use_proxy = False
        if not hasattr(self, 'proxy_address'):
            self.proxy_address = ""
        self.status_var.set("Scraping in progress...")
        self.progress['value'] = 0
        self.scrape_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.troubleshoot_text.delete(1.0, tk.END)
        self.troubleshoot_text.insert(tk.END, "Scraping in progress...\n")
        threading.Thread(target=self.scrape_article, args=(url,), daemon=True).start()
    def scrape_article(self, url):
        try:
            self.progress['value'] = 10
            self.root.update_idletasks()
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.google.com/'
            }
            proxies = None
            if self.use_proxy and self.proxy_address and self.proxy_address != "http://your.proxy.address:port":
                proxies = {
                    'http': self.proxy_address,
                    'https': self.proxy_address
                }
            res = None
            for attempt in range(self.retry_attempts):
                try:
                    self.log_troubleshoot(f"Attempt {attempt + 1} of {self.retry_attempts}")
                    res = requests.get(
                        url, 
                        headers=headers, 
                        timeout=self.request_timeout,
                        proxies=proxies
                    )
                    if res.status_code == 403:
                        self.log_troubleshoot(f"Received 403 Forbidden. Waiting {self.request_delay} seconds before retry...")
                        time.sleep(self.request_delay)
                        continue
                    if res.status_code != 200:
                        self.log_troubleshoot(f"Received HTTP status code: {res.status_code}")
                        break
                    break
                except requests.exceptions.RequestException as e:
                    self.log_troubleshoot(f"Request exception: {str(e)}")
                    if attempt < self.retry_attempts - 1:
                        self.log_troubleshoot(f"Waiting {self.request_delay} seconds before retry...")
                        time.sleep(self.request_delay)
                    continue
            if not res or res.status_code != 200:
                error_msg = f"Failed to retrieve page. Status code: {res.status_code if res else 'No response'}"
                self.log_troubleshoot(f"Error: {error_msg}")
                self.root.after(0, self.show_error, error_msg)
                return
            self.progress['value'] = 30
            self.root.update_idletasks()
            content = BeautifulSoup(res.text, "html.parser")
            self.progress['value'] = 50
            self.root.update_idletasks()
            self.article_title = self.extract_title(content)
            article_data = {}
            if self.extract_summary.get():
                article_data["summary"] = self.extract_summary_text(content)
            if self.extract_infobox.get():
                article_data["infobox"] = self.extract_infobox_data(content)
            if self.extract_sections.get():
                article_data["sections"] = self.extract_sections_data(content)
            if self.extract_references.get():
                article_data["references"] = self.extract_references_data(content)
            article_stats = self.generate_statistics(content, article_data)
            self.progress['value'] = 90
            self.root.update_idletasks()
            self.root.after(0, self.update_ui, article_data, article_stats)
        except Exception as e:
            self.log_troubleshoot(f"Exception occurred: {str(e)}")
            self.root.after(0, self.show_error, str(e))
    def log_troubleshoot(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, lambda: self.troubleshoot_text.insert(tk.END, f"[{timestamp}] {message}\n"))
        self.root.after(0, lambda: self.troubleshoot_text.see(tk.END))
    def extract_title(self, content):
        title_element = content.find("h1", id="firstHeading")
        return title_element.text.strip() if title_element else "Unknown Title"
    def extract_summary_text(self, content):
        summary_paragraphs = content.select("div.mw-parser-output > p")
        summary = ""
        for p in summary_paragraphs:
            if p.text.strip() and not p.find("b"): 
                summary += p.text.strip() + "\n\n"
                if len(summary) > 1000:                
                    break
        return summary if summary else "No summary found"
    def extract_infobox_data(self, content):
        infobox = content.find("table", class_="infobox")
        if not infobox:
            return "No infobox found"
        infobox_data = {}
        for row in infobox.find_all("tr"):
            header = row.find("th")
            data = row.find("td")
            if header and data:
                infobox_data[header.text.strip()] = data.text.strip()
        return infobox_data
    def extract_sections_data(self, content):
        sections = {}
        content_div = content.find("div", id="mw-content-text")
        if not content_div:
            return "No content found"
        headings = content_div.find_all(["h2", "h3", "h4"])
        for heading in headings:
            heading_text = heading.text.strip().replace("[edit]", "")
            if not heading_text:
                continue
            content_elements = []
            current = heading.next_sibling
            while current and current.name not in ["h2", "h3", "h4"]:
                if current.name and current.name in ["p", "ul", "ol", "div"] and "class" in current.attrs:
                    if "mw-empty-elt" not in current.get("class", []):
                        content_elements.append(current)
                current = current.next_sibling
            section_text = ""
            for element in content_elements:
                if element.name in ["p", "div"]:
                    section_text += element.text.strip() + "\n\n"
                elif element.name in ["ul", "ol"]:
                    for li in element.find_all("li", recursive=False):
                        section_text += f"• {li.text.strip()}\n"
                    section_text += "\n"
            sections[heading_text] = section_text
        return sections
    def extract_references_data(self, content):
        references = {}
        ref_list = content.find("ol", class_="references")
        if not ref_list:
            return "No references found"
        for i, ref in enumerate(ref_list.find_all("li", recursive=False)):
            ref_text = ref.get_text().strip()
            ref_id = ref.get("id", "")
            references[f"Reference {i+1}"] = ref_text
        return references
    def generate_statistics(self, content, article_data):
        stats = {}
        stats["title"] = self.article_title
        stats["url"] = self.url_entry.get().strip()
        stats["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        all_text = content.get_text()
        stats["character_count"] = len(all_text)
        stats["word_count"] = len(all_text.split())
        if "sections" in article_data:
            stats["section_count"] = len(article_data["sections"])
        else:
            stats["section_count"] = 0
            
        if "infobox" in article_data and isinstance(article_data["infobox"], dict):
            stats["infobox_fields"] = len(article_data["infobox"])
        else:
            stats["infobox_fields"] = 0
            
        if "references" in article_data and isinstance(article_data["references"], dict):
            stats["reference_count"] = len(article_data["references"])
        else:
            stats["reference_count"] = 0
        images = content.find_all("img")
        stats["image_count"] = len(images)
        links = content.find_all("a", href=True)
        stats["link_count"] = len(links)
        external_links = [link for link in links if link["href"].startswith("http")]
        stats["external_link_count"] = len(external_links)
        return stats
    def update_ui(self, article_data, article_stats):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.text_area.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.article_data = article_data
        self.article_stats = article_stats
        if "summary" in article_data:
            self.tree.insert("", tk.END, values=("Summary", article_data["summary"][:100] + "..."))
        if "infobox" in article_data and isinstance(article_data["infobox"], dict):
            for key, value in article_data["infobox"].items():
                self.tree.insert("", tk.END, values=(f"Infobox: {key}", value[:100] + "..." if len(value) > 100 else value))
        if "sections" in article_data:
            for section, content in article_data["sections"].items():
                self.tree.insert("", tk.END, values=(f"Section: {section}", content[:100] + "..." if len(content) > 100 else content))
        if "references" in article_data and isinstance(article_data["references"], dict):
            for ref, content in article_data["references"].items():
                self.tree.insert("", tk.END, values=(ref, content[:100] + "..." if len(content) > 100 else content))
        self.text_area.insert(tk.END, f"TITLE: {self.article_title}\n")
        self.text_area.insert(tk.END, f"URL: {self.url_entry.get().strip()}\n")
        self.text_area.insert(tk.END, f"SCRAPED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.text_area.insert(tk.END, "=" * 80 + "\n\n")
        if "summary" in article_data:
            self.text_area.insert(tk.END, "SUMMARY:\n")
            self.text_area.insert(tk.END, article_data["summary"] + "\n\n")
            self.text_area.insert(tk.END, "-" * 80 + "\n\n")
        if "infobox" in article_data and isinstance(article_data["infobox"], dict):
            self.text_area.insert(tk.END, "INFOBOX:\n")
            for key, value in article_data["infobox"].items():
                self.text_area.insert(tk.END, f"{key}: {value}\n")
            self.text_area.insert(tk.END, "\n" + "-" * 80 + "\n\n")
        if "sections" in article_data:
            self.text_area.insert(tk.END, "SECTIONS:\n")
            for section, content in article_data["sections"].items():
                self.text_area.insert(tk.END, f"{section}:\n{content}\n\n")
            self.text_area.insert(tk.END, "-" * 80 + "\n\n")
        if "references" in article_data and isinstance(article_data["references"], dict):
            self.text_area.insert(tk.END, "REFERENCES:\n")
            for ref, content in article_data["references"].items():
                self.text_area.insert(tk.END, f"{ref}: {content}\n\n")
        self.stats_text.insert(tk.END, f"TITLE: {article_stats['title']}\n")
        self.stats_text.insert(tk.END, f"URL: {article_stats['url']}\n")
        self.stats_text.insert(tk.END, f"SCRAPED AT: {article_stats['scraped_at']}\n")
        self.stats_text.insert(tk.END, "=" * 80 + "\n\n")
        self.stats_text.insert(tk.END, "CONTENT STATISTICS:\n")
        self.stats_text.insert(tk.END, f"Character Count: {article_stats['character_count']:,}\n")
        self.stats_text.insert(tk.END, f"Word Count: {article_stats['word_count']:,}\n")
        self.stats_text.insert(tk.END, f"Section Count: {article_stats['section_count']}\n")
        self.stats_text.insert(tk.END, f"Infobox Fields: {article_stats['infobox_fields']}\n")
        self.stats_text.insert(tk.END, f"Reference Count: {article_stats['reference_count']}\n")
        self.stats_text.insert(tk.END, f"Image Count: {article_stats['image_count']}\n")
        self.stats_text.insert(tk.END, f"Total Links: {article_stats['link_count']}\n")
        self.stats_text.insert(tk.END, f"External Links: {article_stats['external_link_count']}\n")
        self.progress['value'] = 100
        self.status_var.set(f"Successfully scraped article: {self.article_title}")
        self.scrape_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        self.log_troubleshoot("Scraping completed successfully!")
    def show_error(self, error_msg):
        self.status_var.set("Error occurred")
        messagebox.showerror("Scraping Error", f"An error occurred: {error_msg}")
        self.scrape_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.troubleshoot_text.insert(tk.END, "\n\nTROUBLESHOOTING TIPS:\n")
        self.troubleshoot_text.insert(tk.END, "1. Check your internet connection\n")
        self.troubleshoot_text.insert(tk.END, "2. Try increasing the request delay in Advanced Options\n")
        self.troubleshoot_text.insert(tk.END, "3. Try using a different user agent\n")
        self.troubleshoot_text.insert(tk.END, "4. Consider using a proxy if you're making many requests\n")
        self.troubleshoot_text.insert(tk.END, "5. Verify the Wikipedia URL is correct\n")
    def save_results(self):
        if not hasattr(self, 'article_data') or not self.article_data:
            messagebox.showwarning("No Data", "No article data to save. Please scrape an article first.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=f"{self.article_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if not file_path:
            return
        try:
            if file_path.endswith('.json'):
                import json
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "title": self.article_title,
                        "url": self.url_entry.get().strip(),
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data": self.article_data,
                        "statistics": self.article_stats
                    }, f, indent=2)
            elif file_path.endswith('.csv'):
                import csv
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Section", "Content"])
                    if "summary" in self.article_data:
                        writer.writerow(["Summary", self.article_data["summary"].replace("\n", " ")])
                    if "infobox" in self.article_data and isinstance(self.article_data["infobox"], dict):
                        for key, value in self.article_data["infobox"].items():
                            writer.writerow([f"Infobox: {key}", value.replace("\n", " ")])
                    if "sections" in self.article_data:
                        for section, content in self.article_data["sections"].items():
                            writer.writerow([f"Section: {section}", content.replace("\n", " ")])
                    if "references" in self.article_data and isinstance(self.article_data["references"], dict):
                        for ref, content in self.article_data["references"].items():
                            writer.writerow([ref, content.replace("\n", " ")])
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"TITLE: {self.article_title}\n")
                    f.write(f"URL: {self.url_entry.get().strip()}\n")
                    f.write(f"SCRAPED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 80 + "\n\n")
                    if "summary" in self.article_data:
                        f.write("SUMMARY:\n")
                        f.write(self.article_data["summary"] + "\n\n")
                        f.write("-" * 80 + "\n\n")
                    if "infobox" in self.article_data and isinstance(self.article_data["infobox"], dict):
                        f.write("INFOBOX:\n")
                        for key, value in self.article_data["infobox"].items():
                            f.write(f"{key}: {value}\n")
                        f.write("\n" + "-" * 80 + "\n\n")
                    if "sections" in self.article_data:
                        f.write("SECTIONS:\n")
                        for section, content in self.article_data["sections"].items():
                            f.write(f"{section}:\n{content}\n\n")
                        f.write("-" * 80 + "\n\n")
                    if "references" in self.article_data and isinstance(self.article_data["references"], dict):
                        f.write("REFERENCES:\n")
                        for ref, content in self.article_data["references"].items():
                            f.write(f"{ref}: {content}\n\n")                    
                    f.write("\n" + "=" * 80 + "\n\n")
                    f.write("STATISTICS:\n")
                    f.write(f"Character Count: {self.article_stats['character_count']:,}\n")
                    f.write(f"Word Count: {self.article_stats['word_count']:,}\n")
                    f.write(f"Section Count: {self.article_stats['section_count']}\n")
                    f.write(f"Infobox Fields: {self.article_stats['infobox_fields']}\n")
                    f.write(f"Reference Count: {self.article_stats['reference_count']}\n")
                    f.write(f"Image Count: {self.article_stats['image_count']}\n")
                    f.write(f"Total Links: {self.article_stats['link_count']}\n")
                    f.write(f"External Links: {self.article_stats['external_link_count']}\n")  
            messagebox.showinfo("Success", f"Article data saved to {file_path}")
            self.status_var.set(f"Saved article data to file")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {str(e)}")
            self.status_var.set("Error saving file")
if __name__ == "__main__":
    root = tk.Tk()
    app = WikipediaScraperApp(root)
    root.mainloop()