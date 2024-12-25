from fpdf import FPDF
import os
from datetime import datetime
import numpy as np


class ReportGenerator:
    def __init__(self, snapshots_dir, reports_dir):
        self.snapshots_dir = snapshots_dir
        self.reports_dir = reports_dir

    def generate_report(self, glued_graph_instances, graph1_instances, graph2_instances):
        # Initialize PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Create directories if they don't exist
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        # Header details
        university_logo = "images/university_logo.png"
        sbme_logo = "images/sbme_logo.jpg"

        for i, glued_instance in enumerate(glued_graph_instances):
            # Add a new page for each glued graph instance
            pdf.add_page()

            # Header with logos and title
            pdf.image(university_logo, 10, 10, 30)
            pdf.image(sbme_logo, 170, 10, 30)
            pdf.set_font("Arial", size=20)
            pdf.cell(0, 40, f"Signal Analysis Report - Instance {i + 1}", ln=True, align="C")

            # Save and add snapshot of the glued graph instance
            snapshot_filename = os.path.join(self.snapshots_dir, f"glued_graph_{i + 1}.png")
            self.save_graph_snapshot(glued_instance, snapshot_filename)
            pdf.image(snapshot_filename, x=10, y=60, w=190)

            # Add statistical tables for graph1, graph2, and gluedGraph
            pdf.ln(120)  # Move below the snapshot
            self.add_statistics_table(pdf, graph1_instances[i], "Graph1 Statistics")
            self.add_statistics_table(pdf, graph2_instances[i], "Graph2 Statistics")
            self.add_statistics_table(pdf, glued_instance, "Glued Graph Statistics")

        # Save the PDF report
        report_filename = os.path.join(
            self.reports_dir,
            f"report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
        )
        pdf.output(report_filename)
        print(f"Report saved at {report_filename}")

    def save_graph_snapshot(self, graph_data, filename):
        import matplotlib.pyplot as plt

        # Unpack graph data
        x_vals, y_vals = graph_data

        # Plot and save as an image
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, color="blue", label="Signal")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        plt.title("Graph Snapshot")
        plt.legend()
        plt.savefig(filename)
        plt.close()

    def add_statistics_table(self, pdf, graph_data, title):
        x_vals, y_vals = graph_data

        # Calculate statistics
        mean = np.mean(y_vals)
        std_dev = np.std(y_vals)
        max_val = np.max(y_vals)
        min_val = np.min(y_vals)

        # Add the table to the PDF
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, title, ln=True)
        pdf.cell(0, 10, f"Mean: {mean:.2f}", ln=True)
        pdf.cell(0, 10, f"Standard Deviation: {std_dev:.2f}", ln=True)
        pdf.cell(0, 10, f"Maximum: {max_val:.2f}", ln=True)
        pdf.cell(0, 10, f"Minimum: {min_val:.2f}", ln=True)
        pdf.ln(10)  # Add spacing after the table
