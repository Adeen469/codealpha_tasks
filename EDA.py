import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Make app DPI Aware
except Exception:
    pass

import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd, matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class EcommerceAnalyticsApp:
    def __init__(self, root):
        self.root, self.data = root, None
        self.root.title("Ecommerce Sales Analytics Dashboard")

        # ⚡ Removed direct zoomed
        # self.root.state('zoomed')   

        self.setup_ui()

        # ✅ Fix: force update and delayed zoom
        self.root.update_idletasks()
        self.root.after(100, lambda: self.root.state('zoomed'))


    # ---------- UI ----------
    def setup_ui(self):
        main = ttk.Frame(self.root); main.pack(fill=tk.BOTH, expand=True)
        side = ttk.Frame(main, relief=tk.RAISED, borderwidth=2); side.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self._make_section(side, "Data Import", [("Upload Excel/CSV", self.upload_file)])
        self.file_label = ttk.Label(side, text="No file selected", font=('Arial', 9), wraplength=180); self.file_label.pack()
        
        # Visualization dropdown
        self.viz_var = self._make_combo(side, "Visualization", [
            "Sum of Sales by Segment","Top 10 Customers by Sales","Sales Distribution by Region and Segment",
            "Profit Breakdown by Region and Segment","Count of Order ID by Customer Name","Sum of Sales by Category",
            "Sum of Sales by Customer Name","Sum of Sales by Month and Region","Count of Order ID by Region",
            "Top 5 Products by Revenue","Monthly Revenue Trend","Monthly Sales Trend","Profitability by Sub-Category"
        ], self.update_visualization)

        # Zoom controls
        self._make_section(side, "Zoom Controls", [
            ("➕ Zoom In", self.zoom_in), ("➖ Zoom Out", self.zoom_out), ("🔄 Reset Zoom", self.reset_zoom)
        ])

        content = ttk.Frame(main); content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        ttk.Label(content, text="Ecommerce Sales Analytics Dashboard", font=('Arial',24,'bold')).pack(pady=(0,20))
        
        # metrics
        self.metrics_labels = {}; metrics = ttk.LabelFrame(content, text="Key Metrics", padding=10); metrics.pack(fill=tk.X,pady=20)
        for lbl,key in [("Total Sales","total_sales"),("Total Profit","total_profit"),("Total Orders","total_orders"),("Total Customers","total_customers")]:
            f=ttk.Frame(metrics); f.pack(side=tk.LEFT,expand=True,fill=tk.X,padx=10)
            ttk.Label(f,text=lbl,font=('Arial',10,'bold')).pack()
            self.metrics_labels[key]=ttk.Label(f,text="N/A",font=('Arial',12)); self.metrics_labels[key].pack()

        # viz
        viz = ttk.LabelFrame(content,text="Visualization",padding=10); viz.pack(fill=tk.BOTH,expand=True)
        self.fig=Figure(figsize=(12,8),dpi=100)
        self.canvas=FigureCanvasTkAgg(self.fig,viz)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH,expand=True)
        self.toolbar=NavigationToolbar2Tk(self.canvas,viz); self.toolbar.update()
        for ev in ('<MouseWheel>','<Button-4>','<Button-5>'): self.canvas.get_tk_widget().bind(ev,self.on_mousewheel)

        # enable drag-to-pan
        self.enable_pan()

        # info
        self.info_labels={}; info=ttk.LabelFrame(content,text="Data Information",padding=10); info.pack(fill=tk.X,pady=20)
        for lbl,key in [("Dataset Shape","shape"),("Columns","columns"),("Date Range","date_range")]:
            f=ttk.Frame(info); f.pack(side=tk.LEFT,expand=True,fill=tk.X,padx=10)
            ttk.Label(f,text=lbl,font=('Arial',10,'bold')).pack()
            self.info_labels[key]=ttk.Label(f,text="N/A",font=('Arial',9)); self.info_labels[key].pack()

    def _make_section(self, parent,title,btns):
        f=ttk.LabelFrame(parent,text=title,padding=10); f.pack(fill=tk.X,padx=10,pady=10)
        for txt,cmd in btns: ttk.Button(f,text=txt,command=cmd,width=18).pack(pady=2)

    def _make_combo(self,parent,title,values,cmd,default=None):
        f=ttk.LabelFrame(parent,text=title,padding=10); f.pack(fill=tk.X,padx=10,pady=10)
        var=tk.StringVar(value=default or ""); combo=ttk.Combobox(f,textvariable=var,values=values,state="readonly",width=18)
        combo.pack(); combo.bind('<<ComboboxSelected>>',cmd); return var

    # ---------- Data ----------
    def upload_file(self):
        f=filedialog.askopenfilename(title="Select Excel or CSV",filetypes=[("Excel","*.xlsx"),("CSV","*.csv")])
        if not f: return
        self.data=pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f)
        self._after_load(f)

    def _after_load(self,filename):
        self.process_data(); self.file_label.config(text=filename)
        self.update_metrics(); self.update_info()
        self.viz_var.set("Sum of Sales by Segment"); self.update_visualization()

    def process_data(self):
        if self.data is not None and 'Order Date' in self.data.columns:
            self.data['Order Date']=pd.to_datetime(self.data['Order Date'])
            self.data['Month']=self.data['Order Date'].dt.month
            self.data['Year']=self.data['Order Date'].dt.year

    # ---------- Zoom ----------
    def zoom_in(self): self._zoom(0.1)
    def zoom_out(self): self._zoom(-0.1)
    def reset_zoom(self): self.update_visualization()

    def _zoom(self, factor):
        ax = self.canvas.figure.gca()
        if not ax: return
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        xr, yr = (x1 - x0) * factor, (y1 - y0) * factor
        ax.set_xlim(x0 + xr, x1 - xr); ax.set_ylim(y0 + yr, y1 - yr)
        self.canvas.draw()

    def on_mousewheel(self, e): 
        self.zoom_in() if e.num == 4 or e.delta > 0 else self.zoom_out()

    # ---------- Pan (Drag to Move) ----------
    def enable_pan(self):
        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self._press_event = None

    def _on_press(self, event):
        if event.button == 1 and event.inaxes: self._press_event = event
    def _on_release(self, event): self._press_event = None

    def _on_motion(self, event):
        if self._press_event is None or event.inaxes != self._press_event.inaxes: return
        ax = event.inaxes
        trans = ax.transData.inverted()
        prev_data = trans.transform((self._press_event.x, self._press_event.y))
        curr_data = trans.transform((event.x, event.y))
        dx, dy = prev_data[0] - curr_data[0], prev_data[1] - curr_data[1]
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        ax.set_xlim(x0 + dx, x1 + dx); ax.set_ylim(y0 + dy, y1 + dy)
        self.canvas.draw(); self._press_event = event

    # ---------- Metrics/Info ----------
    def update_metrics(self):
        d=self.data; 
        self.metrics_labels['total_sales'].config(text=f"₹{d['Sales'].sum():,.0f}")
        self.metrics_labels['total_profit'].config(text=f"₹{d['Profit'].sum():,.0f}")
        self.metrics_labels['total_orders'].config(text=f"{d['Order ID'].nunique():,}")
        self.metrics_labels['total_customers'].config(text=f"{d['Customer Name'].nunique():,}")

    def update_info(self):
        d=self.data; self.info_labels['shape'].config(text=str(d.shape))
        self.info_labels['columns'].config(text=f"{len(d.columns)} columns")
        self.info_labels['date_range'].config(text=f"{d['Order Date'].min().date()} to {d['Order Date'].max().date()}")

    # ---------- Visualization ----------
    def update_visualization(self,e=None):
        if self.data is None: return
        self.create_visualization(self.viz_var.get())

    def create_visualization(self,viz):
        self.fig.clear(); ax=self.fig.add_subplot(111)
        ax.grid(False)
        getattr(self,f"viz_{viz.replace(' ','_').replace('-','_').lower()}")(ax)
        self.fig.tight_layout(); self.canvas.draw()

    # ---------- All Visualization Functions ----------
    def viz_sum_of_sales_by_segment(self, ax):
        seg=self.data.groupby('Segment')['Sales'].sum().sort_values(ascending=False)
        bars=ax.bar(seg.index,seg.values,color=['#1f77b4','#ff7f0e','#2ca02c'])
        ax.set_title('Sum of Sales by Segment'); ax.set_xlabel('Segment'); ax.set_ylabel('Total Sales (₹)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)   # horizontal grid
        for bar in bars: 
            h=bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2.,h+h*0.01,f'₹{h:,.0f}',ha='center')


    def viz_top_10_customers_by_sales(self, ax):
        top=self.data.groupby('Customer Name')['Sales'].sum().nlargest(10)
        bars=ax.barh(range(len(top)),top.values)
        ax.set_yticks(range(len(top))); ax.set_yticklabels(top.index)
        ax.set_title('Top 10 Customers by Sales'); ax.set_xlabel('Total Sales (₹)')
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)   # vertical grid
        for i,v in enumerate(top.values): 
            ax.text(v+v*0.01,i,f'₹{v:,.0f}',va='center')


    def viz_sales_distribution_by_region_and_segment(self, ax):
        pivot=self.data.pivot_table(values='Sales',index='Region',columns='Segment',aggfunc='sum',fill_value=0)
        ax.axis('off')
        t=ax.table(cellText=pivot.values.round(2),rowLabels=pivot.index,colLabels=pivot.columns,loc='center')
        t.auto_set_font_size(False); t.set_fontsize(10)
        ax.set_title('Sales Distribution by Region and Segment')


    def viz_profit_breakdown_by_region_and_segment(self, ax):
        pivot=self.data.pivot_table(values='Profit',index='Region',columns='Segment',aggfunc='sum',fill_value=0)
        ax.axis('off')
        t=ax.table(cellText=pivot.values.round(2),rowLabels=pivot.index,colLabels=pivot.columns,loc='center')
        t.auto_set_font_size(False); t.set_fontsize(10)
        ax.set_title('Profit Breakdown by Region and Segment')


    def viz_count_of_order_id_by_customer_name(self, ax):
        counts=self.data.groupby('Customer Name')['Order ID'].nunique().nlargest(15)
        bars=ax.bar(range(len(counts)),counts.values)
        ax.set_xticks(range(len(counts))); ax.set_xticklabels(counts.index,rotation=45,ha='right')
        ax.set_title('Count of Order ID by Customer Name (Top 15)'); ax.set_ylabel('Orders')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)   # horizontal grid
        for i,v in enumerate(counts.values): 
            ax.text(i,v+0.1,str(v),ha='center')


    def viz_sum_of_sales_by_category(self, ax):
        cat=self.data.groupby('Category')['Sales'].sum()
        ax.pie(cat.values,labels=cat.index,autopct='%1.1f%%',startangle=90)
        ax.set_title('Sum of Sales by Category')


    def viz_sum_of_sales_by_customer_name(self, ax):
        cs=self.data.groupby('Customer Name')['Sales'].sum().nlargest(20)
        bars=ax.bar(range(len(cs)),cs.values)
        ax.set_xticks(range(len(cs))); ax.set_xticklabels(cs.index,rotation=45,ha='right')
        ax.set_title('Sum of Sales by Customer Name (Top 20)'); ax.set_ylabel('Sales (₹)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)   # horizontal grid
        for i,v in enumerate(cs.values): 
            ax.text(i,v+v*0.01,f'₹{v:,.0f}',ha='center',rotation=90)


    def viz_sum_of_sales_by_month_and_region(self, ax):
        m=self.data.groupby(['Month','Region'])['Sales'].sum().unstack(fill_value=0)
        m.plot(kind='bar',stacked=True,ax=ax)
        ax.set_title('Sum of Sales by Month and Region'); ax.legend(title='Region')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)   # horizontal grid


    def viz_count_of_order_id_by_region(self, ax):
        ro=self.data.groupby('Region')['Order ID'].nunique()
        ax.pie(ro.values,labels=ro.index,autopct='%1.1f%%',startangle=90)
        ax.set_title('Count of Order ID by Region')


    def viz_top_5_products_by_revenue(self, ax):
        pr=self.data.groupby('Product Name')['Sales'].sum().nlargest(5)
        bars=ax.bar(range(len(pr)),pr.values)
        ax.set_xticks(range(len(pr))); ax.set_xticklabels(pr.index,rotation=45,ha='right')
        ax.set_title('Top 5 Products by Revenue')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)   # horizontal grid
        for i,v in enumerate(pr.values): 
            ax.text(i,v+v*0.01,f'₹{v:,.0f}',ha='center')


    def viz_monthly_revenue_trend(self, ax):
        monthly = self.data.groupby(['Year','Month'])['Sales'].sum().reset_index()
        monthly['Period'] = pd.to_datetime(monthly[['Year','Month']].assign(DAY=1))
        ax.plot(monthly['Period'], monthly['Sales'], marker='o', color='black')
        ax.set_title("Monthly Revenue Trend")
        ax.set_xlabel("Month"); ax.set_ylabel("Revenue")
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)


    def viz_monthly_sales_trend(self, ax):
        monthly = self.data.groupby(['Year','Month'])['Sales'].count().reset_index()
        monthly['Period'] = pd.to_datetime(monthly[['Year','Month']].assign(DAY=1))
        ax.plot(monthly['Period'], monthly['Sales'], marker='o', color='black')
        ax.set_title("Monthly Sales Trend")
        ax.set_xlabel("Month"); ax.set_ylabel("Number of Sales")
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)


    def viz_profitability_by_sub_category(self, ax):
        sc=self.data.groupby('Sub-Category')['Profit'].sum().sort_values(ascending=False)
        colors=['green' if x>0 else 'red' for x in sc.values]
        bars=ax.bar(range(len(sc)),sc.values,color=colors)
        ax.set_xticks(range(len(sc))); ax.set_xticklabels(sc.index,rotation=45,ha='right')
        ax.set_title('Profitability by Sub-Category'); ax.axhline(0,color='black')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)   # horizontal grid
        for i,v in enumerate(sc.values): 
            ax.text(i,v+(v*0.01),f'₹{v:,.0f}',ha='center')


def main(): 
    root=tk.Tk(); EcommerceAnalyticsApp(root); root.mainloop()
if __name__=="__main__": main()
