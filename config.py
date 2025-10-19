class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://flaskuser:flask123@localhost/student_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secretkey1234'
