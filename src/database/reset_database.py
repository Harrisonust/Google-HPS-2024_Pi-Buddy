import sqlite3
import os


def reset_db(reset_todo=False, reset_images=False, reset_videos=False):
    
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()

    if reset_todo:
        _reset_todo(conn, cursor)
    if reset_images:
        _reset_images(conn, cursor)
    if reset_videos:
        _reset_videos(conn, cursor)


def _reset_todo(conn, cursor):
    try:
        # Create todo SQL table
        cursor.execute(
            '''
            DROP TABLE IF EXISTS todo;
            '''
        )
        conn.commit()
        cursor.execute(
            '''
            CREATE TABLE todo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                due_date DATE,
                is_active INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            );
            '''
        )
        conn.commit()
        
    except Exception as e:
        print(f'An error ocurred when resetting todo: {e}')


def _reset_images(conn, cursor):
    try:
        # Create images SQL table
        cursor.execute(
            '''
            DROP TABLE IF EXISTS saved_imgs;
            '''
        )
        conn.commit()
        cursor.execute(
            '''
            CREATE TABLE saved_imgs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                img_name TEXT NOT NULL,
                img_path TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            '''
        )
        conn.commit()
        
        # Ensure the images directory is created
        video_path = './images/'
        if not os.path.exists(video_path):
            os.makedirs(video_path)
            print(f"Directory '{video_path}' created.")
        else:
            print(f"Directory '{video_path}' already exists.")
            image_files = [os.path.relpath(os.path.join(video_path, f), start=video_path) 
                    for f in os.listdir(video_path) if os.path.isfile(os.path.join(video_path, f))]
            
            # Write existing files into SQL table
            for image_file in image_files:
                cursor.execute(
                    f'''
                    INSERT INTO saved_imgs (img_name, img_path)
                    VALUES (\'{image_file.split("/")[-1]}\', \'{image_file}\');
                    '''
                )
                conn.commit()
        
    except Exception as e:
        print(f'An error occurred when resetting images')
    
    
def _reset_videos(conn, cursor):
    try:
        # Create images SQL table
        cursor.execute(
            '''
            DROP TABLE IF EXISTS saved_videos;
            '''
        )
        conn.commit()
        cursor.execute(
            '''
            CREATE TABLE saved_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_name TEXT NOT NULL,
                video_path TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            '''
        )
        conn.commit()
        
        # Ensure the videos directory is created
        video_path = './videos/'
        if not os.path.exists(video_path):
            os.makedirs(video_path)
            print(f"Directory '{video_path}' created.")
        else:
            print(f"Directory '{video_path}' already exists.")
            video_files = [os.path.relpath(os.path.join(video_path, f), start=video_path) 
                    for f in os.listdir(video_path) if os.path.isfile(os.path.join(video_path, f))]
            
            # Write existing files into SQL table
            for video_file in video_files:
                cursor.execute(
                    f'''
                    INSERT INTO saved_videos (video_name, video_path)
                    VALUES (\'{video_file.split("/")[-1]}\', \'{video_file}\');
                    '''
                )
                conn.commit()
        
    except Exception as e:
        print(f'An error occurred when resetting videos')
    