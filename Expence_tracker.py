import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import os
import csv

class IndianExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f2f5')
        
        self.colors = {
            'primary': "#192131",  
            'secondary': '#138808',  
            'accent': '#0066b2',  
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'background': '#f8f9fa'
        }

        self.currency = '₹'
        
        self.expenses = []
        self.categories = ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
                          'Bills & Utilities', 'Healthcare', 'Education', 'Groceries',
                          'Travel', 'Gifts', 'Personal Care', 'Others']
        self.load_data()
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
   
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header = tk.Label(main_frame, text=f"{self.currency} EXPENSE TRACKER", 
                         font=('Arial', 22, 'bold'), 
                         bg=self.colors['primary'], fg='white')
        header.pack(fill=tk.X, pady=(0, 20))
        
        input_frame = tk.Frame(main_frame, bg=self.colors['light'], relief=tk.RAISED, bd=2)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        tk.Label(input_frame, text=f"Amount ({self.currency}):", bg=self.colors['light']).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.amount_entry = tk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(input_frame, text="Category:", bg=self.colors['light']).grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, state="readonly", width=15)
        self.category_combo.grid(row=0, column=3, padx=10, pady=10)
        self.category_combo.current(0)
        
        tk.Label(input_frame, text="Description:", bg=self.colors['light']).grid(row=0, column=4, padx=10, pady=10, sticky=tk.W)
        self.desc_entry = tk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=5, padx=10, pady=10)
        
        tk.Label(input_frame, text="Date:", bg=self.colors['light']).grid(row=0, column=6, padx=10, pady=10, sticky=tk.W)
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=7, padx=10, pady=10)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
   
        add_btn = tk.Button(input_frame, text="➕ Add Expense", command=self.add_expense,
                           bg=self.colors['secondary'], fg='white', font=('Arial', 10, 'bold'))
        add_btn.grid(row=0, column=8, padx=20, pady=10)
      
        stats_frame = tk.Frame(main_frame, bg=self.colors['light'], relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.total_label = tk.Label(stats_frame, text=f"Total: {self.currency}0.00", 
                                   font=('Arial', 12, 'bold'), bg=self.colors['light'])
        self.total_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.count_label = tk.Label(stats_frame, text="Transactions: 0", 
                                   font=('Arial', 12), bg=self.colors['light'])
        self.count_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.avg_label = tk.Label(stats_frame, text=f"Average: {self.currency}0.00", 
                                 font=('Arial', 12), bg=self.colors['light'])
        self.avg_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.today_label = tk.Label(stats_frame, text=f"Today: {self.currency}0.00", 
                                   font=('Arial', 12), bg=self.colors['light'])
        self.today_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Button(stats_frame, text="📊 Export CSV", command=self.export_csv,
                 bg=self.colors['primary'], fg='white').pack(side=tk.RIGHT, padx=10, pady=10)
        tk.Button(stats_frame, text="📈 Report", command=self.generate_report,
                 bg=self.colors['accent'], fg='white').pack(side=tk.RIGHT, padx=10, pady=10)
        tk.Button(stats_frame, text="🔄 Reset", command=self.reset_all,
                 bg=self.colors['danger'], fg='white').pack(side=tk.RIGHT, padx=10, pady=10)
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('Date', 'Category', 'Description', 'Amount')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column('Date', width=100)
            self.tree.column('Category', width=120)
            self.tree.column('Description', width=200)
            self.tree.column('Amount', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Button(main_frame, text="🗑️ Delete Selected", command=self.delete_expense,
                 bg=self.colors['danger'], fg='white').pack(pady=10)
    
    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_combo.get()
            description = self.desc_entry.get()
            date_str = self.date_entry.get()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format!")
                return
            
            if not description:
                description = f"{category} Expense"
            
            expense = {
                'amount': amount,
                'category': category,
                'description': description,
                'date': date_str,
                'timestamp': datetime.now().isoformat()
            }
            
            self.expenses.append(expense)
            self.save_data()
            self.update_display()
            self.amount_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            messagebox.showinfo("Success", "Expense added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")
    
    def update_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sorted_expenses = sorted(self.expenses, 
                                key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), 
                                reverse=True)
        for expense in sorted_expenses[:100]:  
            self.tree.insert('', 'end', values=(
                expense['date'],
                expense['category'],
                expense['description'][:50],
                f"{self.currency}{expense['amount']:,.2f}"
            ))
        if self.expenses:
            total = sum(e['amount'] for e in self.expenses)
            count = len(self.expenses)
            avg = total / count
            today = datetime.now().strftime("%Y-%m-%d")
            today_total = sum(e['amount'] for e in self.expenses if e['date'] == today)
            
            self.total_label.config(text=f"Total: {self.currency}{total:,.2f}")
            self.count_label.config(text=f"Transactions: {count}")
            self.avg_label.config(text=f"Average: {self.currency}{avg:,.2f}")
            self.today_label.config(text=f"Today: {self.currency}{today_total:,.2f}")
        else:
            self.total_label.config(text=f"Total: {self.currency}0.00")
            self.count_label.config(text="Transactions: 0")
            self.avg_label.config(text=f"Average: {self.currency}0.00")
            self.today_label.config(text=f"Today: {self.currency}0.00")
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected expense?"):
            items_to_delete = []
            for item in selected:
                values = self.tree.item(item)['values']
                items_to_delete.append(item)
                amount_str = str(values[3])
                amount_clean = amount_str.replace(self.currency, '').replace(',', '').strip()
            
                for i, expense in enumerate(self.expenses):
                    try:
                        if (abs(float(expense['amount']) - float(amount_clean)) < 0.01 and 
                            expense['category'] == values[1] and
                            expense['date'] == values[0]):
                            del self.expenses[i]
                            break
                    except (ValueError, KeyError):
                        continue
            for item in items_to_delete:
                self.tree.delete(item)
            
            self.save_data()
            self.update_display()
    
    def export_csv(self):
        if not self.expenses:
            messagebox.showwarning("Warning", "No expenses to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    if self.expenses:
                        fieldnames = self.expenses[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.expenses)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def generate_report(self):
        if not self.expenses:
            messagebox.showwarning("Warning", "No expenses to generate report!")
            return
        
        report = "=" * 60 + "\n"
        report += "EXPENSE TRACKER REPORT\n"
        report += "=" * 60 + "\n\n"
        
        total = sum(e['amount'] for e in self.expenses)
        report += f"Total Expenses: {self.currency}{total:,.2f}\n"
        report += f"Number of Transactions: {len(self.expenses)}\n"
        report += f"Average per Transaction: {self.currency}{total/len(self.expenses):,.2f}\n\n"
      
        report += "CATEGORY BREAKDOWN:\n"
        report += "-" * 50 + "\n"
        
        category_totals = {}
        for expense in self.expenses:
            cat = expense['category']
            category_totals[cat] = category_totals.get(cat, 0) + expense['amount']
        
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            report += f"{category:20} {self.currency}{amount:12,.2f} ({percentage:5.1f}%)\n"
        
        messagebox.showinfo("Expense Report", report)
    
    def reset_all(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to delete ALL expenses?\nThis action cannot be undone!"):
            self.expenses = []
            self.save_data()
            self.update_display()
            messagebox.showinfo("Reset Complete", "All expenses have been cleared.")
    
    def save_data(self):
        try:
            with open('expenses_india.json', 'w') as f:
                json.dump(self.expenses, f, indent=4)
        except:
            pass
    
    def load_data(self):
        try:
            if os.path.exists('expenses_india.json'):
                with open('expenses_india.json', 'r') as f:
                    self.expenses = json.load(f)
        except:
            self.expenses = []

def main():
    root = tk.Tk()
    app = IndianExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()