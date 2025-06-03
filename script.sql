CREATE TABLE teacher (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL
);

CREATE TABLE subject (
    name VARCHAR(100) PRIMARY KEY
);

CREATE TABLE timetable (
    id SERIAL PRIMARY KEY,
    day VARCHAR(20) NOT NULL,
    subject VARCHAR(100) NOT NULL REFERENCES subject(name),
    room_numb VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    week_type VARCHAR(10) CHECK (week_type IN ('upper', 'lower', 'both')),
    teacher_id INTEGER REFERENCES teacher(id)
);
