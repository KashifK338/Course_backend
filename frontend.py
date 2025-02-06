import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import webbrowser
from PIL import Image, ImageTk
import io
import json

def fetch_course():
    """ Fetch AI-generated course outline and YouTube videos (per lesson). """
    topic = entry.get().strip()
    if not topic:
        messagebox.showerror("Error", "Please enter a topic")
        return

    url_course = "http://127.0.0.1:8000/generate-course"
    payload = {"topic": topic}

    try:
        # Fetch course outline and lesson-level video data from the backend
        response_course = requests.post(url_course, json=payload)
        response_course.raise_for_status()
        data = response_course.json()
        course_outline = data.get("course_outline", {})
        lesson_videos = data.get("lesson_videos", [])

        # Display Course Outline (Gemini AI Answer) in the right panel
        course_text.config(state=tk.NORMAL)
        course_text.delete(1.0, tk.END)
        course_text.insert(tk.END, json.dumps(course_outline, indent=2) + "\n")
        course_text.config(state=tk.DISABLED)

        # Display YouTube Videos (per lesson) in the left scrollable panel
        display_videos(lesson_videos)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch course: {e}")

def display_videos(lesson_videos):
    """ Display modules and their lessons with YouTube videos in the left panel. """
    # Clear previous results in the scrollable frame
    for widget in left_frame.winfo_children():
        widget.destroy()

    if not lesson_videos:
        tk.Label(left_frame, text="No videos found.", fg="red").pack(pady=10)
        return

    for module_data in lesson_videos:
        module_title = module_data.get("module_title", "Module")
        module_desc = module_data.get("description", None)  # Optional module description

        # Module Header
        module_label = tk.Label(left_frame, text=module_title, font=("Arial", 11, "bold"), fg="green")
        module_label.pack(anchor="w", padx=5, pady=(10, 0))
        
        # Module Description (if available)
        if module_desc:
            desc_label = tk.Label(left_frame, text=module_desc, font=("Arial", 10), fg="black", wraplength=320, justify="left")
            desc_label.pack(anchor="w", padx=10, pady=(2, 5))
        
        # Iterate over each lesson in the module
        lessons = module_data.get("lessons", [])
        for lesson_data in lessons:
            lesson_title = lesson_data.get("lesson_title", "Lesson")
            lesson_label = tk.Label(left_frame, text=lesson_title, font=("Arial", 10, "italic"))
            lesson_label.pack(anchor="w", padx=15, pady=(5, 0))
            
            videos = lesson_data.get("videos", [])
            if videos:
                for video in videos:
                    display_video(video)
            else:
                tk.Label(left_frame, text="No relevant video found for this lesson.", fg="red").pack(anchor="w", padx=25)

def display_video(video):
    """ Display video thumbnail and title in the left panel. """
    thumbnail_url = f"https://img.youtube.com/vi/{video['video_id']}/hqdefault.jpg"
    
    try:
        response = requests.get(thumbnail_url, timeout=10)
        response.raise_for_status()
        image_data = io.BytesIO(response.content)
        img = Image.open(image_data).resize((160, 90))
        thumbnail = ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading thumbnail: {e}")
        thumbnail = None

    frame = tk.Frame(left_frame)
    frame.pack(pady=5, anchor="w", padx=25)

    if thumbnail:
        btn = tk.Button(frame, image=thumbnail, command=lambda: open_link(video["url"]), bd=0)
        btn.image = thumbnail  # Keep a reference to avoid garbage collection
        btn.pack(side=tk.LEFT, padx=5)

    title_label = tk.Label(frame, text=video["title"], fg="blue", cursor="hand2", wraplength=250, justify="left")
    title_label.pack(side=tk.LEFT)
    title_label.bind("<Button-1>", lambda e: open_link(video["url"]))

def open_link(url):
    """ Open the given URL in the default web browser. """
    webbrowser.open(url)

# Set up the Tkinter UI
root = tk.Tk()
root.title("AI Course Generator")
root.geometry("800x600")

# Input Section
input_frame = tk.Frame(root)
input_frame.pack(fill=tk.X, pady=5)

tk.Label(input_frame, text="Enter Topic:").pack(side=tk.LEFT, padx=5)
entry = tk.Entry(input_frame, width=50)
entry.pack(side=tk.LEFT, padx=5)
tk.Button(input_frame, text="Generate Course", command=fetch_course).pack(side=tk.LEFT, padx=5)

# Create Two Panels (Left: Videos for Lessons, Right: Course Outline)
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# --- Scrollable Left Panel Setup ---
# Create a canvas for the left panel
left_canvas = tk.Canvas(main_frame, width=350)
left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

# Add a vertical scrollbar linked to the canvas
v_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=left_canvas.yview)
v_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

left_canvas.configure(yscrollcommand=v_scrollbar.set)

# Create a frame inside the canvas to hold the video widgets
left_frame = tk.Frame(left_canvas)
left_canvas.create_window((0, 0), window=left_frame, anchor="nw")

def on_frame_configure(event):
    left_canvas.configure(scrollregion=left_canvas.bbox("all"))

left_frame.bind("<Configure>", on_frame_configure)

# --- Right Panel for Course Outline ---
right_panel = tk.Frame(main_frame, width=400)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

tk.Label(right_panel, text="📘 Gemini AI Course Outline", font=("Arial", 12, "bold")).pack(pady=5)
course_text = scrolledtext.ScrolledText(right_panel, width=50, height=25, state=tk.DISABLED)
course_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()
