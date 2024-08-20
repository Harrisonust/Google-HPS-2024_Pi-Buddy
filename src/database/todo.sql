-- DROP TABLE IF EXISTS todo;

-- CREATE TABLE todo (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     task_name TEXT NOT NULL,
--     due_date DATE,
--     priority INTEGER,
--     is_active INTEGER DEFAULT 0,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME
-- );

-- INSERT INTO todo (task_name, due_date, priority, is_active)
-- VALUES ('Complete Raspberry Pi project', '2024-08-25', 1, 1);

-- INSERT INTO todo (task_name, priority, is_active)
-- VALUES ('Prepare for Databricks interview', 2, 1);

-- INSERT INTO todo (task_name, due_date, priority, is_active)
-- VALUES ('Read up on threading in Python', '2024-09-01', 3, 0);

-- INSERT INTO todo (task_name, due_date, is_active)
-- VALUES ('Submit assignment for UC San Diego', '2024-08-20', 1);



UPDATE todo
SET is_active = 1;


SELECT * FROM todo;