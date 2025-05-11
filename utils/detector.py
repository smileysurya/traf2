import cv2
import numpy as np
import os
import time
import random  # For simulation purposes

def detect_violations(video_path, output_folder):
    """
    Detect traffic violations in a video.
    
    For this quick implementation, we'll simulate detections
    rather than implementing full ML/DL models.
    
    Args:
        video_path: Path to input video
        output_folder: Folder to save evidence images
        
    Returns:
        List of detected violations
    """
    print(f"Processing video: {video_path}")
    
    violations = []
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Since we're simulating, we'll process only a subset of frames
    # We'll take approximately 10 frames evenly distributed
    frames_to_process = min(10, frame_count)
    frame_interval = max(1, frame_count // frames_to_process)
    
    # Violation types for simulation
    violation_types = [
        'speeding',
        'red_light',
        'lane_violation',
        'illegal_stopping'
    ]
    
    frame_number = 0
    processed_count = 0
    
    while cap.isOpened() and processed_count < frames_to_process:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process only selected frames
        if frame_number % frame_interval == 0:
            # Simulated processing: randomly decide if this frame has a violation
            if random.random() > 0.5:  # 50% chance of violation
                violation_type = random.choice(violation_types)
                
                # Save the frame as evidence
                evidence_path = os.path.join(output_folder, f"violation_{frame_number}.jpg")
                cv2.imwrite(evidence_path, frame)
                
                # Simulate detection by drawing on frame
                processed_frame = frame.copy()
                
                # Different markings based on violation type
                if violation_type == 'speeding':
                    # Draw rectangle around a random "car"
                    h, w = frame.shape[:2]
                    x, y = random.randint(w//4, 3*w//4), random.randint(h//2, 2*h//3)
                    width, height = random.randint(100, 200), random.randint(80, 150)
                    cv2.rectangle(processed_frame, (x, y), (x+width, y+height), (0, 0, 255), 3)
                    cv2.putText(processed_frame, "Speed: 78 km/h", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    details = {'speed': 78, 'limit': 50}
                    
                elif violation_type == 'red_light':
                    # Simulate red light detection
                    h, w = frame.shape[:2]
                    x, y = random.randint(w//4, 3*w//4), random.randint(h//3, h//2)
                    cv2.circle(processed_frame, (x, y), 30, (0, 0, 255), -1)  # Red traffic light
                    x_car, y_car = x+80, y+100
                    cv2.rectangle(processed_frame, (x_car-50, y_car-30), (x_car+50, y_car+30), (255, 0, 0), 3)
                    cv2.line(processed_frame, (0, y+60), (w, y+60), (255, 255, 255), 2)  # Stop line
                    details = {'intersection_id': 'INT-2023'}
                    
                elif violation_type == 'lane_violation':
                    # Draw lane lines and car crossing them
                    h, w = frame.shape[:2]
                    # Lane lines
                    cv2.line(processed_frame, (w//3, 0), (w//3, h), (255, 255, 255), 2)
                    cv2.line(processed_frame, (2*w//3, 0), (2*w//3, h), (255, 255, 255), 2)
                    # Car crossing lane
                    x, y = w//3 - 25, random.randint(h//3, 2*h//3)
                    cv2.rectangle(processed_frame, (x, y), (x+100, y+50), (0, 165, 255), 3)
                    cv2.arrowLine(processed_frame, (x-50, y+25), (x+150, y+25), (0, 165, 255), 2)
                    details = {'lane_change': 'improper'}
                    
                else:  # illegal_stopping
                    h, w = frame.shape[:2]
                    x, y = random.randint(w//4, 3*w//4), random.randint(h//2, 2*h//3)
                    cv2.rectangle(processed_frame, (x, y), (x+150, y+80), (255, 0, 255), 3)
                    cv2.putText(processed_frame, "No Stopping Zone", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
                    details = {'duration': '2m 15s', 'zone': 'no_stopping'}
                
                # Save the processed frame with annotations
                processed_path = os.path.join(output_folder, f"violation_{frame_number}_marked.jpg")
                cv2.imwrite(processed_path, processed_frame)
                
                # Create violation record
                violation = {
                    'id': len(violations) + 1,
                    'type': violation_type,
                    'frame': frame_number,
                    'timestamp': frame_number / fps,
                    'evidence_path': os.path.basename(evidence_path),
                    'processed_path': os.path.basename(processed_path),
                    'details': details
                }
                
                violations.append(violation)
            
            processed_count += 1
        
        frame_number += 1
    
    cap.release()
    print(f"Detected {len(violations)} violations")
    
    return violations