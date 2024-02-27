CREATE TABLE workout (
    workout_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    date DATE,
    distance DECIMAL(5, 2) DEFAULT 0.0,
    workout_time TIME DEFAULT '00:00:00',
    today_weight DECIMAL(5, 2) DEFAULT 0.0
    FOREIGN KEY (member_id) REFERENCES profile(member_id)
);

CREATE TABLE profile (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10),
    age INT,
    height DECIMAL(5, 2),
    init_weight DECIMAL(5, 2),
	NOK INT
);