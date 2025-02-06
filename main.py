from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from ai_service import generate_course_outline
from youtube_service import search_youtube_videos

app = FastAPI()

class CourseRequest(BaseModel):
    topic: str

@app.post("/generate-course")
async def generate_course(request: CourseRequest):
    """
    API endpoint to generate a course outline and fetch related YouTube videos for each lesson.
    """
    # Generate the course outline using Gemini AI
    course_outline = generate_course_outline(request.topic)
    
    lesson_videos = []
    
    # Check if course_outline contains modules and iterate through them
    if "modules" in course_outline:
        for module in course_outline["modules"]:
            module_title = module.get("module_title", request.topic)
            lessons_video_data = []
            for lesson in module.get("lessons", []):
                lesson_title = lesson.get("lesson_title", request.topic)
                # Search for a video using the lesson title
                videos = search_youtube_videos(lesson_title, max_results=1)
                lessons_video_data.append({
                    "lesson_title": lesson_title,
                    "videos": videos
                })
            lesson_videos.append({
                "module_title": module_title,
                "lessons": lessons_video_data
            })
    else:
        # Fallback: if no modules exist, search by the overall topic.
        videos = search_youtube_videos(request.topic, max_results=5)
        lesson_videos.append({
            "module_title": request.topic,
            "lessons": [{
                "lesson_title": request.topic,
                "videos": videos
            }]
        })
    
    return {
        "course_outline": course_outline,
        "lesson_videos": lesson_videos
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
