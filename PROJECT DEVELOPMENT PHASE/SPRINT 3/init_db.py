from mysql.connector import Error, connect

with open('secret.txt', 'r') as f:
    line = f.readline().split(',')
    user = line[0]
    password = line[1]
        
try:
    # create connection
    connection = connect(user=user, password=password, host='localhost')
    print(connection)

    # delete existing database
    delete_db_query = "DROP DATABASE flights"
    with connection.cursor() as cursor:
        cursor.execute(delete_db_query)

    # create new database
    create_db_query = "CREATE DATABASE flights"
    with connection.cursor() as cursor:
        cursor.execute(create_db_query)

    # show databases
    show_db_query = "SHOW DATABASES"
    with connection.cursor() as cursor:
        cursor.execute(show_db_query)
        for db in cursor:
            print(db)
    
    # select database
    select_db_query = "USE flights"
    with connection.cursor() as cursor:
        cursor.execute(select_db_query)
    
        # creating table
        create_table_query = """
        create table if not exists `accounts` (
        `id` int(11) not null auto_increment,
        `name` varchar(50) not null,
        `password` varchar(10) not null,
        `email` varchar(100) not null,
        primary key (`id`)
        ) engine=InnoDB auto_increment=2 default charset=utf8;
        """
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            print("Table created!")
            connection.commit()
    
    # show table
    select_table_query = "DESCRIBE accounts"
    with connection.cursor() as cursor:
        cursor.execute(select_table_query)
        for line in cursor:
            print(line)

    # view table
    select_table_query = "SELECT * FROM accounts"
    with connection.cursor() as cursor:
        cursor.execute(select_table_query)
        for line in cursor:
            print(line)
    
except Error as e:
    print(e)

