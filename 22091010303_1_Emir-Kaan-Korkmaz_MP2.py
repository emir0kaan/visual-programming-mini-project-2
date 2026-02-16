import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


class OlympicsUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Olympics 2024")
        self.geometry("600x800")
        self.minsize(600, 800)

        # Data Holders
        self.medal_map = {}
        self.current_fig = None

        # Grid 
        container = ttk.Frame(self, padding=20)
        container.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        for c in range(3):
            container.grid_columnconfigure(c, weight=1)

        # Tittle
        title = ttk.Label(container, text="Olympics 2024", font=("Arial", 26))
        title.grid(row=0, column=0, columnspan=3, pady=(10, 10), sticky="n")


        # Canvas 
        canvas = tk.Canvas(container, width=420, height=200, highlightthickness=0)
        canvas.grid(row=1, column=0, columnspan=3, pady=(0, 22))


        def draw_ring(cx, cy, r, color, width=10):
            
            canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=color, width=width
            )

        #  Rings positions 
        draw_ring(140, 85, 55, "blue")   
        draw_ring(210, 85, 55, "black")    
        draw_ring(280, 85, 55, "red")  
        draw_ring(175, 125, 55, "yellow") 
        draw_ring(245, 125, 55, "green") 

        # URL
        self.url_var = tk.StringVar(
            value="https://www.bbc.com/sport/olympics/paris-2024/medals"
        )
        url_entry = ttk.Entry(container, textvariable=self.url_var, width=55)
        url_entry.grid(row=2, column=0, columnspan=3, pady=(0, 10), ipady=4, sticky="ew")

        # List Button
        show_list_btn = ttk.Button(container, text="show list", command=self.on_show_list)
        show_list_btn.grid(row=3, column=0, columnspan=3, pady=(0, 14))

        # ListBox
        list_frame = ttk.Frame(container)
        list_frame.grid(row=4, column=0, columnspan=3, pady=(0, 18))

        self.listbox = tk.Listbox(list_frame, height=12, width=34)
        self.listbox.grid(row=0, column=0)

        # Instruction Label 
        info = ttk.Label(container, text="Click on a country to see detailed medals:")
        info.grid(row=5, column=0, columnspan=3, pady=(0, 10))

        # Button
        btn1 = ttk.Button(container, text="Show Chart of selected country", command=self.on_show_country_chart)
        btn1.grid(row=6, column=0, columnspan=3, pady=(0, 12), ipadx=10, ipady=4)

        btn2 = ttk.Button(
            container,
            text="Show top 10 performing countries analytics",
            command=self.on_show_top10_analytics
        )
        btn2.grid(row=7, column=0, columnspan=3, pady=(0, 8), ipadx=10, ipady=4)

        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(9, weight=1)

    # Button: Show List
    def on_show_list(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        try:
            self.medal_map = self.scrape_medals_map(url)
        except Exception as e:
            messagebox.showerror("Scraping Error", f"Could not scrape medal data:\n{e}")
            return

        countries = sorted(self.medal_map.keys(), key=lambda x: x.upper())

        self.listbox.delete(0, tk.END)
        for c in countries:
            self.listbox.insert(tk.END, c)

    # Show Chart
    def on_show_country_chart(self):
        if not self.medal_map:
            messagebox.showwarning("No Data", "Please click 'show list' first.")
            return

        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a country.")
            return

        country = self.listbox.get(sel[0]).strip().upper()
        if country not in self.medal_map:
            messagebox.showerror("Error", "Selected country not found in data.")
            return

        g, s, b = self.medal_map[country]

        # Close previous chart if any
        if self.current_fig is not None:
            try:
                plt.close(self.current_fig)
            except Exception:
                pass
            self.current_fig = None

        fig = plt.figure()
        plt.bar(
            ["Gold", "Silver", "Bronze"],
            [g, s, b],
            color=["gold", "white", "red"],
            edgecolor="black"
        )
        plt.title(f"Medals Count for {country}")
        plt.xlabel("Medal Type")
        plt.ylabel("Count")
        plt.grid(axis="y", linestyle="--", alpha=0.4)

        self.current_fig = fig
        plt.show()


    def on_show_top10_analytics(self):
        if not self.medal_map:
            messagebox.showwarning("No Data", "Please click 'show list' first.")
            return

        # Build list with totals
        data = []
        for country, (g, s, b) in self.medal_map.items():
            total = g + s + b
            data.append((country, g, s, b, total))

        data.sort(key=lambda x: x[4], reverse=True)
        top10 = data[:10]

        countries = [x[0] for x in top10]
        golds = [x[1] for x in top10]
        silvers = [x[2] for x in top10]
        bronzes = [x[3] for x in top10]
        totals = [x[4] for x in top10]

        # Close previous chart if any
        if self.current_fig is not None:
            try:
                plt.close(self.current_fig)
            except Exception:
                pass
            self.current_fig = None

        fig, axs = plt.subplots(2, 2, figsize=(14, 10))

        axs[0, 0].pie(golds, labels=countries, autopct="%1.1f%%", startangle=140)
        axs[0, 0].set_title("Gold Medals")

        axs[0, 1].pie(silvers, labels=countries, autopct="%1.1f%%", startangle=140)
        axs[0, 1].set_title("Silver Medals")

        axs[1, 0].pie(bronzes, labels=countries, autopct="%1.1f%%", startangle=140)
        axs[1, 0].set_title("Bronze Medals")

        axs[1, 1].plot(countries, totals, marker="o")
        axs[1, 1].set_title("Total Medals")
        axs[1, 1].set_xlabel("Country")
        axs[1, 1].set_ylabel("Number of Medals")
        axs[1, 1].tick_params(axis="x", rotation=45)

        plt.tight_layout()
        self.current_fig = fig
        plt.show()

    #COUNTRY + MEDALS 
    def scrape_medals_map(self, url: str) -> dict:
        r = requests.get(url)
        r.raise_for_status()
        html = r.text

        medal_map = self._medals_from_table(html)
        if medal_map:
            return medal_map

        raise ValueError("Could not extract medal counts (gold/silver/bronze) from the page.")

    def _medals_from_table(self, html: str) -> dict:
        try:
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table")
            if not table:
                return {}

            def to_int(x):
                try:
                    return int(x)
                except Exception:
                    return 0

            medal_map = {}

            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 5:
                    continue

                first = tds[0].get_text(" ", strip=True)

            
                if first.isdigit():
                    country_raw = tds[1].get_text(" ", strip=True)
                    g_txt = tds[2].get_text(" ", strip=True)
                    s_txt = tds[3].get_text(" ", strip=True)
                    b_txt = tds[4].get_text(" ", strip=True)
                else:
                    country_raw = tds[0].get_text(" ", strip=True)
                    g_txt = tds[1].get_text(" ", strip=True)
                    s_txt = tds[2].get_text(" ", strip=True)
                    b_txt = tds[3].get_text(" ", strip=True)

                if not country_raw:
                    continue

                parts = country_raw.split(" ", 1)
                if len(parts) == 2 and len(parts[0]) == 3:
                    country = parts[1]
                else:
                    country = country_raw

                country = country.strip().upper()

                g = to_int(g_txt)
                s = to_int(s_txt)
                b = to_int(b_txt)

                medal_map[country] = (g, s, b)

            return medal_map
        except Exception:
            return {}


if __name__ == "__main__":
    app = OlympicsUI()
    app.mainloop()
