import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. NODE OBJECT FOR MANUAL MODE
# ==========================================
class NodeObject:
    def __init__(self, canvas, node_id, val, x, y):
        self.canvas = canvas
        self.id = node_id
        self.val = val
        self.x = x
        self.y = y
        self.radius = 24

        self.oval_id = self.canvas.create_oval(
            x - self.radius, y - self.radius, 
            x + self.radius, y + self.radius, 
            fill="#b4befe", outline="#cdd6f4", width=2, tags="node"
        )
        self.text_id = self.canvas.create_text(
            x, y, text=str(val), fill="#11111b", font=("Calibri", 13, "bold"), tags="node"
        )

    def move_to(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.canvas.coords(
            self.oval_id, 
            new_x - self.radius, new_y - self.radius, 
            new_x + self.radius, new_y + self.radius
        )
        self.canvas.coords(self.text_id, new_x, new_y)

    def set_color(self, fill_color):
        self.canvas.itemconfig(self.oval_id, fill=fill_color)

    def contains(self, px, py):
        return (self.x - px) ** 2 + (self.y - py) ** 2 <= (self.radius + 5) ** 2

    def delete_from_canvas(self):
        self.canvas.delete(self.oval_id)
        self.canvas.delete(self.text_id)


# ==========================================
# 2. TAB 1: MANUAL TREE BUILDER
# ==========================================
class ManualTreeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        
        self.nodes = {}        
        self.edges = []        
        self.node_counter = 0
        self.dragged_node_id = None
        self.selected_node_id = None

        self.LEVEL_GAP_Y = 100
        self.START_Y = 80

        # --- Top Bar ---
        top_frame = tk.Frame(self, bg="#313244", padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        title = tk.Label(top_frame, text="🛠️ โหมดสร้างต้นไม้เอง (วางตำแหน่งและเชื่อมเส้นเอง)", font=("Calibri", 13, "bold"), fg="#cdd6f4", bg="#313244")
        title.pack(side=tk.LEFT, padx=10)

        btn_check = tk.Button(top_frame, text="✅ ตรวจสอบกฎ BST", font=("Calibri", 11, "bold"), bg="#a6e3a1", fg="#11111b", command=self.check_if_bst)
        btn_check.pack(side=tk.RIGHT, padx=5)

        btn_clear = tk.Button(top_frame, text="🗑️ ล้างหน้าจอ", font=("Calibri", 11, "bold"), bg="#f38ba8", fg="#11111b", command=self.clear_all)
        btn_clear.pack(side=tk.RIGHT, padx=5)

        # --- Main Layout ---
        main_frame = tk.Frame(self, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        palette = tk.Frame(main_frame, bg="#2b2b3b", width=220, padx=15, pady=15)
        palette.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(palette, text="➕ เพิ่ม Node ใหม่", font=("Calibri", 12, "bold"), fg="#f9e2af", bg="#2b2b3b").pack(anchor="w", pady=(0, 5))
        
        self.entry_val = tk.Entry(palette, font=("Calibri", 12), width=10, bg="#45475a", fg="#ffffff", insertbackground="white")
        self.entry_val.pack(anchor="w", pady=(2, 10))
        self.entry_val.bind("<Return>", lambda e: self.add_node_to_canvas())

        btn_add = tk.Button(palette, text="+ เพิ่ม Node (Enter)", font=("Calibri", 10, "bold"), bg="#89b4fa", fg="#11111b", command=self.add_node_to_canvas)
        btn_add.pack(fill=tk.X, pady=(0, 15))

        instructions = (
            "📌 **วิธีใช้งาน:**\n\n"
            "1. **วาง Node:** ลากย้าย Node ไปตาม Level ต่างๆ\n\n"
            "2. **เส้นไกด์สีส้ม:** แสดงฝั่งซ้าย/ขวา ของ Node แม่ที่คลิกเลือก\n\n"
            "3. **เชื่อม/ตัดเส้น:** คลิกขวาที่ Node"
        )
        tk.Label(palette, text=instructions, font=("Calibri", 9), fg="#a6adc8", bg="#2b2b3b", justify=tk.LEFT, wraplength=180).pack(anchor="w")

        self.canvas = tk.Canvas(main_frame, bg="#181825", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", lambda e: self.draw_level_lines())
        self.canvas.bind("<Button-1>", self.on_left_click_press)
        self.canvas.bind("<B1-Motion>", self.on_left_click_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_click_release)
        self.canvas.bind("<Button-3>", self.show_popup_menu)
        self.canvas.bind("<Button-2>", self.show_popup_menu)

    def draw_level_lines(self):
        self.canvas.delete("grid_line")
        width = self.canvas.winfo_width() or 800
        for level in range(6):
            y = self.START_Y + (level * self.LEVEL_GAP_Y)
            self.canvas.create_line(20, y, width - 20, y, fill="#313244", dash=(4, 6), width=1, tags="grid_line")
            lbl_text = f"Level {level} (Root)" if level == 0 else f"Level {level}"
            self.canvas.create_text(25, y - 12, text=lbl_text, fill="#6c7086", font=("Calibri", 10, "bold"), anchor="w", tags="grid_line")
        self.canvas.tag_lower("grid_line")

    def draw_helper_zone(self, parent_id):
        self.canvas.delete("helper_zone")
        if not parent_id or parent_id not in self.nodes: return
        parent = self.nodes[parent_id]
        px, py = parent.x, parent.y

        self.canvas.create_line(px, py + 25, px, py + 220, fill="#fab387", dash=(3, 3), width=2, tags="helper_zone")
        self.canvas.create_text(px - 15, py + 45, text=f"← ฝั่งซ้าย (< {parent.val})", fill="#fab387", font=("Calibri", 10, "bold"), anchor="e", tags="helper_zone")
        self.canvas.create_text(px + 15, py + 45, text=f"ฝั่งขวา (> {parent.val}) →", fill="#fab387", font=("Calibri", 10, "bold"), anchor="w", tags="helper_zone")
        self.canvas.tag_lower("helper_zone")
        self.canvas.tag_lower("grid_line")

    def snap_to_level(self, y):
        closest_level = max(0, min(5, round((y - self.START_Y) / self.LEVEL_GAP_Y)))
        return self.START_Y + (closest_level * self.LEVEL_GAP_Y)

    def add_node_to_canvas(self):
        val_str = self.entry_val.get().strip()
        if not val_str.isdigit():
            messagebox.showerror("Error", "กรุณากรอกตัวเลขจำนวนเต็ม")
            return
        val = int(val_str)
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"

        spawn_x = (self.canvas.winfo_width() // 2) + ((self.node_counter * 35) % 200 - 100)
        new_node = NodeObject(self.canvas, node_id, val, spawn_x, self.START_Y)
        self.nodes[node_id] = new_node
        self.entry_val.delete(0, tk.END)
        self.redraw_edges()

    def get_node_at(self, x, y):
        for n_id, node_obj in self.nodes.items():
            if node_obj.contains(x, y): return n_id
        return None

    def on_left_click_press(self, event):
        self.dragged_node_id = self.get_node_at(event.x, event.y)
        if self.dragged_node_id:
            self.selected_node_id = self.dragged_node_id
            self.draw_helper_zone(self.selected_node_id)
        else:
            self.canvas.delete("helper_zone")
            self.selected_node_id = None

    def on_left_click_drag(self, event):
        if self.dragged_node_id and self.dragged_node_id in self.nodes:
            self.nodes[self.dragged_node_id].move_to(event.x, event.y)
            self.redraw_edges()
            if self.dragged_node_id == self.selected_node_id:
                self.draw_helper_zone(self.dragged_node_id)

    def on_left_click_release(self, event):
        if self.dragged_node_id and self.dragged_node_id in self.nodes:
            node_obj = self.nodes[self.dragged_node_id]
            node_obj.move_to(node_obj.x, self.snap_to_level(node_obj.y))
            self.redraw_edges()
            if self.dragged_node_id == self.selected_node_id:
                self.draw_helper_zone(self.dragged_node_id)
        self.dragged_node_id = None

    def show_popup_menu(self, event):
        selected_id = self.get_node_at(event.x, event.y)
        if not selected_id: return

        self.selected_node_id = selected_id
        self.draw_helper_zone(selected_id)
        parent_node = self.nodes[selected_id]
        popup = tk.Menu(self, tearoff=0, font=("Calibri", 11))

        # Connect Submenu
        connect_menu = tk.Menu(popup, tearoff=0, font=("Calibri", 11))
        for child_id, child_node in self.nodes.items():
            if child_id != selected_id:
                already_connected = any(p == selected_id and c == child_id for p, c, _ in self.edges)
                connect_menu.add_command(
                    label=f"Node [{child_node.val}]" + (" (เชื่อมอยู่แล้ว)" if already_connected else ""),
                    state=tk.DISABLED if already_connected else tk.NORMAL,
                    command=lambda p=selected_id, c=child_id: self.connect_nodes(p, c)
                )
        popup.add_cascade(label=f"🔗 เชื่อมจาก [{parent_node.val}] ไปยัง...", menu=connect_menu)

        # Disconnect Submenu
        connected_edges = [(p, c) for p, c, _ in self.edges if p == selected_id or c == selected_id]
        if connected_edges:
            disconnect_menu = tk.Menu(popup, tearoff=0, font=("Calibri", 11))
            for p, c in connected_edges:
                other_id = c if p == selected_id else p
                other_node = self.nodes[other_id]
                direction = "ลูก" if p == selected_id else "แม่"
                disconnect_menu.add_command(
                    label=f"ตัดเส้นเชื่อมกับ Node [{other_node.val}] ({direction})",
                    command=lambda parent=p, child=c: self.disconnect_nodes(parent, child)
                )
            popup.add_cascade(label=f"❌ ตัดเส้นเชื่อม...", menu=disconnect_menu)

        popup.add_separator()
        popup.add_command(label=f"🗑️ ลบ Node [{parent_node.val}]", command=lambda: self.delete_node(selected_id))

        try: popup.tk_popup(event.x_root, event.y_root)
        finally: popup.grab_release()

    def connect_nodes(self, parent_id, child_id):
        if not any(p == parent_id and c == child_id for p, c, _ in self.edges):
            self.edges.append((parent_id, child_id, None))
            self.redraw_edges()

    def disconnect_nodes(self, parent_id, child_id):
        for p, c, line_id in self.edges:
            if p == parent_id and c == child_id and line_id:
                self.canvas.delete(line_id)
        self.edges = [(p, c, l) for p, c, l in self.edges if not (p == parent_id and c == child_id)]
        self.redraw_edges()

    def delete_node(self, node_id):
        if node_id in self.nodes:
            self.nodes[node_id].delete_from_canvas()
            del self.nodes[node_id]
            for p, c, line_id in self.edges:
                if (p == node_id or c == node_id) and line_id:
                    self.canvas.delete(line_id)
            self.edges = [(p, c, l) for p, c, l in self.edges if p != node_id and c != node_id]
            if self.selected_node_id == node_id:
                self.canvas.delete("helper_zone")
                self.selected_node_id = None
            self.redraw_edges()

    def redraw_edges(self):
        for p, c, line_id in self.edges:
            if line_id: self.canvas.delete(line_id)

        for node_obj in self.nodes.values():
            node_obj.set_color("#b4befe")

        new_edges = []
        for p, c, _ in self.edges:
            if p in self.nodes and c in self.nodes:
                p_node, c_node = self.nodes[p], self.nodes[c]
                is_correct = (c_node.val < p_node.val) if c_node.x < p_node.x else (c_node.val > p_node.val)
                
                line_color = "#a6e3a1" if is_correct else "#f38ba8"
                line_id = self.canvas.create_line(p_node.x, p_node.y, c_node.x, c_node.y, fill=line_color, width=2, arrow=tk.LAST)
                if not is_correct: c_node.set_color("#f38ba8")

                self.canvas.tag_lower(line_id)
                self.canvas.tag_lower("helper_zone")
                self.canvas.tag_lower("grid_line")
                new_edges.append((p, c, line_id))
        self.edges = new_edges

    def clear_all(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.node_counter = 0
        self.selected_node_id = None
        self.draw_level_lines()

    def check_if_bst(self):
        if not self.nodes:
            messagebox.showwarning("แจ้งเตือน", "ยังไม่มี Node บนหน้าจอ")
            return
        has_parent = set(c for _, c, _ in self.edges)
        roots = [n_id for n_id in self.nodes if n_id not in has_parent]
        if len(roots) != 1:
            messagebox.showerror("ผิดพลาด ❌", "ต้องมี Root Node เพียง 1 ตัวเท่านั้น")
            return
        messagebox.showinfo("ถูกต้อง! 🎉", "โครงสร้าง Binary Search Tree (BST) ถูกต้องครับ!")


# ==========================================
# 3. TAB 2: AUTOMATIC BST BUILDER (FIXED ALGORITHM)
# ==========================================
class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.x = 0
        self.y = 0

class AutoBSTTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#1e1e2e")
        self.root_bst = None

        # --- Top Control Panel ---
        top_frame = tk.Frame(self, bg="#313244", padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # 1. โซนกรอกตัวเลขเดี่ยว (เพิ่ม / ลบ ทีละตัว)
        single_frame = tk.Frame(top_frame, bg="#313244")
        single_frame.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(single_frame, text="ตัวเลข:", font=("Calibri", 11, "bold"), fg="#cdd6f4", bg="#313244").pack(side=tk.LEFT, padx=2)
        self.entry_single = tk.Entry(single_frame, font=("Calibri", 11), width=6, bg="#45475a", fg="#ffffff", insertbackground="white")
        self.entry_single.pack(side=tk.LEFT, padx=2)
        self.entry_single.bind("<Return>", lambda e: self.add_single_node())

        btn_add = tk.Button(single_frame, text="➕ เพิ่ม", font=("Calibri", 10, "bold"), bg="#a6e3a1", fg="#11111b", command=self.add_single_node)
        btn_add.pack(side=tk.LEFT, padx=2)

        btn_delete = tk.Button(single_frame, text="➖ ลบ", font=("Calibri", 10, "bold"), bg="#f38ba8", fg="#11111b", command=self.delete_single_node)
        btn_delete.pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(top_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)

        # 2. โซนกรอกเป็นชุด (Batch Input)
        batch_frame = tk.Frame(top_frame, bg="#313244")
        batch_frame.pack(side=tk.LEFT)

        tk.Label(batch_frame, text="ชุดตัวเลข:", font=("Calibri", 11, "bold"), fg="#cdd6f4", bg="#313244").pack(side=tk.LEFT, padx=2)
        self.entry_batch = tk.Entry(batch_frame, font=("Calibri", 11), width=22, bg="#45475a", fg="#ffffff", insertbackground="white")
        self.entry_batch.insert(0, "50, 30, 70, 20, 40, 60, 80")
        self.entry_batch.pack(side=tk.LEFT, padx=2)

        btn_gen = tk.Button(batch_frame, text="⚡ สร้างจากชุดตัวเลข", font=("Calibri", 10, "bold"), bg="#89b4fa", fg="#11111b", command=self.build_batch_tree)
        btn_gen.pack(side=tk.LEFT, padx=2)

        btn_clear = tk.Button(top_frame, text="🗑️ ล้างทั้งหมด", font=("Calibri", 10, "bold"), bg="#f38ba8", fg="#11111b", command=self.clear_all)
        btn_clear.pack(side=tk.RIGHT, padx=5)

        # --- Canvas Area ---
        self.canvas = tk.Canvas(self, bg="#181825", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.canvas.bind("<Configure>", lambda e: self.redraw_tree())

    # --- BST Core Logic ---
    def insert_bst(self, root, val):
        if not root:
            return BSTNode(val)
        if val < root.val:
            root.left = self.insert_bst(root.left, val)
        elif val > root.val:
            root.right = self.insert_bst(root.right, val)
        return root

    def min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def delete_bst(self, root, val):
        if not root:
            return root
        if val < root.val:
            root.left = self.delete_bst(root.left, val)
        elif val > root.val:
            root.right = self.delete_bst(root.right, val)
        else:
            if root.left is None:
                temp = root.right
                root = None
                return temp
            elif root.right is None:
                temp = root.left
                root = None
                return temp

            temp = self.min_value_node(root.right)
            root.val = temp.val
            root.right = self.delete_bst(root.right, temp.val)
        return root

    def search_bst(self, root, val):
        if not root or root.val == val:
            return root
        if val < root.val:
            return self.search_bst(root.left, val)
        return self.search_bst(root.right, val)

    # --- Layout Calculation Algorithm ---
    def get_max_depth(self, node):
        if not node: return 0
        return 1 + max(self.get_max_depth(node.left), self.get_max_depth(node.right))

    def calculate_positions(self, node, x, y, depth, max_depth, canvas_width):
        if not node: return

        # คำนวณระยะห่างฝั่งซ้าย/ขวา อย่างแม่นยำเพื่อไม่ให้ Node ซ้อนทับกัน
        offset = canvas_width / (2 ** (depth + 2))
        offset = max(offset, 30) # ระยะห่างขั้นต่ำ
        
        node.x = x
        node.y = y

        if node.left:
            self.calculate_positions(node.left, x - offset, y + 75, depth + 1, max_depth, canvas_width)
        if node.right:
            self.calculate_positions(node.right, x + offset, y + 75, depth + 1, max_depth, canvas_width)

    # --- Drawing Logic ---
    def draw_nodes_and_edges(self, node):
        if not node: return

        # วาดเส้นเชื่อมไปยังลูก
        if node.left:
            self.canvas.create_line(node.x, node.y, node.left.x, node.left.y, fill="#a6e3a1", width=2, arrow=tk.LAST)
            self.draw_nodes_and_edges(node.left)
        if node.right:
            self.canvas.create_line(node.x, node.y, node.right.x, node.right.y, fill="#a6e3a1", width=2, arrow=tk.LAST)
            self.draw_nodes_and_edges(node.right)

        # วาด Node ตัวเอง
        r = 22
        self.canvas.create_oval(node.x - r, node.y - r, node.x + r, node.y + r, fill="#b4befe", outline="#cdd6f4", width=2)
        self.canvas.create_text(node.x, node.y, text=str(node.val), fill="#11111b", font=("Calibri", 12, "bold"))

    def redraw_tree(self):
        self.canvas.delete("all")
        if not self.root_bst: return

        width = self.canvas.winfo_width() or 800
        start_x = width // 2
        start_y = 60
        max_depth = self.get_max_depth(self.root_bst)

        self.calculate_positions(self.root_bst, start_x, start_y, 0, max_depth, width)
        self.draw_nodes_and_edges(self.root_bst)

    # --- UI Event Actions ---
    def add_single_node(self):
        val_str = self.entry_single.get().strip()
        if not val_str.isdigit():
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกตัวเลขจำนวนเต็ม")
            return
        val = int(val_str)
        if self.search_bst(self.root_bst, val):
            messagebox.showwarning("แจ้งเตือน", f" Node ({val}) มีอยู่ในต้นไม้อยู่แล้ว!")
            return

        self.root_bst = self.insert_bst(self.root_bst, val)
        self.entry_single.delete(0, tk.END)
        self.redraw_tree()

    def delete_single_node(self):
        val_str = self.entry_single.get().strip()
        if not val_str.isdigit():
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกตัวเลขจำนวนเต็มที่ต้องการลบ")
            return
        val = int(val_str)
        if not self.search_bst(self.root_bst, val):
            messagebox.showwarning("ไม่พบ Node", f"ไม่พบ Node ({val}) ในต้นไม้")
            return

        self.root_bst = self.delete_bst(self.root_bst, val)
        self.entry_single.delete(0, tk.END)
        self.redraw_tree()

    def build_batch_tree(self):
        raw_input = self.entry_batch.get().strip()
        try:
            vals = [int(v.strip()) for v in raw_input.split(",") if v.strip()]
        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกตัวเลขคั่นด้วยเครื่องหมายจุลภาค (,) ให้ถูกต้อง")
            return

        self.root_bst = None
        for v in vals:
            self.root_bst = self.insert_bst(self.root_bst, v)

        self.redraw_tree()

    def clear_all(self):
        self.root_bst = None
        self.entry_single.delete(0, tk.END)
        self.canvas.delete("all")


# ==========================================
# 4. MAIN APP WITH TABS
# ==========================================
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Binary Search Tree (BST) Studio")
        self.root.geometry("1100x780")
        self.root.configure(bg="#1e1e2e")

        # Style Tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1e1e2e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#313244', foreground='#cdd6f4', padding=[15, 8], font=('Calibri', 11, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#89b4fa')], foreground=[('selected', '#11111b')])

        # Create Notebook Tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab1 = ManualTreeTab(notebook)
        tab2 = AutoBSTTab(notebook)

        notebook.add(tab1, text="  🛠️ หน้าที่ 1: สร้างต้นไม้เอง  ")
        notebook.add(tab2, text="  ⚡ หน้าที่ 2: จัดวางอัตโนมัติ (Auto BST)  ")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()