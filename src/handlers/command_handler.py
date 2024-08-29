import re

def process_response(response_text: str):
    # Regular expressions to find !CommandX, &args, and #{emotion}
    command_pattern = r"!Command(\d+)"
    arg_pattern = r"&(\w+)"
    emotion_pattern = r"#(\w+)"
    
    # Find and process command
    command_match = re.search(command_pattern, response_text)
    if command_match:
        command_number = int(command_match.group(1))
        args = re.findall(arg_pattern, response_text)
        emotions = re.findall(emotion_pattern, response_text)
        
        # Call the appropriate command function based on command_number
        if command_number == 1:
            page = args[0] if args else None
            additional_args = args[1:] if len(args) > 1 else None
            page_switching(page, additional_args)
        elif command_number == 2:
            call_and_come()
        elif command_number == 3:
            emotion = args[0] if args else None
            set_emotion(emotion)
        elif command_number == 4:
            seconds = int(args[0]) if len(args) > 0 else None
            minutes = int(args[1]) if len(args) > 1 else None
            hours = int(args[2]) if len(args) > 2 else None
            set_count_down_timer(seconds, minutes, hours)
        elif command_number == 5:
            task_name = args[0] if args else None
            add_todo(task_name)
        elif command_number == 6:
            take_a_photo()
        elif command_number == 7:
            seconds_of_video = int(args[0]) if args else None
            start_recording(seconds_of_video)
        elif command_number == 8:
            end_recording()

        if emotions:
            set_emotion(emotions[0])
        
        # Remove the processed parts from response_text
        response_text = re.sub(command_pattern, '', response_text)
        response_text = re.sub(arg_pattern, '', response_text)
        response_text = re.sub(emotion_pattern, '', response_text)
    
    # Clean up the remaining text
    leftover_text = response_text.strip()
    
    return leftover_text
