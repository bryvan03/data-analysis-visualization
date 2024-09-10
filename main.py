import pandas as pd
from tkinter import Tk, filedialog, Label, Button, StringVar, Text, Scrollbar, END
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotly.graph_objects as go
from plotly.offline import plot
from sklearn.linear_model import LinearRegression
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

class DataProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Processor")
        
        self.label = Label(root, text="Upload a CSV file:")
        self.label.pack(pady=10)
        
        self.upload_button = Button(root, text="Browse", command=self.upload_file)
        self.upload_button.pack(pady=5)
        
        self.file_path = StringVar()
        self.file_label = Label(root, textvariable=self.file_path)
        self.file_label.pack(pady=10)
        
        self.process_button = Button(root, text="Process Data", command=self.process_data)
        self.process_button.pack(pady=5)

        # Initialize result_text and scrollbar
        self.result_text = Text(root, wrap='word', height=20, width=80)
        self.result_text.pack(pady=10)
        self.scrollbar = Scrollbar(root, command=self.result_text.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.result_text.config(yscrollcommand=self.scrollbar.set)
        
        self.data = None
    
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path.set(file_path)
            self.data = pd.read_csv(file_path)
            self.result_text.insert(END, f"File loaded: {file_path}\n")
    
    def process_data(self):
        if self.data is not None:
            self.result_text.delete(1.0, END)  # Clear previous results
            
            # Example data processing
            summary = self.data.describe(include='all')
            self.result_text.insert(END, "Data Summary:\n")
            self.result_text.insert(END, f"{summary}\n\n")
            
            # Correlation analysis
            if self.data.select_dtypes(include=[np.number]).shape[1] > 1:
                correlation = self.data.corr()
                self.result_text.insert(END, "Correlation Matrix:\n")
                self.result_text.insert(END, f"{correlation}\n\n")
            else:
                self.result_text.insert(END, "Not enough numeric data for correlation analysis.\n\n")
            
            # Trend detection (Simple linear regression example)
            if 'Year' in self.data.columns and 'Value' in self.data.columns:
                X = self.data[['Year']]
                y = self.data['Value']
                model = LinearRegression()
                model.fit(X, y)
                trend = model.coef_[0]
                self.result_text.insert(END, f"Detected Trend (Year vs Value): {trend:.2f}\n")
            else:
                self.result_text.insert(END, "Year and Value columns are required for trend detection.\n")

            # Visualization
            self.create_visualizations()

            # Generate Report
            self.generate_report()
        else:
            self.result_text.insert(END, "No data to process. Please upload a CSV file first.\n")

    def create_visualizations(self):
        if self.data is not None:
            # Example: Scatter plot using Matplotlib
            if 'Year' in self.data.columns and 'Value' in self.data.columns:
                plt.figure(figsize=(6, 4))
                plt.scatter(self.data['Year'], self.data['Value'], color='blue')
                plt.title('Scatter Plot of Year vs Value')
                plt.xlabel('Year')
                plt.ylabel('Value')
                plt.grid(True)
                plt.savefig("scatter_plot.png")
                plt.close()

            # Example: Interactive plot using Plotly
            if 'Category' in self.data.columns and 'Value' in self.data.columns:
                fig = go.Figure()
                for category in self.data['Category'].unique():
                    category_data = self.data[self.data['Category'] == category]
                    fig.add_trace(go.Scatter(
                        x=category_data['Year'],
                        y=category_data['Value'],
                        mode='lines+markers',
                        name=category
                    ))
                fig.update_layout(title='Interactive Plot of Value by Category',
                                  xaxis_title='Year',
                                  yaxis_title='Value')
                plot(fig, filename='interactive_plot.html', auto_open=False)
        else:
            self.result_text.insert(END, "No data to visualize. Please upload a CSV file first.\n")

    def generate_report(self):
        if self.data is not None:
            # Create a PDF report
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            c.drawString(100, height - 100, "Automated Data Analysis Report")
            
            # Data Summary
            c.drawString(100, height - 130, "Data Summary:")
            summary = self.data.describe(include='all').to_string()
            text = c.beginText(100, height - 150)
            text.setTextOrigin(100, height - 150)
            text.setFont("Helvetica", 10)
            text.textLines(summary)
            c.drawText(text)

            # Add scatter plot
            if os.path.exists("scatter_plot.png"):
                c.drawImage("scatter_plot.png", 100, height - 400, width=400, height=300)

            # Add link to interactive plot
            if os.path.exists("interactive_plot.html"):
                c.drawString(100, height - 730, "Interactive Plot:")
                c.drawString(100, height - 750, "Open 'interactive_plot.html' to view interactive plot.")

            c.save()

            # Save PDF file
            with open("data_analysis_report.pdf", "wb") as f:
                f.write(buffer.getvalue())
            
            self.result_text.insert(END, "Report generated and saved as 'data_analysis_report.pdf'.\n")
        else:
            self.result_text.insert(END, "No data to generate a report. Please upload a CSV file first.\n")

if __name__ == "__main__":
    root = Tk()
    app = DataProcessorApp(root)
    root.mainloop()
