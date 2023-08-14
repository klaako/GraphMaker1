import pandas as pd
import matplotlib.pyplot as plt
import io
import np
import clipboard
from PIL import Image
from io import BytesIO
import os

def get_filename():
    """Prompt the user for the output filename."""
    return input("Enter the desired filename (without extension): ") + ".png"

def select_color_scheme():
    """Prompt the user to select a color scheme from a provided list."""
    color_maps = ["viridis", "plasma", "inferno", "magma", "cividis"]
    print("\nSelect a color scheme by number:")
    for i, cmap in enumerate(color_maps, 1):
        print(f"{i}. {cmap}")
    selection = int(input("Enter your choice (1-5): "))
    return color_maps[selection - 1]

def get_graph_title():
    """Prompt the user for the title of the graph."""
    return input("Enter the desired title for the graph: ")

def select_background_color():
    """Prompt the user to select a background color for the graph."""
    options = {
        "1": "Default",
        "2": "Pro"
    }
    colors = {
        "Default": "white",
        "Pro": "#e7e7e6"
    }
    print("\nSelect a background color by number:")
    for key, value in options.items():
        print(f"{key}. {value}")
    selection = input("Enter your choice (1-2): ")
    return colors[options[selection]]

def input_csv_data():
    """Prompt the user to input CSV data."""
    print("\nEnter your CSV data (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return "\n".join(lines)

def select_graph_type():
    """Prompt the user to select a type of graph from a provided list."""
    graph_types = ["Stacked Bar Graph", "Line Graph", "Area Graph"]
    print("\nSelect a type of graph by number:")
    for i, gtype in enumerate(graph_types, 1):
        print(f"{i}. {gtype}")
    selection = int(input("Enter your choice (1-3): "))
    return graph_types[selection - 1]

def currency_formatter(x, pos):
    """Format y-ticks with currency symbol."""
    return f"${x:,.0f}"

def copy_to_clipboard(fig):
    """Copy the provided figure to the clipboard (macOS)."""
    temp_filename = "temp_clipboard_image.png"
    fig.savefig(temp_filename, format="png", bbox_inches='tight', facecolor=fig.get_facecolor())
    
    cmd = f'''
    osascript -e 'set the clipboard to (read (POSIX file "{temp_filename}") as TIFF picture)'
    '''
    os.system(cmd)
    os.remove(temp_filename)

# Get user inputs
filename = get_filename()
color_scheme = select_color_scheme()
graph_type = select_graph_type()
graph_title = get_graph_title()
background_color = select_background_color()
data = input_csv_data()

# Parse and plot the CSV data
df = pd.read_csv(io.StringIO(data), parse_dates=["billing_period"])
date_col = df.columns[0] # assuming the first column is the date column
category_col = df.columns[1] # assuming the second column is the category column
value_col = df.columns[-1] # assuming the last column is the value column
grouped_df = df.groupby([date_col, category_col]).sum()[value_col].unstack().fillna(0)


fig, ax = plt.subplots(figsize=(12, 8))
colors = plt.get_cmap(color_scheme)(np.linspace(0, 1, len(grouped_df.columns)))
fig.patch.set_facecolor(background_color)
ax.set_facecolor(background_color)

if graph_type == "Stacked Bar Graph":
    grouped_df.plot(kind="bar", stacked=True, ax=ax, color=colors)
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy() 
        ax.annotate(f'${height:,.0f}', (x + width/2, y + height/2), ha='center', va='center', color='white', fontsize=8)
elif graph_type == "Line Graph":
    grouped_df.plot(kind="line", ax=ax, color=colors, marker='o')
    for x, y in zip(range(len(grouped_df)), grouped_df.values):
        ax.annotate(f'${y[-1]:,.0f}', (x, y[-1]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)
elif graph_type == "Area Graph":
    grouped_df.plot(kind="area", ax=ax, color=colors, alpha=0.7)
    for x, y in zip(range(len(grouped_df)), grouped_df.values):
        ax.annotate(f'${y[-1]:,.0f}', (x, y[-1]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

ax.yaxis.set_major_formatter(plt.FuncFormatter(currency_formatter))
if pd.api.types.is_datetime64_any_dtype(df[date_col].dtype):  # Check if the date column is of datetime type
    ax.set_xticklabels(grouped_df.index.strftime('%B'))
else:
    ax.set_xticklabels(grouped_df.index)
plt.ylabel(value_col)
plt.xlabel(date_col)
plt.xticks(rotation=45)
plt.legend(title="Product Family", bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()
plt.savefig(filename, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"Graph saved as {filename}")
copy_to_clipboard(fig)
print("Graph copied to clipboard!")
plt.show()
