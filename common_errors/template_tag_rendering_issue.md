# Django Template Tag Rendering Issue

## Problem
In the browser, you see the raw template code (e.g., `{{ booking.room.room_number }}`) displayed literally, instead of the actual data (e.g., "101" or "Suite A").

## Symptoms
- The page renders, but specific parts show curly braces `{{ ... }}`.
- No Python traceback or server error (500) occurs; it just looks wrong on the screen.

## Cause
This usually happens when a Django template variable tag is split across multiple lines in the HTML file. While Django is generally flexible, splitting the opening `{{` and closing `}}` or the variable name across lines can sometimes prevent the template engine from recognizing it as a variable to be processed, causing it to be treated as plain text.

**Incorrect Code (Split Logic):**
This often happens in long lines, like in alert messages:
```html
<!-- The line break inside the tag causes the issue -->
(Room {{ 
    booking.room.room_number }})
```

**Specific Example from Project (Red Alert Box):**
You saw this error in the "Overdue Booking" alert on the dashboard:
`Action Required: 2 Overdue Booking(s)`
`Idiris Abdi Aadan (Room {{ booking.room.room_number }}) ...`

This happened because the code for the room display was split:
```html
<span class="font-bold">{{ booking.guest.full_name }}</span> (Room {{
    booking.room.room_number }})
```

## Solution
Always keep the entire template variable tag on a single line.

**Correct Code:**
```html
<!-- Correct: All on one line -->
(Room {{ booking.room.room_number }})
```

## Prevention
When using auto-formatters (like Prettier or HTML formatters) in VS Code, be careful that they don't aggressively wrap long lines in a way that breaks Django template tags. If a line is too long, try to break the HTML structure *around* the tag, not *inside* the tag.
